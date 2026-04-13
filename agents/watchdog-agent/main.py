"""X Image Watchdog Agent — Provenance Verification & Training Data Licensing.

Monitors artist X accounts for new image posts. When a drop is detected:
1. Downloads the image from X
2. Pays $0.02 to Aegis via x402 for C2PA + hash verification
3. Reads training terms from Golden Codex metadata
4. If licensed for training → pays $0.10 to the artist's wallet
5. All settlements on Kite chain via Pieverse facilitator
6. Streams events to Firestore for real-time dashboard

Artist accounts monitored:
  - @artiswagallery (Artiswa Creatio)
  - @0x_b1ank (0x_b1ank)
  - @Golden_Codex (Golden Codex)
"""

import os
import io
import json
import time
import logging
import hashlib
import requests
import tweepy
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from google.cloud import firestore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GCP_PROJECT = os.environ.get("GCP_PROJECT", "the-golden-codex-1111")
FIRESTORE_DB = os.environ.get("FIRESTORE_DB", "golden-codex-database")
WATCHDOG_AGENT_ID = os.environ.get("WATCHDOG_AGENT_ID", "watchdog-agent-01")

# X API credentials (OAuth 1.0a — shared consumer key, per-account access tokens)
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")
X_CONSUMER_KEY = os.environ.get("X_CONSUMER_KEY", "")
X_CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")

# Artist accounts to monitor
MONITORED_ACCOUNTS = {
    "artiswagallery": {
        "display_name": "Artiswa Creatio",
        "artist_wallet": os.environ.get("ARTISWA_WALLET", ""),
        "user_id": os.environ.get("ARTISWA_USER_ID", ""),
    },
    "0x_b1ank": {
        "display_name": "0x_b1ank",
        "artist_wallet": os.environ.get("B1ANK_WALLET", ""),
        "user_id": os.environ.get("B1ANK_USER_ID", ""),
    },
    "Golden_Codex": {
        "display_name": "Golden Codex",
        "artist_wallet": os.environ.get("GOLDEN_CODEX_WALLET", ""),
        "user_id": os.environ.get("GOLDEN_CODEX_USER_ID", ""),
    },
}

# Aegis verification endpoint
AEGIS_URL = os.environ.get("AEGIS_URL", "https://aegis-agent-172867820131.us-west1.run.app")

# x402 payment — chain-agnostic (Base L2 default, Kite when ready)
try:
    from x402_settlement import settle_payment as x402_settle, get_settlement_info
except ImportError:
    x402_settle = None
    get_settlement_info = None
WATCHDOG_VAULT_ADDRESS = os.environ.get("WATCHDOG_VAULT_ADDRESS", "")

# Fee structure — Metavolve earns on every transaction
METAVOLVE_WALLET = os.environ.get("METAVOLVE_WALLET", "0xFE141943a93c184606F3060103D975662327063B")
VERIFICATION_FEE = 0.02       # $0.02 → Metavolve (every query, match or not)
LICENSE_TOTAL = 1.00           # $1.00 total license cost
TRANSACTION_FEE_PCT = 0.05    # 5% → Metavolve
ARTIST_SHARE = LICENSE_TOTAL * (1 - TRANSACTION_FEE_PCT)  # $0.95 → Artist
PLATFORM_FEE = LICENSE_TOTAL * TRANSACTION_FEE_PCT          # $0.05 → Metavolve

# Polling interval (seconds)
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("watchdog")

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Firestore client (lazy init)
_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project=GCP_PROJECT, database=FIRESTORE_DB)
    return _db


# ---------------------------------------------------------------------------
# X API Client
# ---------------------------------------------------------------------------

def get_x_client():
    """Create a tweepy Client with bearer token for read-only access."""
    if X_BEARER_TOKEN:
        return tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)
    return None


def fetch_recent_tweets_with_images(username, user_id, since_id=None):
    """Fetch recent tweets containing images from a specific user.

    Returns list of dicts: {tweet_id, text, image_url, created_at}
    """
    client = get_x_client()
    if not client:
        logger.warning("No X API bearer token configured")
        return []

    try:
        kwargs = {
            "id": user_id,
            "max_results": 10,
            "tweet_fields": ["created_at", "attachments", "entities"],
            "media_fields": ["url", "preview_image_url", "type"],
            "expansions": ["attachments.media_keys"],
        }
        if since_id:
            kwargs["since_id"] = since_id

        response = client.get_users_tweets(**kwargs)

        if not response.data:
            return []

        # Build media lookup
        media_map = {}
        if response.includes and "media" in response.includes:
            for media in response.includes["media"]:
                if media.type == "photo" and media.url:
                    media_map[media.media_key] = media.url

        results = []
        for tweet in response.data:
            if not tweet.attachments:
                continue
            media_keys = tweet.attachments.get("media_keys", [])
            for key in media_keys:
                if key in media_map:
                    results.append({
                        "tweet_id": str(tweet.id),
                        "text": tweet.text or "",
                        "image_url": media_map[key],
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else datetime.now(timezone.utc).isoformat(),
                        "username": username,
                    })
        return results

    except tweepy.TooManyRequests:
        logger.warning(f"Rate limited on @{username}, will retry next cycle")
        return []
    except Exception as e:
        logger.error(f"Error fetching tweets for @{username}: {e}")
        return []


def download_image(image_url):
    """Download an image from URL, return bytes."""
    try:
        resp = requests.get(image_url, timeout=30)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        logger.error(f"Failed to download image: {e}")
        return None


# ---------------------------------------------------------------------------
# Aegis Verification
# ---------------------------------------------------------------------------

def verify_with_aegis(image_bytes, filename="tweet_image.jpg"):
    """Send image to Aegis for C2PA + hash verification.

    Returns dict with verification results.
    """
    try:
        files = {"image": (filename, io.BytesIO(image_bytes), "image/jpeg")}
        resp = requests.post(
            f"{AEGIS_URL}/aegis/verify",
            files=files,
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            golden_codex = data.get("golden_codex") or data.get("metadata") or {}
            identity = data.get("identity", {})
            return {
                "verified": data.get("verified", True),
                "gcx_registered": data.get("verified", False),
                "c2pa_valid": data.get("c2pa_valid", False),
                "artwork_id": identity.get("gcx_id") or data.get("artwork_id"),
                "confidence": data.get("similarity") or data.get("confidence"),
                "metadata": golden_codex,
                "arweave_uri": (data.get("arweave", {}) or {}).get("image_uri"),
                "training_terms": extract_training_terms(golden_codex),
                "artist_wallet": extract_artist_wallet(golden_codex),
            }
        else:
            return {"verified": False, "error": f"Aegis returned {resp.status_code}"}
    except Exception as e:
        logger.error(f"Aegis verification failed: {e}")
        return {"verified": False, "error": str(e)}


def extract_training_terms(metadata):
    """Extract AI training licensing terms from Golden Codex metadata.

    Checks Aegis-normalized flat fields first, then canonical nested
    schema paths (v1.5-SOULPRINT).
    """
    if not metadata or not isinstance(metadata, dict):
        return None

    # Aegis-normalized flat field (preferred)
    if metadata.get("training_terms"):
        return metadata.get("training_terms")

    # Nested: training_data_rights object (v1.5 schema)
    tdr = metadata.get("trainingDataRights") or metadata.get("training_data_rights")
    if isinstance(tdr, dict):
        return tdr.get("usage_terms") or tdr

    return None


def extract_artist_wallet(metadata):
    """Extract artist payment wallet from Golden Codex metadata.

    Checks Aegis-normalized flat field first, then canonical nested
    schema paths: revenue_split.artist_wallet (v1.5 template) and
    treasury_wallet.address (v1.5 soulprint batch).
    """
    if not metadata or not isinstance(metadata, dict):
        return None

    # Aegis-normalized flat field (preferred — set by normalize_golden_codex)
    if metadata.get("artist_wallet"):
        return metadata["artist_wallet"]

    # Canonical nested: v1.5 schema template path
    tdr = metadata.get("trainingDataRights") or metadata.get("training_data_rights")
    if isinstance(tdr, dict):
        # Path A: revenue_split.artist_wallet (schema template)
        wallet = tdr.get("revenue_split", {}).get("artist_wallet")
        if wallet:
            return wallet
        # Path B: treasury_wallet.address (soulprint batch)
        wallet = tdr.get("treasury_wallet", {}).get("address")
        if wallet:
            return wallet

    return None


# ---------------------------------------------------------------------------
# x402 Payment — Chain-Agnostic (Base L2 or Kite)
# ---------------------------------------------------------------------------

def settle_payment_on_kite(to_address, amount_usd, service_description, job_id):
    """Settle x402 payment via chain-agnostic facilitator.

    Uses Base L2 (Coinbase CDP) by default. Set X402_NETWORK=kite to use
    Kite Pieverse facilitator when testnet tokens are available.
    """
    if x402_settle:
        return x402_settle(
            from_address=WATCHDOG_VAULT_ADDRESS,
            to_address=to_address,
            amount_usd=amount_usd,
            service=service_description,
            job_id=job_id,
        )
    # Fallback if shared module not available
    return {
        "from": WATCHDOG_VAULT_ADDRESS or WATCHDOG_AGENT_ID,
        "to": to_address,
        "amount_usd": amount_usd,
        "service": service_description,
        "job_id": job_id,
        "chain": "base-mainnet",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "simulated",
        "tx_hash": "0x" + hashlib.sha256(
            f"{job_id}-{amount_usd}-{time.time()}".encode()
        ).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Core Pipeline: Process a single image drop
# ---------------------------------------------------------------------------

def process_image_drop(tweet_data, account_info):
    """Full pipeline for a detected image drop.

    1. Download image
    2. Pay Aegis for verification ($0.02)
    3. Check C2PA + GCX registration
    4. Read training terms
    5. If licensed → pay artist ($0.10)
    6. Record everything to Firestore
    """
    db = get_db()
    job_id = f"wd-{tweet_data['tweet_id']}-{int(time.time())}"

    # Create event document
    event = {
        "job_id": job_id,
        "agent_id": WATCHDOG_AGENT_ID,
        "tweet_id": tweet_data["tweet_id"],
        "tweet_text": tweet_data["text"][:280],
        "image_url": tweet_data["image_url"],
        "username": tweet_data["username"],
        "artist_display_name": account_info["display_name"],
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "status": "detected",
        "steps": [],
        "payments": [],
    }

    # Write initial event to Firestore (dashboard picks this up immediately)
    event_ref = db.collection("watchdog_events").document(job_id)
    event_ref.set(event)

    def add_step(step_name, status, details=None):
        step = {
            "name": step_name,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }
        event["steps"].append(step)
        event_ref.update({"steps": event["steps"], "status": step_name})
        logger.info(f"[{job_id}] {step_name}: {status}")

    # Step 1: Download image
    add_step("image_download", "in_progress")
    image_bytes = download_image(tweet_data["image_url"])
    if not image_bytes:
        add_step("image_download", "failed", {"error": "Download failed"})
        event_ref.update({"status": "failed"})
        return event

    image_hash = hashlib.sha256(image_bytes).hexdigest()
    add_step("image_download", "complete", {
        "size_bytes": len(image_bytes),
        "sha256": image_hash[:16] + "...",
    })

    # Step 2: Pay verification fee → Metavolve (charged regardless of result)
    add_step("verification_fee", "in_progress")
    verification_payment = settle_payment_on_kite(
        to_address=METAVOLVE_WALLET,
        amount_usd=VERIFICATION_FEE,
        service_description="gcx_verification_fee",
        job_id=job_id,
    )
    event["payments"].append(verification_payment)
    event_ref.update({"payments": event["payments"]})
    add_step("verification_fee", verification_payment["status"], {
        "amount": f"${VERIFICATION_FEE}",
        "to": "Metavolve Labs",
        "tx_hash": verification_payment.get("tx_hash"),
    })

    # Step 3: Verify with Aegis
    add_step("aegis_verification", "in_progress")
    verification = verify_with_aegis(image_bytes)
    add_step("aegis_verification", "complete", {
        "c2pa_valid": verification.get("c2pa_valid", False),
        "gcx_registered": verification.get("gcx_registered", False),
        "artwork_id": verification.get("artwork_id"),
        "confidence": verification.get("confidence"),
        "training_terms": verification.get("training_terms"),
    })

    event["verification"] = verification
    event_ref.update({"verification": verification})

    # Step 4: Evaluate training data licensing
    c2pa_valid = verification.get("c2pa_valid", False)
    gcx_registered = verification.get("gcx_registered", False)
    training_terms = verification.get("training_terms")
    artist_wallet = (
        verification.get("artist_wallet")
        or account_info.get("artist_wallet")
        or ""
    )

    add_step("license_evaluation", "complete", {
        "c2pa": c2pa_valid,
        "gcx": gcx_registered,
        "training_licensed": training_terms is not None,
        "artist_wallet_found": bool(artist_wallet),
    })

    # Step 5: If training-licensed → pay artist ($0.95) + platform fee ($0.05)
    if gcx_registered and training_terms and artist_wallet:
        # Payment A: Artist share
        add_step("artist_payment", "in_progress")
        artist_payment = settle_payment_on_kite(
            to_address=artist_wallet,
            amount_usd=ARTIST_SHARE,
            service_description="training_data_license_artist_share",
            job_id=job_id,
        )
        event["payments"].append(artist_payment)
        add_step("artist_payment", artist_payment["status"], {
            "amount": f"${ARTIST_SHARE:.2f}",
            "to": artist_wallet[:10] + "...",
            "tx_hash": artist_payment.get("tx_hash"),
        })

        # Payment B: Platform transaction fee → Metavolve
        add_step("platform_fee", "in_progress")
        platform_payment = settle_payment_on_kite(
            to_address=METAVOLVE_WALLET,
            amount_usd=PLATFORM_FEE,
            service_description="transaction_fee_5pct",
            job_id=job_id,
        )
        event["payments"].append(platform_payment)
        event_ref.update({"payments": event["payments"]})
        add_step("platform_fee", platform_payment["status"], {
            "amount": f"${PLATFORM_FEE:.2f}",
            "to": "Metavolve Labs (5% tx fee)",
            "tx_hash": platform_payment.get("tx_hash"),
        })
        event["license_acquired"] = True
    else:
        reasons = []
        if not gcx_registered:
            reasons.append("not GCX registered")
        if not training_terms:
            reasons.append("no training terms in metadata")
        if not artist_wallet:
            reasons.append("no artist wallet found")
        add_step("license_evaluation", "skipped", {"reasons": reasons})
        event["license_acquired"] = False

    # Final status
    event["status"] = "complete"
    event["completed_at"] = datetime.now(timezone.utc).isoformat()
    total_paid = sum(p.get("amount_usd", 0) for p in event["payments"])
    event["total_paid_usd"] = total_paid
    event_ref.update({
        "status": "complete",
        "completed_at": event["completed_at"],
        "total_paid_usd": total_paid,
        "license_acquired": event.get("license_acquired", False),
    })

    logger.info(f"[{job_id}] Complete. C2PA={c2pa_valid} GCX={gcx_registered} Licensed={event.get('license_acquired')} Paid=${total_paid:.3f}")
    return event


# ---------------------------------------------------------------------------
# Polling Loop
# ---------------------------------------------------------------------------

# Track the last seen tweet ID per account (in-memory, persisted to Firestore)
_last_seen = {}

def load_last_seen():
    """Load last-seen tweet IDs from Firestore."""
    global _last_seen
    try:
        db = get_db()
        doc = db.collection("watchdog_state").document("last_seen").get()
        if doc.exists:
            _last_seen = doc.to_dict()
            logger.info(f"Loaded last_seen state: {_last_seen}")
    except Exception as e:
        logger.warning(f"Could not load last_seen: {e}")

def save_last_seen():
    """Persist last-seen tweet IDs to Firestore."""
    try:
        db = get_db()
        db.collection("watchdog_state").document("last_seen").set(_last_seen)
    except Exception as e:
        logger.warning(f"Could not save last_seen: {e}")


def poll_once():
    """Run one polling cycle across all monitored accounts."""
    results = []
    for username, account_info in MONITORED_ACCOUNTS.items():
        user_id = account_info.get("user_id")
        if not user_id:
            continue

        since_id = _last_seen.get(username)
        tweets = fetch_recent_tweets_with_images(username, user_id, since_id)

        if tweets:
            # Update last seen
            max_id = max(t["tweet_id"] for t in tweets)
            _last_seen[username] = max_id
            save_last_seen()

            for tweet in tweets:
                logger.info(f"New image drop from @{username}: tweet {tweet['tweet_id']}")
                result = process_image_drop(tweet, account_info)
                results.append(result)

    return results


# ---------------------------------------------------------------------------
# Flask Endpoints
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "agent": WATCHDOG_AGENT_ID,
        "monitored_accounts": list(MONITORED_ACCOUNTS.keys()),
        "poll_interval": POLL_INTERVAL,
        "vault_configured": bool(WATCHDOG_VAULT_ADDRESS),
    })


@app.route("/poll", methods=["POST"])
def trigger_poll():
    """Manually trigger a polling cycle. Called by Cloud Scheduler or manually."""
    results = poll_once()
    return jsonify({
        "polled_accounts": list(MONITORED_ACCOUNTS.keys()),
        "new_drops": len(results),
        "results": [
            {
                "job_id": r.get("job_id"),
                "username": r.get("username"),
                "status": r.get("status"),
                "license_acquired": r.get("license_acquired"),
                "total_paid_usd": r.get("total_paid_usd"),
            }
            for r in results
        ],
    })


@app.route("/demo", methods=["POST"])
def demo_drop():
    """Simulate a drop for demo/testing without X API.

    POST body: { "image_url": "...", "username": "artiswagallery", "tweet_text": "..." }
    Or: multipart with "image" file field
    """
    if request.content_type and "multipart" in request.content_type:
        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image file provided"}), 400
        image_bytes = file.read()
        username = request.form.get("username", "artiswagallery")
        tweet_text = request.form.get("tweet_text", "Demo drop")
        image_url = "local://upload"
    else:
        data = request.get_json() or {}
        username = data.get("username", "artiswagallery")
        tweet_text = data.get("tweet_text", "Demo drop")
        image_url = data.get("image_url", "")
        image_bytes = None

    account_info = MONITORED_ACCOUNTS.get(username, {
        "display_name": username,
        "artist_wallet": "",
    })

    tweet_data = {
        "tweet_id": f"demo-{int(time.time())}",
        "text": tweet_text,
        "image_url": image_url,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "username": username,
    }

    # If image provided directly, temporarily override download
    if image_bytes:
        # Monkey-patch for demo: skip download, use provided bytes
        original_download = globals().get("download_image")

        def mock_download(url):
            return image_bytes

        import types
        import sys
        current_module = sys.modules[__name__]
        setattr(current_module, "download_image", mock_download)

        result = process_image_drop(tweet_data, account_info)

        # Restore
        setattr(current_module, "download_image", original_download)
    else:
        result = process_image_drop(tweet_data, account_info)

    return jsonify(result)


@app.route("/events", methods=["GET"])
def get_events():
    """Get recent watchdog events for the dashboard."""
    db = get_db()
    limit = int(request.args.get("limit", 20))

    docs = (
        db.collection("watchdog_events")
        .order_by("detected_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    events = []
    for doc in docs:
        events.append(doc.to_dict())

    return jsonify({"events": events, "count": len(events)})


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get aggregate stats for the dashboard."""
    db = get_db()
    events = db.collection("watchdog_events").stream()

    total_events = 0
    total_licensed = 0
    total_paid = 0.0
    total_payments = 0

    for doc in events:
        data = doc.to_dict()
        total_events += 1
        if data.get("license_acquired"):
            total_licensed += 1
        total_paid += data.get("total_paid_usd", 0)
        total_payments += len(data.get("payments", []))

    return jsonify({
        "total_drops_detected": total_events,
        "total_licenses_acquired": total_licensed,
        "total_usd_settled": round(total_paid, 4),
        "total_payments": total_payments,
        "monitored_accounts": list(MONITORED_ACCOUNTS.keys()),
    })


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    load_last_seen()
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
