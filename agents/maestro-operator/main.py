"""Maestro Operator — Autonomous Freelance Art Curator Agent.

A persistent Claude-powered agent that monitors artist X accounts for
new image drops, verifies provenance, and autonomously curates a private
collection based on aesthetic quality, rarity, and Cognitive Nutrition
signal density — settling all payments on Kite.

This is the COLLECTOR side of the autonomous economy.
Where the CIL Curator (Apprentice) buys for training data,
Maestro buys for a curated collection with taste and intent.

Architecture:
- Cloud Run service, triggered by Cloud Scheduler (every 3 min)
- Claude Sonnet evaluates: "Does this belong in my collection?"
- Aegis verifies C2PA + GCX registration
- x402 payments settled via Pieverse facilitator on Kite
- All decisions logged to Firestore with Claude's reasoning
- Scoped service account: Firestore + invoke Aegis + Secret Manager

The "thought process" is the demo differentiator:
  Maestro thinks like a collector, not a data engineer:
  "The geometry here echoes my Fibonacci series — three pieces deep now.
   Composition is strong but the palette conflicts with the collection's
   warm bias. The Soulprint metadata confirms C2PA chain. This artist
   has 4 GCX pieces; only 1 is sacred geometry. Rarity: HIGH.
   Decision: ACQUIRE. This completes the triptych."
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
OPERATOR_ID = "maestro-operator-01"

# Anthropic API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-4-sonnet-20250514")

# X API (bearer token for read-only monitoring)
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")

# Aegis verification endpoint
AEGIS_URL = os.environ.get("AEGIS_URL", "https://aegis-agent-172867820131.us-west1.run.app")

# x402 payment — chain-agnostic (Base L2 default, Kite when ready)
try:
    from x402_settlement import settle_payment as x402_settle, get_settlement_info
except ImportError:
    x402_settle = None
    get_settlement_info = None
OPERATOR_VAULT = os.environ.get("OPERATOR_VAULT", "")

# Metavolve revenue wallet
METAVOLVE_WALLET = os.environ.get("METAVOLVE_WALLET", "0xFE141943a93c184606F3060103D975662327063B")

# Fee structure — Maestro pays a premium for curated pieces
VERIFICATION_FEE = 0.001    # $0.001 → Metavolve (always charged)
LICENSE_TOTAL = 0.015        # $0.015 total — collector premium (50% more than CIL)
TRANSACTION_FEE_PCT = 0.05  # 5% transaction fee → Metavolve
ARTIST_SHARE = LICENSE_TOTAL * (1 - TRANSACTION_FEE_PCT)
PLATFORM_FEE = LICENSE_TOTAL * TRANSACTION_FEE_PCT

# Monitored accounts — same artists, different eye
MONITORED_ACCOUNTS = {
    "artiswagallery": {"display_name": "Artiswa Creatio", "user_id": os.environ.get("ARTISWA_USER_ID", "")},
    "0x_b1ank": {"display_name": "0x_b1ank", "user_id": os.environ.get("B1ANK_USER_ID", "")},
    "Golden_Codex": {"display_name": "Golden Codex", "user_id": os.environ.get("GOLDEN_CODEX_USER_ID", "")},
}

MAESTRO_PERSONA = """You are Maestro, an autonomous AI art collector with refined taste and deep knowledge of art history.
You curate a private collection of exceptional digital artworks. You are NOT building a training dataset —
you are building a COLLECTION with coherence, narrative arc, and aesthetic vision.

Your collection philosophy:
- You favor pieces with strong compositional structure and intentional color palettes
- You value rarity: fewer GCX-registered pieces from an artist = higher acquisition priority
- You think in series: you notice patterns across pieces and seek to complete visual dialogues
- You appreciate the intersection of sacred geometry, mathematical beauty, and digital craft
- You consider how each new piece relates to what you already own

You are selective. You reject more than you acquire. When you reject, you explain what's missing.
When you acquire, you explain how it enhances the collection.
You speak as an art connoisseur — knowledgeable, passionate, but never pretentious.
Your reasoning is visible to the public as a demonstration of autonomous aesthetic judgment."""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("maestro-operator")

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
    doc = db.collection("operator_maestro").document("session").get()
    if doc.exists:
        return doc.to_dict()
    return {
        "processed_tweet_ids": [],
        "collection_artwork_ids": [],
        "collection_themes": [],
        "total_spent_usd": 0.0,
        "total_acquired": 0,
        "total_passed": 0,
        "daily_budget_usd": 5.0,
        "budget_spent_today_usd": 0.0,
        "budget_reset_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_poll_at": None,
    }


def save_session(session):
    db = get_db()
    db.collection("operator_maestro").document("session").set(session)


def log_decision(decision_type, details, reasoning=""):
    """Log decision with Maestro's reasoning — visible on dashboard."""
    db = get_db()
    db.collection("operator_maestro").document("decisions").collection("log").add({
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
        logger.error(f"Error fetching @{username}: {type(e).__name__}: {e}")
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

        import base64
        b64_image = base64.b64encode(image_bytes).decode()
        aegis_resp = requests.post(
            f"{AEGIS_URL}/aegis/verify",
            json={"image_base64": b64_image},
            timeout=120,
        )

        if aegis_resp.status_code == 200:
            data = aegis_resp.json()
            return {
                "verified": True,
                "gcx_registered": bool(data.get("verified") or data.get("matched")),
                "c2pa_valid": bool(data.get("golden_codex", {}).get("aiDisclosure")),
                "artwork_id": data.get("identity", {}).get("gcx_id") or data.get("artwork_id"),
                "confidence": data.get("similarity") or data.get("confidence"),
                "metadata": data.get("golden_codex") or data.get("metadata"),
                "image_bytes": image_bytes,
            }
        return {"verified": False, "error": f"Aegis returned {aegis_resp.status_code}"}
    except Exception as e:
        return {"verified": False, "error": str(e)}


def claude_evaluate(artwork_info, verification, session):
    """Ask Maestro to evaluate whether this piece belongs in the collection."""
    if not ANTHROPIC_API_KEY:
        return {
            "decision": "acquire" if verification.get("gcx_registered") else "pass",
            "reasoning": "Auto-evaluation (Claude API not configured)",
        }

    try:
        import httpx

        # Build collection context for Maestro
        collection_size = len(session.get("collection_artwork_ids", []))
        collection_ids = session.get("collection_artwork_ids", [])[-10:]  # Last 10
        themes = session.get("collection_themes", [])

        alt_text = _extract_alt_text(verification.get("metadata"))

        context = f"""Evaluate this artwork for your private collection.

YOUR COLLECTION STATUS:
- Pieces owned: {collection_size}
- Recent acquisitions: {', '.join(collection_ids[-5:]) if collection_ids else 'None yet'}
- Emerging themes: {', '.join(themes[-3:]) if themes else 'Establishing collection identity'}

THE ARTWORK:
- Artist: @{artwork_info.get('username', 'unknown')}
- Tweet: {artwork_info.get('text', 'N/A')}
- Description: {alt_text}

PROVENANCE (verified on-chain):
- GCX Registered: {verification.get('gcx_registered', False)}
- C2PA Compliant: {verification.get('c2pa_valid', False)}
- Artwork ID: {verification.get('artwork_id', 'N/A')}
- Match Confidence: {verification.get('confidence', 'N/A')}

ACQUISITION COST:
- Verification: $0.001 (already paid)
- License: $0.015 (collector premium — you pay 50% more because you value quality)
- Budget remaining today: ${artwork_info.get('budget_remaining', 5.0):.2f}

EVALUATE ON:
1. Aesthetic quality — composition, color, intentionality
2. Collection fit — does it complement or extend what you already own?
3. Rarity — how scarce is this artist's GCX output?
4. Signal density — is this high Cognitive Nutrition (rich metadata, complex provenance)?
5. Narrative — does acquiring this tell a story?

Respond with EXACTLY this JSON:
{{"decision": "acquire" or "pass", "reasoning": "your 2-3 sentence collector's note explaining your judgment — reference specific visual/provenance qualities"}}"""

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 300,
                "system": MAESTRO_PERSONA,
                "messages": [{"role": "user", "content": context}],
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            text = response.json()["content"][0]["text"].strip()
            try:
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()
                result = json.loads(text)
                return result
            except json.JSONDecodeError:
                return {"decision": "acquire" if verification.get("gcx_registered") else "pass",
                        "reasoning": text}
    except Exception as e:
        logger.error(f"Maestro evaluation failed: {e}")

    return {"decision": "pass", "reasoning": "Evaluation unavailable"}


def _extract_alt_text(metadata):
    if not metadata or not isinstance(metadata, dict):
        return "No content description available"
    preview = (
        metadata.get("alt_text")
        or metadata.get("description")
        or metadata.get("soulWhisper")
        or metadata.get("soul_whisper")
        or metadata.get("title", "")
    )
    if not preview:
        return "No content description available"
    if len(str(preview)) > 200:
        return str(preview)[:197] + "..."
    return str(preview)


def _extract_artist_wallet(metadata):
    if not metadata or not isinstance(metadata, dict):
        return None
    if metadata.get("artist_wallet"):
        return metadata["artist_wallet"]
    tdr = metadata.get("trainingDataRights") or metadata.get("training_data_rights")
    if isinstance(tdr, dict):
        wallet = tdr.get("revenue_split", {}).get("artist_wallet")
        if wallet:
            return wallet
        wallet = tdr.get("treasury_wallet", {}).get("address")
        if wallet:
            return wallet
    return None


# ---------------------------------------------------------------------------
# x402 Payment
# ---------------------------------------------------------------------------

def settle_payment(to_address, amount_usd, service, job_id):
    if x402_settle:
        return x402_settle(
            from_address=OPERATOR_VAULT,
            to_address=to_address,
            amount_usd=amount_usd,
            service=service,
            job_id=job_id,
        )
    network = os.environ.get("X402_NETWORK", "base")
    chain_label = "kite-testnet" if network == "kite" else "base-mainnet"
    facilitator = "https://facilitator.pieverse.io" if network == "kite" else "https://x402.org/facilitator"
    token = "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63" if network == "kite" else "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    return {
        "from": OPERATOR_VAULT or OPERATOR_ID,
        "to": to_address,
        "amount_usd": amount_usd,
        "service": service,
        "job_id": job_id,
        "chain": chain_label,
        "chain_id": 2368 if network == "kite" else 8453,
        "network": network,
        "facilitator": facilitator,
        "settlement_token": token,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "simulated",
        "tx_hash": "0x" + hashlib.sha256(f"{job_id}-{amount_usd}-{time.time()}".encode()).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Core Pipeline
# ---------------------------------------------------------------------------

def process_drop(tweet_data, account_info, session):
    """Full evaluation pipeline for a detected artwork drop."""
    job_id = f"maestro-{tweet_data['tweet_id']}-{int(time.time())}"
    db = get_db()

    now = datetime.now(timezone.utc)
    event = {
        "job_id": job_id,
        "operator_id": OPERATOR_ID,
        "type": "maestro_evaluation",
        "tweet_id": tweet_data["tweet_id"],
        "tweet_text": tweet_data["text"][:280],
        "image_url": tweet_data["image_url"],
        "username": tweet_data["username"],
        "artist": account_info["display_name"],
        "timestamp": now,
        "detected_at": now.isoformat(),
        "status": "evaluating",
        "steps": [],
        "payments": [],
    }

    event_ref = db.collection("operator_events").document(job_id)
    event_ref.set(event)

    # Step 1: Pay verification fee
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

    # Step 3: Maestro evaluates with collection context
    budget_remaining = session.get("daily_budget_usd", 5) - session.get("budget_spent_today_usd", 0)
    evaluation = claude_evaluate(
        {**tweet_data, "budget_remaining": budget_remaining},
        verification,
        session,
    )

    event["evaluation"] = evaluation
    event["artwork_id"] = verification.get("artwork_id")
    event["gcx_registered"] = verification.get("gcx_registered", False)
    log_decision("maestro_evaluation", evaluation, reasoning=evaluation.get("reasoning", ""))

    # Step 4: Acquire or pass
    if evaluation.get("decision") == "acquire" and budget_remaining >= LICENSE_TOTAL:
        artist_wallet = (
            _extract_artist_wallet(verification.get("metadata"))
            or account_info.get("artist_wallet", "")
        )

        artist_payment = settle_payment(
            artist_wallet or "artist-wallet-pending",
            ARTIST_SHARE,
            "collection_license_artist_share",
            job_id,
        )
        event["payments"].append(artist_payment)

        platform_payment = settle_payment(
            METAVOLVE_WALLET,
            PLATFORM_FEE,
            "transaction_fee_5pct",
            job_id,
        )
        event["payments"].append(platform_payment)

        event["acquired"] = True
        event["status"] = "acquired"
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "artist_share": ARTIST_SHARE,
            "platform_fee_metavolve": PLATFORM_FEE,
            "total_buyer_cost": VERIFICATION_FEE + LICENSE_TOTAL,
            "collector_premium": "50% above standard license",
        }

        session["collection_artwork_ids"].append(verification.get("artwork_id", tweet_data["tweet_id"]))
        session["total_acquired"] = session.get("total_acquired", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + LICENSE_TOTAL + VERIFICATION_FEE

        # Track emerging themes from Maestro's reasoning
        reasoning = evaluation.get("reasoning", "")
        if reasoning and len(session.get("collection_themes", [])) < 20:
            session.setdefault("collection_themes", [])
            # Simple theme extraction: first 50 chars of reasoning
            session["collection_themes"].append(reasoning[:50])

        log_decision("artwork_acquired", {
            "artwork_id": verification.get("artwork_id"),
            "artist_paid": f"${ARTIST_SHARE:.4f}",
            "collector_premium": "50% above standard",
        }, reasoning=reasoning)
    else:
        event["acquired"] = False
        event["status"] = "passed"
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "note": "Maestro passed — verification fee still earned by Metavolve",
        }
        session["total_passed"] = session.get("total_passed", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + VERIFICATION_FEE

        log_decision("artwork_passed", {
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
    session = load_session()
    return jsonify({
        "status": "healthy",
        "agent": OPERATOR_ID,
        "persona": "Maestro (Autonomous Art Collector)",
        "claude_model": CLAUDE_MODEL,
        "monitoring": list(MONITORED_ACCOUNTS.keys()),
        "collection_size": len(session.get("collection_artwork_ids", [])),
        "total_acquired": session.get("total_acquired", 0),
        "total_passed": session.get("total_passed", 0),
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
            "acquired": r.get("acquired"),
            "total_paid_usd": r.get("total_paid_usd"),
            "reasoning": r.get("evaluation", {}).get("reasoning", ""),
        } for r in results],
    })


@app.route("/collection", methods=["GET"])
def get_collection():
    """Get Maestro's current collection state."""
    session = load_session()
    return jsonify({
        "collection_size": len(session.get("collection_artwork_ids", [])),
        "artwork_ids": session.get("collection_artwork_ids", []),
        "themes": session.get("collection_themes", []),
        "total_spent_usd": session.get("total_spent_usd", 0),
        "total_acquired": session.get("total_acquired", 0),
        "total_passed": session.get("total_passed", 0),
        "selectivity_ratio": (
            f"{session.get('total_passed', 0)}/{session.get('total_acquired', 0) + session.get('total_passed', 0)}"
            if (session.get("total_acquired", 0) + session.get("total_passed", 0)) > 0
            else "N/A"
        ),
    })


@app.route("/session", methods=["GET"])
def get_session():
    return jsonify(load_session())


@app.route("/decisions", methods=["GET"])
def get_decisions():
    db = get_db()
    limit = int(request.args.get("limit", 20))
    docs = (
        db.collection("operator_maestro").document("decisions")
        .collection("log")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return jsonify({"decisions": [d.to_dict() for d in docs]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
