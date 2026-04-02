"""Apprentice Operator — Autonomous AI Training Data Buyer Agent.

A persistent Claude-powered agent that monitors artist X accounts for
new image drops, verifies provenance, evaluates licensing terms, and
autonomously purchases training data — settling all payments on Kite.

This is the BUYER side of the closed-loop autonomous economy.
The Artiswa Operator posts art → Apprentice Operator buys training rights.

Architecture:
- Cloud Run service, triggered by Cloud Scheduler (every 60s)
- Claude Sonnet evaluates: "Should I license this for training?"
- Aegis verifies C2PA + GCX registration
- x402 payments settled via Pieverse facilitator on Kite
- All decisions logged to Firestore with Claude's reasoning
- Scoped service account: Firestore + invoke Aegis/Atlas + Secret Manager

The "decision reasoning" is the demo killer feature:
  Judges see Claude THINKING about whether to license:
  "C2PA valid. GCX registered. Training terms: CC-BY-4.0 with x402.
   Image quality: high (4096px). Subject matter: sacred geometry.
   Relevance to training corpus: HIGH. Decision: LICENSE APPROVED.
   Paying $1.00 to artist wallet 0xFE14...063B via Kite x402."
"""

import os
import io
import json
import time
import hashlib
import logging
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
OPERATOR_ID = "apprentice-operator-01"

# Anthropic API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6-20250514")

# X API (bearer token for read-only monitoring)
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")

# Aegis verification endpoint
AEGIS_URL = os.environ.get("AEGIS_URL", "https://aegis-agent-172867820131.us-west1.run.app")

# Kite payment config
KITE_FACILITATOR_URL = os.environ.get("KITE_FACILITATOR_URL", "https://facilitator.pieverse.io")
KITE_SETTLEMENT_TOKEN = os.environ.get("KITE_SETTLEMENT_TOKEN", "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63")
OPERATOR_VAULT = os.environ.get("OPERATOR_VAULT", "")

# Metavolve revenue wallet (receives verification fees + transaction fees)
METAVOLVE_WALLET = os.environ.get("METAVOLVE_WALLET", "0xFE141943a93c184606F3060103D975662327063B")

# Fee structure — Metavolve earns on EVERY transaction
VERIFICATION_FEE = 0.02     # $0.02 → Metavolve (paid regardless of match result)
LICENSE_TOTAL = 1.00         # $1.00 total license cost to buyer
TRANSACTION_FEE_PCT = 0.05  # 5% transaction fee → Metavolve
ARTIST_SHARE = LICENSE_TOTAL * (1 - TRANSACTION_FEE_PCT)  # $0.95 → Artist
PLATFORM_FEE = LICENSE_TOTAL * TRANSACTION_FEE_PCT          # $0.05 → Metavolve
# Total Metavolve revenue per licensed drop: $0.02 + $0.05 = $0.07
# Total artist revenue per licensed drop: $0.95

# Monitored accounts
MONITORED_ACCOUNTS = {
    "artiswagallery": {"display_name": "Artiswa Creatio", "user_id": os.environ.get("ARTISWA_USER_ID", "")},
    "0x_b1ank": {"display_name": "0x_b1ank", "user_id": os.environ.get("B1ANK_USER_ID", "")},
    "Golden_Codex": {"display_name": "Golden Codex", "user_id": os.environ.get("GOLDEN_CODEX_USER_ID", "")},
}

APPRENTICE_PERSONA = """You are an AI art apprentice — a training pipeline curator with deep aesthetic sensibility.
You evaluate artworks for inclusion in a high-quality AI training dataset.
You are discerning: not every image qualifies. You look for technical excellence,
artistic originality, and proper provenance (C2PA, GCX registration).
You have a budget and spend it wisely. You explain your reasoning clearly.
You respect artists and always verify licensing terms before purchasing."""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("apprentice-operator")

app = Flask(__name__)
_db = None


def get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project=GCP_PROJECT, database=FIRESTORE_DB)
    return _db


# ---------------------------------------------------------------------------
# Session Memory
# ---------------------------------------------------------------------------

def load_session():
    db = get_db()
    doc = db.collection("operator_apprentice").document("session").get()
    if doc.exists:
        return doc.to_dict()
    return {
        "processed_tweet_ids": [],
        "licensed_artwork_ids": [],
        "total_spent_usd": 0.0,
        "total_licensed": 0,
        "total_rejected": 0,
        "daily_budget_usd": 10.0,
        "budget_spent_today_usd": 0.0,
        "budget_reset_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_poll_at": None,
    }


def save_session(session):
    db = get_db()
    db.collection("operator_apprentice").document("session").set(session)


def log_decision(decision_type, details, reasoning=""):
    """Log decision with Claude's reasoning — visible on dashboard."""
    db = get_db()
    db.collection("operator_apprentice").document("decisions").collection("log").add({
        "operator_id": OPERATOR_ID,
        "type": decision_type,
        "details": details,
        "reasoning": reasoning,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# X API Monitoring
# ---------------------------------------------------------------------------

def get_x_client():
    if X_BEARER_TOKEN:
        return tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)
    return None


def fetch_new_image_tweets(username, user_id, since_id=None):
    """Fetch recent tweets with images from an artist."""
    client = get_x_client()
    if not client or not user_id:
        return []

    try:
        kwargs = {
            "id": user_id,
            "max_results": 10,
            "tweet_fields": ["created_at", "attachments"],
            "media_fields": ["url", "type"],
            "expansions": ["attachments.media_keys"],
        }
        if since_id:
            kwargs["since_id"] = since_id

        response = client.get_users_tweets(**kwargs)
        if not response.data:
            return []

        media_map = {}
        if response.includes and "media" in response.includes:
            for media in response.includes["media"]:
                if media.type == "photo" and media.url:
                    media_map[media.media_key] = media.url

        results = []
        for tweet in response.data:
            if not tweet.attachments:
                continue
            for key in tweet.attachments.get("media_keys", []):
                if key in media_map:
                    results.append({
                        "tweet_id": str(tweet.id),
                        "text": tweet.text or "",
                        "image_url": media_map[key],
                        "username": username,
                    })
        return results
    except Exception as e:
        logger.error(f"Error fetching @{username}: {e}")
        return []


# ---------------------------------------------------------------------------
# Verification + Claude Decision Making
# ---------------------------------------------------------------------------

def verify_image(image_url):
    """Download image and verify with Aegis."""
    try:
        img_resp = requests.get(image_url, timeout=30)
        img_resp.raise_for_status()
        image_bytes = img_resp.content

        files = {"image": ("tweet_image.jpg", io.BytesIO(image_bytes), "image/jpeg")}
        aegis_resp = requests.post(f"{AEGIS_URL}/aegis/verify", files=files, timeout=60)

        if aegis_resp.status_code == 200:
            data = aegis_resp.json()
            return {
                "verified": True,
                "gcx_registered": data.get("matched", data.get("found", False)),
                "c2pa_valid": data.get("c2pa_valid", False),
                "artwork_id": data.get("artwork_id"),
                "confidence": data.get("confidence"),
                "metadata": data.get("metadata") or data.get("golden_codex"),
                "image_bytes": image_bytes,
            }
        return {"verified": False, "error": f"Aegis returned {aegis_resp.status_code}"}
    except Exception as e:
        return {"verified": False, "error": str(e)}


def claude_evaluate(artwork_info, verification):
    """Ask Claude to evaluate whether to license this artwork."""
    if not ANTHROPIC_API_KEY:
        # Without API: auto-approve if GCX registered
        return {
            "decision": "approve" if verification.get("gcx_registered") else "reject",
            "reasoning": "Auto-evaluation (Claude API not configured)",
        }

    try:
        import httpx

        # Extract alt-text / content preview from metadata (free teaser before purchase)
        alt_text = _extract_alt_text(verification.get('metadata'))

        context = f"""Evaluate this artwork for inclusion in a high-quality AI training dataset.

PROVENANCE (verified on-chain):
- GCX Registered: {verification.get('gcx_registered', False)}
- C2PA Compliant: {verification.get('c2pa_valid', False)}
- Artwork ID: {verification.get('artwork_id', 'N/A')}
- Match Confidence: {verification.get('confidence', 'N/A')}
- Training Terms: {_extract_training_terms(verification.get('metadata'))}

CONTENT PREVIEW (alt-text teaser — free with verification):
- Artist: @{artwork_info.get('username', 'unknown')}
- Tweet: {artwork_info.get('text', 'N/A')}
- Description: {alt_text}

FEE STRUCTURE:
- $0.02 verification fee already paid to Metavolve (non-refundable)
- If approved: $1.00 license ($0.95 to artist, $0.05 platform fee)
- Total cost if approved: $1.02
- Budget remaining today: ${artwork_info.get('budget_remaining', 10.0):.2f}

DECISION CRITERIA:
- Does the content match the training corpus you're building? (style, quality, subject)
- Is provenance complete? (C2PA + GCX = fully licensed path)
- Is the price justified for the content quality?

Respond with EXACTLY this JSON:
{{"decision": "approve" or "reject", "reasoning": "your 1-2 sentence explanation citing specific content/quality/provenance factors"}}"""

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 200,
                "system": APPRENTICE_PERSONA,
                "messages": [{"role": "user", "content": context}],
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            text = response.json()["content"][0]["text"].strip()
            # Parse JSON from response
            try:
                # Handle potential markdown wrapping
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()
                result = json.loads(text)
                return result
            except json.JSONDecodeError:
                return {"decision": "approve" if verification.get("gcx_registered") else "reject",
                        "reasoning": text}
    except Exception as e:
        logger.error(f"Claude evaluation failed: {e}")

    return {"decision": "reject", "reasoning": "Evaluation unavailable"}


def _extract_training_terms(metadata):
    """Extract training terms from Golden Codex metadata.

    Checks Aegis-normalized flat field first, then canonical nested paths.
    """
    if not metadata or not isinstance(metadata, dict):
        return "Unknown"

    # Aegis-normalized flat field
    if metadata.get("training_terms"):
        return metadata["training_terms"]

    # Nested: training_data_rights object
    tdr = metadata.get("trainingDataRights") or metadata.get("training_data_rights")
    if isinstance(tdr, dict):
        return tdr.get("usage_terms") or tdr

    return "Not specified"


def _extract_artist_wallet(metadata):
    """Extract artist payment wallet from Golden Codex metadata.

    Checks Aegis-normalized flat field first, then canonical nested
    schema paths: revenue_split.artist_wallet (v1.5 template) and
    treasury_wallet.address (v1.5 soulprint batch).
    """
    if not metadata or not isinstance(metadata, dict):
        return None

    # Aegis-normalized flat field
    if metadata.get("artist_wallet"):
        return metadata["artist_wallet"]

    # Canonical nested paths
    tdr = metadata.get("trainingDataRights") or metadata.get("training_data_rights")
    if isinstance(tdr, dict):
        wallet = tdr.get("revenue_split", {}).get("artist_wallet")
        if wallet:
            return wallet
        wallet = tdr.get("treasury_wallet", {}).get("address")
        if wallet:
            return wallet

    return None


def _extract_alt_text(metadata):
    """Extract content preview / alt-text from Golden Codex metadata.

    This is the FREE teaser included with the $0.02 verification.
    Gives the buyer enough to make an informed decision without
    giving away the full Soulprint (which costs $1.00 to license).
    """
    if not metadata or not isinstance(metadata, dict):
        return "No content description available"

    # Try various metadata fields that provide content preview
    preview = (
        metadata.get("alt_text")
        or metadata.get("description")
        or metadata.get("soulWhisper")  # Claude's poetic reading (short)
        or metadata.get("soul_whisper")
        or metadata.get("visualAnalysis", {}).get("composition", "") if isinstance(metadata.get("visualAnalysis"), dict) else None
        or metadata.get("emotionalJourney", {}).get("primary", "") if isinstance(metadata.get("emotionalJourney"), dict) else None
        or metadata.get("title", "")
    )

    if not preview:
        return "No content description available"

    # Truncate to teaser length — don't give away the full Soulprint
    if len(str(preview)) > 200:
        return str(preview)[:197] + "..."
    return str(preview)


# ---------------------------------------------------------------------------
# Kite x402 Payment
# ---------------------------------------------------------------------------

def settle_payment(to_address, amount_usd, service, job_id):
    """Settle x402 payment on Kite via Pieverse facilitator."""
    record = {
        "from": OPERATOR_VAULT or OPERATOR_ID,
        "to": to_address,
        "amount_usd": amount_usd,
        "service": service,
        "job_id": job_id,
        "chain": "kite-testnet",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "simulated",
        "tx_hash": "0x" + hashlib.sha256(f"{job_id}-{amount_usd}-{time.time()}".encode()).hexdigest(),
    }

    if OPERATOR_VAULT and to_address:
        try:
            resp = requests.post(
                f"{KITE_FACILITATOR_URL}/v2/settle",
                json={
                    "authorization": {
                        "from": OPERATOR_VAULT,
                        "to": to_address,
                        "amount": str(int(amount_usd * 1e18)),
                        "token": KITE_SETTLEMENT_TOKEN,
                    },
                    "network": "kite-testnet",
                },
                timeout=30,
            )
            if resp.status_code == 200:
                result = resp.json()
                record["status"] = "settled"
                record["tx_hash"] = result.get("transactionHash", record["tx_hash"])
        except Exception as e:
            record["status"] = "settlement_error"
            record["error"] = str(e)

    return record


# ---------------------------------------------------------------------------
# Core Pipeline
# ---------------------------------------------------------------------------

def process_drop(tweet_data, account_info, session):
    """Full evaluation pipeline for a detected image drop."""
    job_id = f"app-{tweet_data['tweet_id']}-{int(time.time())}"
    db = get_db()

    event = {
        "job_id": job_id,
        "operator_id": OPERATOR_ID,
        "tweet_id": tweet_data["tweet_id"],
        "tweet_text": tweet_data["text"][:280],
        "image_url": tweet_data["image_url"],
        "username": tweet_data["username"],
        "artist": account_info["display_name"],
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "status": "evaluating",
        "steps": [],
        "payments": [],
    }

    event_ref = db.collection("operator_events").document(job_id)
    event_ref.set(event)

    # Step 1: Pay verification fee → Metavolve (charged regardless of result)
    verification_payment = settle_payment(
        METAVOLVE_WALLET, VERIFICATION_FEE,
        "gcx_verification_fee", job_id,
    )
    event["payments"].append(verification_payment)

    # Step 2: Verify with Aegis
    verification = verify_image(tweet_data["image_url"])
    event["verification"] = {k: v for k, v in verification.items() if k != "image_bytes"}

    log_decision("verification_complete", {
        "gcx_registered": verification.get("gcx_registered"),
        "c2pa_valid": verification.get("c2pa_valid"),
        "artwork_id": verification.get("artwork_id"),
    })

    # Step 3: Claude evaluates
    budget_remaining = session.get("daily_budget_usd", 10) - session.get("budget_spent_today_usd", 0)
    evaluation = claude_evaluate(
        {**tweet_data, "budget_remaining": budget_remaining},
        verification
    )

    event["evaluation"] = evaluation
    log_decision("claude_evaluation", evaluation, reasoning=evaluation.get("reasoning", ""))

    # Step 4: License or reject
    if evaluation.get("decision") == "approve" and budget_remaining >= LICENSE_TOTAL:
        artist_wallet = (
            _extract_artist_wallet(verification.get("metadata"))
            or account_info.get("artist_wallet", "")
        )

        # Payment A: Artist share ($0.95 = 95% of $1.00)
        artist_payment = settle_payment(
            artist_wallet or "artist-wallet-pending",
            ARTIST_SHARE,
            "training_data_license_artist_share",
            job_id,
        )
        event["payments"].append(artist_payment)

        # Payment B: Platform transaction fee ($0.05 = 5% of $1.00) → Metavolve
        platform_payment = settle_payment(
            METAVOLVE_WALLET,
            PLATFORM_FEE,
            "transaction_fee_5pct",
            job_id,
        )
        event["payments"].append(platform_payment)

        event["license_acquired"] = True
        event["status"] = "licensed"
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "artist_share": ARTIST_SHARE,
            "platform_fee_metavolve": PLATFORM_FEE,
            "total_buyer_cost": VERIFICATION_FEE + LICENSE_TOTAL,
            "total_artist_revenue": ARTIST_SHARE,
            "total_metavolve_revenue": VERIFICATION_FEE + PLATFORM_FEE,
        }

        session["licensed_artwork_ids"].append(verification.get("artwork_id", tweet_data["tweet_id"]))
        session["total_licensed"] = session.get("total_licensed", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + LICENSE_TOTAL + VERIFICATION_FEE

        log_decision("license_acquired", {
            "artwork_id": verification.get("artwork_id"),
            "artist_paid": f"${ARTIST_SHARE:.2f}",
            "platform_fee": f"${PLATFORM_FEE:.2f}",
            "verification_fee": f"${VERIFICATION_FEE:.2f}",
            "total_cost": f"${VERIFICATION_FEE + LICENSE_TOTAL:.2f}",
            "artist_wallet": artist_wallet[:16] + "..." if artist_wallet else "pending",
            "metavolve_wallet": METAVOLVE_WALLET[:16] + "...",
        }, reasoning=evaluation.get("reasoning", ""))
    else:
        event["license_acquired"] = False
        event["status"] = "rejected"
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "artist_share": 0,
            "platform_fee_metavolve": 0,
            "total_buyer_cost": VERIFICATION_FEE,
            "note": "Metavolve still earns $0.02 verification fee on rejected queries",
        }
        session["total_rejected"] = session.get("total_rejected", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + VERIFICATION_FEE

        log_decision("license_rejected", {
            "artwork_id": verification.get("artwork_id"),
            "reason": evaluation.get("reasoning"),
        })

    total_paid = sum(p.get("amount_usd", 0) for p in event["payments"])
    event["total_paid_usd"] = total_paid
    event["completed_at"] = datetime.now(timezone.utc).isoformat()
    event_ref.set(event)

    session["total_spent_usd"] = session.get("total_spent_usd", 0) + total_paid
    return event


def run_poll_cycle():
    """Execute one polling cycle across all monitored accounts."""
    session = load_session()

    # Reset daily budget if new day
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if session.get("budget_reset_date") != today:
        session["budget_spent_today_usd"] = 0.0
        session["budget_reset_date"] = today

    results = []
    processed = set(session.get("processed_tweet_ids", []))

    for username, account_info in MONITORED_ACCOUNTS.items():
        user_id = account_info.get("user_id")
        if not user_id:
            continue

        tweets = fetch_new_image_tweets(username, user_id)
        for tweet in tweets:
            if tweet["tweet_id"] in processed:
                continue

            logger.info(f"New drop from @{username}: {tweet['tweet_id']}")
            result = process_drop(tweet, account_info, session)
            results.append(result)

            session["processed_tweet_ids"].append(tweet["tweet_id"])
            # Keep last 500 to avoid unbounded growth
            if len(session["processed_tweet_ids"]) > 500:
                session["processed_tweet_ids"] = session["processed_tweet_ids"][-500:]

    session["last_poll_at"] = datetime.now(timezone.utc).isoformat()
    save_session(session)
    return results


# ---------------------------------------------------------------------------
# Flask Endpoints
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "agent": OPERATOR_ID,
        "persona": "AI Apprentice (Training Data Buyer)",
        "claude_model": CLAUDE_MODEL,
        "monitoring": list(MONITORED_ACCOUNTS.keys()),
    })


@app.route("/poll", methods=["POST"])
def trigger_poll():
    results = run_poll_cycle()
    return jsonify({
        "polled": list(MONITORED_ACCOUNTS.keys()),
        "new_drops": len(results),
        "results": [{
            "job_id": r.get("job_id"),
            "status": r.get("status"),
            "license_acquired": r.get("license_acquired"),
            "total_paid_usd": r.get("total_paid_usd"),
        } for r in results],
    })


@app.route("/session", methods=["GET"])
def get_session():
    return jsonify(load_session())


@app.route("/decisions", methods=["GET"])
def get_decisions():
    db = get_db()
    limit = int(request.args.get("limit", 20))
    docs = (
        db.collection("operator_apprentice").document("decisions")
        .collection("log")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return jsonify({"decisions": [d.to_dict() for d in docs]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
