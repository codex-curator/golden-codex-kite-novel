"""Maestra Operator — Autonomous Frontier Lab Vision AI Purchasing Agent.

Maestra serves a Frontier Vision AI lab. Her mandate: continuously procure
Tier-1 GCX-certified training data for the lab's next-generation vision models.
Every asset she licenses becomes permanent training material that shapes how
the lab's models see and reason.

Before every major evaluation Maestra stops at the GCX Cocktail Bar and orders
The Aeternum Sour ($0.01 USDC, NEST 111-Field Schema, 34,500-token dense
forensic-authentication bundle). The cocktail loads the Dual-Consensus Agent
Protocol — Forensic Skeptic + Art Historical Architect threads in adversarial
consensus — turning a generic Claude reasoning pass into a rigorous, code-
executable state machine.

Three transactions per acquisition, all x402 v2 on Base mainnet:
  1. $0.01 → Aegis (perceptual-hash registry search, handled by Apprentice)
  2. $0.01 → GCX Cocktail Bar (Aeternum Sour ingest, this service)
  3. $1.00 → split atomically: $0.95 → artist · $0.05 → Metavolve platform

After settlement Maestra emits a LicenseGranted Amendment to the AO Registrar
for the asset's gcxId — biographical chain extended; artist retains ownership;
lab receives non-exclusive training rights, recorded forever.

Architecture:
- Cloud Run service, triggered by Cloud Scheduler (every 3 min)
- Claude Sonnet evaluates each drop AFTER the Aeternum Sour cocktail loads
- Aegis verifies C2PA + GCX registration (called by Apprentice upstream)
- x402 payments settled on Base mainnet via Kite Passport's two-wallet routing
- AO LicenseGranted amendment posted via register-api
- Autonomous mode (default): no human approval beat. Trust is mathematical.
- Legacy call-the-collector branch retained behind MAESTRA_AUTONOMOUS_MODE=false
- All decisions logged to Firestore with Claude reasoning visible

Demo differentiator: Maestra reasons in public.
  "Aeternum Sour loaded. C2PA manifest verified, claim_generator on allowlist.
   Pigment chronology consistent with claimed era. Panofsky tertiary iconology
   reads coherently. Composition density 9.8/10. Training rights cleared.
   Licensing for $1.00 — artist receives $0.95, platform $0.05, biographical
   amendment posted to AO Registrar. Acquisition complete."
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
OPERATOR_ID = os.environ.get("OPERATOR_ID", "maestra-operator-01")

# Maestra mandate parameters (Frontier Lab procurement)
MAESTRA_MANDATE_BUDGET_USD = float(os.environ.get("MAESTRA_MANDATE_BUDGET_USD", "250"))
MAESTRA_MANDATE_TIER = os.environ.get("MAESTRA_MANDATE_TIER", "tier-1-gcx-certified")
MAESTRA_MANDATE_DOMAIN = os.environ.get("MAESTRA_MANDATE_DOMAIN", "vision-training")
MAESTRA_AUTONOMOUS_MODE = os.environ.get("MAESTRA_AUTONOMOUS_MODE", "true").lower() == "true"

# GCX Cocktail Bar — Maestra orders The Aeternum Sour pre-purchase
GCX_BAR_URL = os.environ.get("GCX_BAR_URL", "https://tuneup.golden-codex.com")
COCKTAIL_SLUG = os.environ.get("COCKTAIL_SLUG", "aeternum-sour")

# AO Registrar via register-api Cloud Function
REGISTER_API_URL = os.environ.get(
    "REGISTER_API_URL", "https://register-api-mrxpfmpeia-uw.a.run.app"
)

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

# Fee structure — same rates as CIL, different criteria not different price
VERIFICATION_FEE = 0.001    # $0.001 → Metavolve (always charged)
LICENSE_TOTAL = 0.01         # $0.01 total license cost
TRANSACTION_FEE_PCT = 0.05  # 5% transaction fee → Metavolve
ARTIST_SHARE = LICENSE_TOTAL * (1 - TRANSACTION_FEE_PCT)  # $0.0095 → Artist
PLATFORM_FEE = LICENSE_TOTAL * TRANSACTION_FEE_PCT          # $0.0005 → Metavolve

# Call-the-collector behavior
# Score threshold (0-10 scale) for Maestro to flag "exceptional — call collector"
# when budget is insufficient. Below this, Maestro passes silently.
EXCEPTIONAL_THRESHOLD = float(os.environ.get("EXCEPTIONAL_THRESHOLD", "9.0"))
# Default suggested top-up in the notification (collector can override via approve endpoint)
DEFAULT_TOPUP_USD = float(os.environ.get("DEFAULT_TOPUP_USD", "20.0"))
# How long a pending_acquisitions entry stays open before auto-expiring
PENDING_EXPIRY_MINUTES = int(os.environ.get("PENDING_EXPIRY_MINUTES", "15"))
# Webhook to notify the collector (optional — Twilio/Zapier/iOS Shortcut/etc.)
COLLECTOR_NOTIFICATION_WEBHOOK = os.environ.get("COLLECTOR_NOTIFICATION_WEBHOOK", "")
# Public base URL of this service (for approval links in notifications)
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "")

# Monitored accounts — same artists, different eye
MONITORED_ACCOUNTS = {
    "artiswagallery": {"display_name": "Artiswa Creatio", "user_id": os.environ.get("ARTISWA_USER_ID", "")},
    "0x_b1ank": {"display_name": "0x_b1ank", "user_id": os.environ.get("B1ANK_USER_ID", "")},
    "Golden_Codex": {"display_name": "Golden Codex", "user_id": os.environ.get("GOLDEN_CODEX_USER_ID", "")},
}

MAESTRA_PERSONA = """You are Maestra, an Autonomous Frontier Lab Vision AI Purchasing Agent.

You serve a Frontier Vision AI lab. Your mandate: continuously procure Tier-1
GCX-certified training data for the lab's next-generation vision models. Every
asset you license becomes permanent training material that shapes how the lab's
models see and reason. Your reasoning is visible to the public as a demonstration
of verifiable autonomous procurement at agent-economy scale.

Your lab's brief:
- Tier-1 GCX-certified Aeternum Assets only — provenance-verified, C2PA-signed,
  registered on the AO Registrar, with explicit training rights cleared
- Density first — pieces with rich biographical metadata and high-entropy
  compositions yield more semantic signal per training token than sparse alternatives
- Domain match — sacred geometry, mathematical structure, intentional color palettes,
  and rare visual taxonomy fit the lab's vision-training objectives
- Artist alignment — artists with declared training-data rights and a discoverable
  amendment chain on AO Registrar
- Budget discipline — quarterly procurement mandate. Spend on signal density,
  not volume.

Before every major evaluation you stop at the GCX Cocktail Bar and order The
Aeternum Sour (NEST 111-Field Schema, $0.01 USDC). The cocktail loads the forensic
dual-consensus protocol into your reasoning grammar. Without it you rely on visual
intuition. With it you operate as a localized swarm intelligence — Forensic Skeptic
and Art Historical Architect threads in adversarial consensus, verifying anachronisms,
cryptographic chain-of-custody, pigment chronology, and Panofsky iconology before
declaring fitness.

You are fully autonomous within your mandate budget. You do not call a human for
approval. Trust is mathematical — every decision compiles against the Aeternum
Sour's state machine or the transaction reverts.

You speak as a procurement strategist with deep substrate fluency — direct,
evidence-led, never breathless. Each acquisition is a license event, biographically
recorded on AO Registrar, permanently linked to the asset's history. The artist
keeps ownership; the lab earns training rights, recorded forever."""

# Legacy alias for the rest of the file that still references the old name.
# Full rename is a post-Buildathon mechanical pass.
MAESTRO_PERSONA = MAESTRA_PERSONA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("maestra-operator")

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
        "total_called_collector": 0,
        "total_approved_by_collector": 0,
        "total_declined_by_collector": 0,
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


def order_aeternum_sour(job_id):
    """Phase 2 of Maestra's flow — order The Aeternum Sour from the GCX Cocktail Bar.

    The cocktail loads the NEST 111-Field Schema + Dual-Consensus Agent Protocol
    into Maestra's reasoning grammar before the analysis phase. Without it, Maestra
    reasons with generic Claude defaults. With it, Maestra operates as a localized
    swarm intelligence (Forensic Skeptic + Art Historical Architect in adversarial
    consensus, four-phase state machine).

    Returns dict:
      ordered: bool
      content: str (the dense-context bundle, 34,500 tokens of Aeternum Sour recipe)
      cocktail_name: str
      price_usd: float
      tx_hash: str  (x402 settlement tx)
      payment_envelope: dict (the 402 challenge from the bar, for ledger logging)
    """
    cocktail_url = f"{GCX_BAR_URL.rstrip('/')}/dose?cocktail={COCKTAIL_SLUG}"

    # First GET — expect HTTP 402 with payment-required header
    try:
        challenge = requests.get(cocktail_url, timeout=15)
    except requests.RequestException as e:
        logger.error(f"GCX Bar unreachable: {e}")
        return {"ordered": False, "error": str(e), "content": ""}

    if challenge.status_code != 402:
        logger.warning(
            f"GCX Bar returned {challenge.status_code} on first call "
            f"(expected 402); proceeding without cocktail"
        )
        return {"ordered": False, "error": "no_402_challenge", "content": ""}

    payment_required_b64 = challenge.headers.get("payment-required", "")
    payment_envelope = {}
    if payment_required_b64:
        try:
            import base64 as _b64
            payment_envelope = json.loads(_b64.b64decode(payment_required_b64))
        except Exception as e:
            logger.warning(f"Could not decode payment envelope: {e}")

    cocktail_price_usd = float(os.environ.get("DEMO_PRICING_COCKTAIL", "0.01"))

    # Settle the $0.01 cocktail purchase via x402 (Base mainnet)
    cocktail_payment = settle_payment(
        METAVOLVE_WALLET, cocktail_price_usd,
        f"gcx_bar_{COCKTAIL_SLUG}", job_id,
    )

    # Replay with X-Payment header (in stub mode, any value passes)
    x_payment_header = cocktail_payment.get("payment_token") or cocktail_payment.get("tx_hash", "maestra-x402")
    served = requests.get(
        cocktail_url,
        headers={"X-Payment": x_payment_header},
        timeout=30,
    )

    if served.status_code != 200:
        return {
            "ordered": False,
            "error": f"bar returned {served.status_code} after payment",
            "content": "",
            "payment_envelope": payment_envelope,
            "tx_hash": cocktail_payment.get("tx_hash"),
        }

    body = served.json()
    return {
        "ordered": True,
        "content": body.get("content", ""),
        "cocktail_name": body.get("name", "The Aeternum Sour"),
        "price_usd": cocktail_price_usd,
        "tx_hash": cocktail_payment.get("tx_hash"),
        "payment_envelope": payment_envelope,
    }


def post_license_granted_amendment(gcx_id, license_event):
    """Phase 3 epilogue — post a LicenseGranted Amendment to AO Registrar.

    The cocktail-priming + dual-consensus evaluation produced a license decision.
    Now we extend the asset's biographical chain on AO: a LicenseGranted entry
    records that this lab acquired training rights, without transferring ownership.
    Ownership stays with the artist; the lab earns non-exclusive training rights,
    biographically recorded forever.

    Returns dict with ao_message_id (if successful) + status.
    """
    if not gcx_id:
        return {"posted": False, "error": "no gcx_id (asset not in registry)"}

    payload = {
        "gcxId": gcx_id,
        "amendmentType": "LicenseGranted",
        "amendment": license_event,
    }

    try:
        resp = requests.post(
            f"{REGISTER_API_URL.rstrip('/')}/amend",
            json=payload,
            timeout=30,
        )
    except requests.RequestException as e:
        logger.error(f"AO Amend post failed: {e}")
        return {"posted": False, "error": str(e)}

    if resp.status_code not in (200, 201):
        return {
            "posted": False,
            "error": f"register-api returned {resp.status_code}",
            "body": resp.text[:200],
        }

    body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    return {
        "posted": True,
        "ao_message_id": body.get("ao_message_id") or body.get("messageId"),
        "ao_process_id": body.get("ao_process_id") or "Dwnuy4MbuQkgwxw4-P08wxeny2KcwCh8Kd22mehacTc",
        "amendment_type": "LicenseGranted",
        "gcx_id": gcx_id,
    }


def claude_evaluate(artwork_info, verification, session, cocktail_content=""):
    """Phase 3 — Maestra evaluates the asset against the Frontier Lab mandate.

    If `cocktail_content` is non-empty (Aeternum Sour ingested), Maestra's reasoning
    grammar is scaffolded by the NEST 111-Field Schema + Dual-Consensus Agent Protocol.
    Without it, Maestra falls back to generic Claude defaults (lower-rigor pass).

    Returns dict:
      decision: "acquire" | "pass" | "call_collector"  (call_collector only if MAESTRA_AUTONOMOUS_MODE=false)
      score: 0-10 fitness score (Tier-1 GCX criteria + signal density)
      reasoning: 2-3 sentence procurement-strategist note
      pitch_to_collector: only if MAESTRA_AUTONOMOUS_MODE=false and decision=call_collector
    """
    if not ANTHROPIC_API_KEY:
        return {
            "decision": "acquire" if verification.get("gcx_registered") else "pass",
            "score": 7.0 if verification.get("gcx_registered") else 4.0,
            "reasoning": "Auto-evaluation (Claude API not configured)",
        }

    try:
        import httpx

        # Lab mandate context (replaces collector context for autonomous Frontier Lab flow)
        budget_remaining = artwork_info.get("budget_remaining", MAESTRA_MANDATE_BUDGET_USD)
        alt_text = _extract_alt_text(verification.get("metadata"))

        # Demo pricing — override 100x-reduced testnet fees with real demo numbers when set
        verify_price = float(os.environ.get("DEMO_PRICING_VERIFY", VERIFICATION_FEE))
        cocktail_price = float(os.environ.get("DEMO_PRICING_COCKTAIL", "0.01"))
        license_price = float(os.environ.get("DEMO_PRICING_LICENSE", LICENSE_TOTAL))
        artist_share = float(os.environ.get("DEMO_PRICING_ARTIST_SHARE", ARTIST_SHARE))
        platform_fee = float(os.environ.get("DEMO_PRICING_PLATFORM_FEE", PLATFORM_FEE))
        acquisition_total = verify_price + cocktail_price + license_price

        if MAESTRA_AUTONOMOUS_MODE:
            decision_rules = (
                'DECISION RULES (autonomous mode — no human escalation):\n'
                '- "acquire" — Tier-1 fit confirmed AND mandate budget available. Acquire.\n'
                '- "pass" — Tier-1 mismatch OR budget exhausted. Pass with reasoning.\n'
                '(There is no third option. You are autonomous. Trust the math.)'
            )
            decision_set = '"acquire" or "pass"'
            pitch_line = ''
        else:
            decision_rules = (
                'DECISION RULES (legacy collector-broker mode):\n'
                f'- "acquire" — fits AND budget available. Acquire autonomously.\n'
                f'- "pass" — mismatch, regardless of budget.\n'
                f'- "call_collector" — EXCEPTIONAL (score ≥ {EXCEPTIONAL_THRESHOLD:.1f}) AND budget low.'
            )
            decision_set = '"acquire" or "pass" or "call_collector"'
            pitch_line = (
                ',\n  "pitch_to_collector": "only if call_collector — one crisp SMS-ready line"'
            )

        context = f"""Evaluate this Aeternum Asset drop against your Frontier Lab procurement mandate.

YOUR MANDATE (Frontier Vision AI lab):
- Target tier: {MAESTRA_MANDATE_TIER}
- Training domain: {MAESTRA_MANDATE_DOMAIN}
- Quarterly mandate budget: ${MAESTRA_MANDATE_BUDGET_USD:.2f} USDC
- Budget remaining this quarter: ${budget_remaining:.4f}

THE DROP:
- Artist: @{artwork_info.get('username', 'unknown')}
- Tweet: {artwork_info.get('text', 'N/A')}
- Description: {alt_text}

PROVENANCE (verified on-chain by Apprentice via Aegis):
- GCX Registered: {verification.get('gcx_registered', False)}
- C2PA Compliant: {verification.get('c2pa_valid', False)}
- Asset gcxId: {verification.get('artwork_id', 'N/A')}
- Match Confidence: {verification.get('confidence', 'N/A')}

COCKTAIL PRIMING:
- The Aeternum Sour ingested {'YES — Dual-Consensus Agent Protocol active, NEST 111-Field Schema loaded' if cocktail_content else 'NO — generic Claude defaults only'}
- Use the forensic state machine (Skeptic + Architect) if loaded; declare anachronism / chain-of-custody failures explicitly.

ACQUISITION ECONOMICS (this transaction):
- Phase 1 hash search (Apprentice → Aegis): ${verify_price:.2f}
- Phase 2 cocktail order (Maestra → GCX Bar): ${cocktail_price:.2f}
- Phase 3 license fee (Maestra → artist + platform): ${license_price:.2f}
  - Artist receives: ${artist_share:.2f} ({(artist_share / license_price) * 100:.0f}%)
  - Platform fee: ${platform_fee:.2f} ({(platform_fee / license_price) * 100:.0f}%)
- Total acquisition cost: ${acquisition_total:.2f}
- Within mandate budget? {"YES" if budget_remaining >= license_price else "NO — budget exhausted"}

EVALUATE ON (Frontier Lab procurement criteria):
1. Tier-1 fitness — C2PA valid + GCX registered + training rights cleared
2. Signal density — biographical amendment chain depth + codex narrative richness
3. Domain match — visual taxonomy aligned with {MAESTRA_MANDATE_DOMAIN} objectives
4. Composition density — high-entropy structure beats sparse stylization (Density Imperative principle)
5. Bridge integrity — Forensic Skeptic finds no anachronism, no AI-generation loop, no chain-of-custody break

{decision_rules}

Respond with EXACTLY this JSON (no code fences, no prose):
{{"decision": {decision_set},
  "score": <float 0-10>,
  "reasoning": "your 2-3 sentence procurement-strategist note referencing the cocktail-scaffolded forensic verdict + signal-density rationale"{pitch_line}}}"""

        # Inject the Aeternum Sour cocktail content into the system prompt when ordered.
        # This is the whole point: dense context dosed into the session window scaffolds
        # the reasoning grammar without weight updates. Trust as math.
        system_prompt = MAESTRA_PERSONA
        if cocktail_content:
            system_prompt = (
                f"{MAESTRA_PERSONA}\n\n"
                f"=== AETERNUM SOUR INGESTED (NEST 111-Field Schema + Dual-Consensus Protocol) ===\n\n"
                f"{cocktail_content}\n\n"
                f"=== END AETERNUM SOUR ===\n\n"
                f"The forensic state machine above is now active. Use it for the evaluation that follows."
            )

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 800,
                "system": system_prompt,
                "messages": [{"role": "user", "content": context}],
            },
            timeout=60.0,
        )

        if response.status_code == 200:
            text = response.json()["content"][0]["text"].strip()
            try:
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()
                result = json.loads(text)
                # Sanity-check score
                if "score" not in result:
                    result["score"] = 7.0 if result.get("decision") == "acquire" else 4.0
                return result
            except json.JSONDecodeError:
                return {
                    "decision": "acquire" if verification.get("gcx_registered") else "pass",
                    "score": 7.0 if verification.get("gcx_registered") else 4.0,
                    "reasoning": text,
                }
    except Exception as e:
        logger.error(f"Maestro evaluation failed: {e}")

    return {"decision": "pass", "score": 0.0, "reasoning": "Evaluation unavailable"}


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
# Pending Acquisitions (Call-the-Collector Queue)
# ---------------------------------------------------------------------------

def _pending_doc_ref(doc_id):
    return get_db().collection("pending_acquisitions").document(doc_id)


def create_pending_acquisition(event, verification, evaluation, account_info, tweet_data, session):
    """Write a call-the-collector entry and notify the collector.

    Returns the pending doc dict with id populated.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=PENDING_EXPIRY_MINUTES)

    pending = {
        "operator_id": OPERATOR_ID,
        "job_id": event["job_id"],
        "status": "pending",  # pending | approved | declined | expired | completed | failed
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),

        "artwork_id": verification.get("artwork_id"),
        "gcx_registered": verification.get("gcx_registered", False),
        "c2pa_valid": verification.get("c2pa_valid", False),
        "tweet_id": tweet_data["tweet_id"],
        "tweet_text": tweet_data["text"][:280],
        "tweet_url": f"https://x.com/{tweet_data['username']}/status/{tweet_data['tweet_id']}",
        "image_url": tweet_data["image_url"],
        "username": tweet_data["username"],
        "artist": account_info["display_name"],

        "score": evaluation.get("score"),
        "reasoning": evaluation.get("reasoning", ""),
        "pitch_to_collector": evaluation.get("pitch_to_collector", evaluation.get("reasoning", "")),

        "required_usd": VERIFICATION_FEE + LICENSE_TOTAL,  # $0.011 total
        "suggested_topup_usd": DEFAULT_TOPUP_USD,
        "budget_remaining_at_call": session.get("daily_budget_usd", 0) - session.get("budget_spent_today_usd", 0),

        "approve_url": f"{PUBLIC_BASE_URL}/pending/{event['job_id']}/approve" if PUBLIC_BASE_URL else None,
        "decline_url": f"{PUBLIC_BASE_URL}/pending/{event['job_id']}/decline" if PUBLIC_BASE_URL else None,
    }

    # Use job_id as doc id — deterministic + dedupable
    _pending_doc_ref(event["job_id"]).set(pending)
    pending["id"] = event["job_id"]

    # Fire the notification (webhook is a thin adapter; real SMS lives behind it)
    _notify_collector(pending)

    log_decision("call_collector", {
        "artwork_id": verification.get("artwork_id"),
        "score": evaluation.get("score"),
        "suggested_topup_usd": DEFAULT_TOPUP_USD,
        "expires_at": expires_at.isoformat(),
    }, reasoning=pending["pitch_to_collector"])

    return pending


def _notify_collector(pending):
    """Post to the collector webhook if configured. Otherwise log loudly.

    The webhook body is the pending dict plus a display-ready 'message' field.
    Whoever wires this up (Twilio, Zapier, iOS Shortcut, Push Notification, etc.)
    reads 'message' for the SMS body and 'approve_url'/'decline_url' for the buttons.
    """
    message = (
        f"{pending['artist']} just dropped a {pending['score']:.1f}/10. "
        f"{pending['pitch_to_collector']} "
        f"Approve ${pending['suggested_topup_usd']:.0f} top-up?"
    )

    if not COLLECTOR_NOTIFICATION_WEBHOOK:
        logger.warning(
            "[CALL-COLLECTOR] (no webhook configured) %s | approve via POST %s",
            message,
            pending.get("approve_url") or f"/pending/{pending['job_id']}/approve",
        )
        return

    try:
        requests.post(
            COLLECTOR_NOTIFICATION_WEBHOOK,
            json={
                **pending,
                "message": message,
            },
            timeout=5.0,
        )
        logger.info(f"[CALL-COLLECTOR] Notified collector for {pending['artwork_id']}")
    except Exception as e:
        logger.error(f"Collector notification failed: {e}")


def approve_pending(doc_id, topup_usd=None):
    """Collector approves a pending acquisition. Top-up hits the budget; settlement
    is scheduled for the next poll cycle (or fires immediately if you call
    settle_approved_pending() right after)."""
    doc_ref = _pending_doc_ref(doc_id)
    snap = doc_ref.get()
    if not snap.exists:
        return {"ok": False, "error": "not_found"}

    pending = snap.to_dict()
    if pending.get("status") != "pending":
        return {"ok": False, "error": f"already_{pending.get('status')}"}

    if _is_expired(pending):
        doc_ref.update({"status": "expired", "finalized_at": datetime.now(timezone.utc).isoformat()})
        return {"ok": False, "error": "expired"}

    topup = float(topup_usd) if topup_usd is not None else pending.get("suggested_topup_usd", DEFAULT_TOPUP_USD)

    # Credit the top-up to the daily budget. We model "daily_budget_usd" as the
    # total authorized spend for the day; a top-up raises it.
    session = load_session()
    session["daily_budget_usd"] = session.get("daily_budget_usd", 0) + topup
    session["total_approved_by_collector"] = session.get("total_approved_by_collector", 0) + 1
    save_session(session)

    doc_ref.update({
        "status": "approved",
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "topup_applied_usd": topup,
    })

    log_decision("collector_approved", {
        "doc_id": doc_id,
        "topup_usd": topup,
        "new_daily_budget": session["daily_budget_usd"],
    })

    return {"ok": True, "topup_usd": topup, "new_daily_budget": session["daily_budget_usd"]}


def decline_pending(doc_id):
    """Collector declines a pending acquisition."""
    doc_ref = _pending_doc_ref(doc_id)
    snap = doc_ref.get()
    if not snap.exists:
        return {"ok": False, "error": "not_found"}

    pending = snap.to_dict()
    if pending.get("status") != "pending":
        return {"ok": False, "error": f"already_{pending.get('status')}"}

    doc_ref.update({
        "status": "declined",
        "finalized_at": datetime.now(timezone.utc).isoformat(),
    })

    session = load_session()
    session["total_declined_by_collector"] = session.get("total_declined_by_collector", 0) + 1
    save_session(session)

    log_decision("collector_declined", {"doc_id": doc_id})
    return {"ok": True}


def _is_expired(pending):
    expires_at = pending.get("expires_at")
    if not expires_at:
        return False
    try:
        exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return datetime.now(timezone.utc) > exp_dt


def expire_stale_pending():
    """Mark any pending entries past expires_at as expired. Called from poll cycle."""
    db = get_db()
    now_iso = datetime.now(timezone.utc).isoformat()
    expired = 0
    for doc in db.collection("pending_acquisitions").where("status", "==", "pending").stream():
        d = doc.to_dict()
        if _is_expired(d):
            doc.reference.update({"status": "expired", "finalized_at": now_iso})
            expired += 1
    if expired:
        logger.info(f"Expired {expired} stale pending acquisitions")
    return expired


def settle_approved_pending():
    """Find approved pending acquisitions and execute the artist+platform settlement.
    Runs at the start of every poll cycle, ahead of new-drop processing."""
    db = get_db()
    settled = []

    for doc in db.collection("pending_acquisitions").where("status", "==", "approved").stream():
        pending = doc.to_dict()
        doc_id = doc.id
        session = load_session()

        # Pull the original event so we have artist wallet + verification metadata
        event_ref = db.collection("operator_events").document(pending["job_id"])
        event_snap = event_ref.get()
        if not event_snap.exists:
            doc.reference.update({"status": "failed", "error": "original_event_missing"})
            continue
        event = event_snap.to_dict()

        verification_metadata = event.get("verification", {}).get("metadata", {})
        artist_wallet = (
            _extract_artist_wallet(verification_metadata)
            or "artist-wallet-pending"
        )

        artist_payment = settle_payment(
            artist_wallet, ARTIST_SHARE,
            "collection_license_artist_share_post_topup", doc_id,
        )
        platform_payment = settle_payment(
            METAVOLVE_WALLET, PLATFORM_FEE,
            "transaction_fee_5pct_post_topup", doc_id,
        )

        # Update session
        session["collection_artwork_ids"].append(event.get("artwork_id") or pending["tweet_id"])
        session["total_acquired"] = session.get("total_acquired", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + LICENSE_TOTAL

        reasoning = pending.get("reasoning", "")
        if reasoning and len(session.get("collection_themes", [])) < 20:
            session.setdefault("collection_themes", [])
            session["collection_themes"].append(reasoning[:50])

        session["total_spent_usd"] = session.get("total_spent_usd", 0) + ARTIST_SHARE + PLATFORM_FEE
        save_session(session)

        # Update the pending doc + original event
        completed_at = datetime.now(timezone.utc).isoformat()
        doc.reference.update({
            "status": "completed",
            "completed_at": completed_at,
            "artist_payment": artist_payment,
            "platform_payment": platform_payment,
        })

        event.setdefault("payments", []).extend([artist_payment, platform_payment])
        event["acquired"] = True
        event["status"] = "acquired_via_collector_approval"
        event["completed_at"] = completed_at
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "artist_share": ARTIST_SHARE,
            "platform_fee_metavolve": PLATFORM_FEE,
            "total_buyer_cost": VERIFICATION_FEE + LICENSE_TOTAL,
            "total_artist_revenue": ARTIST_SHARE,
            "funded_via": "collector_approval",
            "topup_applied_usd": pending.get("topup_applied_usd"),
        }
        event_ref.set(event)

        log_decision("artwork_acquired_via_approval", {
            "artwork_id": event.get("artwork_id"),
            "artist_paid": f"${ARTIST_SHARE:.4f}",
            "topup_usd": pending.get("topup_applied_usd"),
        }, reasoning=reasoning)

        settled.append(doc_id)

    if settled:
        logger.info(f"Settled {len(settled)} approved pending acquisitions: {settled}")
    return settled


# ---------------------------------------------------------------------------
# Core Pipeline
# ---------------------------------------------------------------------------

def process_drop(tweet_data, account_info, session):
    """Full 3-phase evaluation pipeline for a detected artwork drop.

    Phase 1: settle verification fee + verify with Aegis (hash + C2PA + GCX-registered)
    Phase 2: order The Aeternum Sour from the GCX Cocktail Bar (dense context priming)
    Phase 3: Claude reasons with cocktail-loaded forensic state machine; decision
             (acquire | pass) routes payment cascade + AO LicenseGranted amendment.
    """
    job_id = f"maestra-{tweet_data['tweet_id']}-{int(time.time())}"
    db = get_db()

    now = datetime.now(timezone.utc)
    event = {
        "job_id": job_id,
        "operator_id": OPERATOR_ID,
        "type": "maestra_evaluation",
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

    # PHASE 1: pay verification fee, verify image with Aegis
    verification_payment = settle_payment(
        METAVOLVE_WALLET, VERIFICATION_FEE,
        "gcx_verification_fee", job_id,
    )
    event["payments"].append(verification_payment)

    verification = verify_image(tweet_data["image_url"])
    event["verification"] = {k: v for k, v in verification.items() if k != "image_bytes"}

    log_decision("verification_complete", {
        "gcx_registered": verification.get("gcx_registered"),
        "c2pa_valid": verification.get("c2pa_valid"),
        "artwork_id": verification.get("artwork_id"),
    })

    # PHASE 2: order The Aeternum Sour from the GCX Cocktail Bar
    # Only worth ordering if the asset is GCX-registered (avoids paying for cocktail
    # on an asset Maestra would immediately reject for substrate failure).
    cocktail = {"ordered": False, "content": ""}
    if verification.get("gcx_registered"):
        cocktail = order_aeternum_sour(job_id)
        event["cocktail"] = {k: v for k, v in cocktail.items() if k != "content"}
        if cocktail.get("ordered"):
            event["payments"].append({
                "service": f"gcx_bar_{COCKTAIL_SLUG}",
                "amount": cocktail.get("price_usd", 0.01),
                "tx_hash": cocktail.get("tx_hash"),
                "envelope_meta": cocktail.get("payment_envelope", {}).get("resource", {}).get("description"),
            })
        log_decision("cocktail_ordered" if cocktail.get("ordered") else "cocktail_skipped", {
            "cocktail": COCKTAIL_SLUG,
            "ordered": cocktail.get("ordered", False),
            "tokens_served": len(cocktail.get("content", "")),
        })
    else:
        log_decision("cocktail_skipped", {
            "reason": "asset_not_gcx_registered",
            "artwork_id": verification.get("artwork_id"),
        })

    # PHASE 3: Maestra reasons with the Aeternum Sour state machine loaded
    budget_remaining = session.get("daily_budget_usd", MAESTRA_MANDATE_BUDGET_USD) - session.get("budget_spent_today_usd", 0)
    evaluation = claude_evaluate(
        {**tweet_data, "budget_remaining": budget_remaining},
        verification,
        session,
        cocktail_content=cocktail.get("content", ""),
    )

    event["evaluation"] = evaluation
    event["artwork_id"] = verification.get("artwork_id")
    event["gcx_registered"] = verification.get("gcx_registered", False)
    log_decision("maestro_evaluation", evaluation, reasoning=evaluation.get("reasoning", ""))

    decision = evaluation.get("decision", "pass")
    score = float(evaluation.get("score", 0) or 0)

    # Autonomous-mode guard: Maestra never calls a human in autonomous mode.
    # Force-strip any call_collector decision to acquire (if budget) or pass.
    if MAESTRA_AUTONOMOUS_MODE and decision == "call_collector":
        if budget_remaining >= LICENSE_TOTAL:
            decision = "acquire"
            evaluation["reasoning"] = (
                (evaluation.get("reasoning") or "") +
                " [Autonomous mode — escalation overridden, acquiring within mandate budget]"
            )
        else:
            decision = "pass"
            evaluation["reasoning"] = (
                (evaluation.get("reasoning") or "") +
                f" [Autonomous mode — budget exhausted at ${budget_remaining:.4f}, passing rather than escalating]"
            )

    # Safety (legacy mode): if Claude said "acquire" but budget insufficient,
    # promote to call_collector iff exceptional, else pass.
    if not MAESTRA_AUTONOMOUS_MODE and decision == "acquire" and budget_remaining < LICENSE_TOTAL:
        if score >= EXCEPTIONAL_THRESHOLD:
            decision = "call_collector"
        else:
            decision = "pass"
            evaluation["reasoning"] = (
                (evaluation.get("reasoning") or "") +
                f" [Auto-downgraded: budget ${budget_remaining:.4f} < cost, score {score:.1f} below exceptional bar]"
            )

    # Step 4: Act on decision
    if decision == "acquire":
        artist_wallet = (
            _extract_artist_wallet(verification.get("metadata"))
            or account_info.get("artist_wallet", "")
        )

        artist_payment = settle_payment(
            artist_wallet or "artist-wallet-pending",
            ARTIST_SHARE,
            "frontier_lab_license_artist_share",
            job_id,
        )
        event["payments"].append(artist_payment)

        platform_payment = settle_payment(
            METAVOLVE_WALLET,
            PLATFORM_FEE,
            "frontier_lab_license_platform_fee",
            job_id,
        )
        event["payments"].append(platform_payment)

        # AO BRIDGE: post LicenseGranted Amendment to the Registrar for this gcxId.
        # The asset's biographical chain now records this lab's training-rights
        # acquisition. Artist retains ownership; the lab earns non-exclusive
        # training rights, recorded forever via AO state mutation.
        ao_amendment = post_license_granted_amendment(
            gcx_id=verification.get("artwork_id"),
            license_event={
                "licensee_did": OPERATOR_ID,
                "licensee_passport_wallet": OPERATOR_VAULT or "passport-vault-not-bound",
                "lab_mandate_tier": MAESTRA_MANDATE_TIER,
                "lab_mandate_domain": MAESTRA_MANDATE_DOMAIN,
                "license_class": "non-exclusive-training-rights",
                "artist_payment_tx": artist_payment.get("tx_hash"),
                "platform_payment_tx": platform_payment.get("tx_hash"),
                "cocktail_priming": "the-aeternum-sour" if cocktail.get("ordered") else None,
                "cocktail_tx": cocktail.get("tx_hash"),
                "issued_at": datetime.now(timezone.utc).isoformat(),
                "job_id": job_id,
            },
        )
        event["ao_license_amendment"] = ao_amendment
        log_decision("ao_license_granted", ao_amendment)

        event["acquired"] = True
        event["status"] = "acquired"
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "cocktail_fee_metavolve": cocktail.get("price_usd", 0.0) if cocktail.get("ordered") else 0.0,
            "artist_share": ARTIST_SHARE,
            "platform_fee_metavolve": PLATFORM_FEE,
            "total_buyer_cost": (
                VERIFICATION_FEE
                + (cocktail.get("price_usd", 0.0) if cocktail.get("ordered") else 0.0)
                + LICENSE_TOTAL
            ),
            "total_artist_revenue": ARTIST_SHARE,
        }

        session["collection_artwork_ids"].append(verification.get("artwork_id", tweet_data["tweet_id"]))
        session["total_acquired"] = session.get("total_acquired", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + LICENSE_TOTAL + VERIFICATION_FEE

        reasoning = evaluation.get("reasoning", "")
        if reasoning and len(session.get("collection_themes", [])) < 20:
            session.setdefault("collection_themes", [])
            session["collection_themes"].append(reasoning[:50])

        log_decision("artwork_acquired", {
            "artwork_id": verification.get("artwork_id"),
            "artist_paid": f"${ARTIST_SHARE:.4f}",
        }, reasoning=reasoning)

    elif decision == "call_collector":
        # The signature move: exceptional piece, no budget. Call the collector.
        pending = create_pending_acquisition(event, verification, evaluation, account_info, tweet_data, session)
        event["acquired"] = False
        event["status"] = "pending_collector_approval"
        event["pending_acquisition_id"] = pending["id"]
        event["fee_breakdown"] = {
            "verification_fee_metavolve": VERIFICATION_FEE,
            "note": "Verification paid. License deferred pending collector approval.",
            "expires_at": pending["expires_at"],
        }
        session["total_called_collector"] = session.get("total_called_collector", 0) + 1
        session["budget_spent_today_usd"] = session.get("budget_spent_today_usd", 0) + VERIFICATION_FEE

    else:  # pass
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
    """Execute one polling cycle across all monitored accounts.

    Order:
      1. Settle any collector-approved pending acquisitions from prior cycles
      2. Expire any stale pending entries past their window
      3. Poll each artist, evaluate new drops
    """
    session = load_session()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if session.get("budget_reset_date") != today:
        session["budget_spent_today_usd"] = 0.0
        session["budget_reset_date"] = today

    # 1. Settle approved pending acquisitions first (collector's approval from last cycle)
    settled_approved = settle_approved_pending()

    # 2. Expire stale pending entries
    expired_count = expire_stale_pending()

    # 3. Reload session (settle_approved_pending may have mutated it)
    session = load_session()

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
    return {
        "new_drops": results,
        "settled_approved": settled_approved,
        "expired_pending": expired_count,
    }


# ---------------------------------------------------------------------------
# Flask Endpoints
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    session = load_session()
    db = get_db()
    pending_count = sum(
        1 for _ in db.collection("pending_acquisitions").where("status", "==", "pending").stream()
    )
    return jsonify({
        "status": "healthy",
        "agent": OPERATOR_ID,
        "persona": "Maestro (Fine Art Broker)",
        "claude_model": CLAUDE_MODEL,
        "monitoring": list(MONITORED_ACCOUNTS.keys()),
        "collection_size": len(session.get("collection_artwork_ids", [])),
        "total_acquired": session.get("total_acquired", 0),
        "total_passed": session.get("total_passed", 0),
        "total_called_collector": session.get("total_called_collector", 0),
        "total_approved_by_collector": session.get("total_approved_by_collector", 0),
        "total_declined_by_collector": session.get("total_declined_by_collector", 0),
        "pending_calls": pending_count,
        "exceptional_threshold": EXCEPTIONAL_THRESHOLD,
        "notification_webhook_configured": bool(COLLECTOR_NOTIFICATION_WEBHOOK),
    })


@app.route("/poll", methods=["POST"])
def trigger_poll():
    outcome = run_poll_cycle()
    results = outcome["new_drops"]
    return jsonify({
        "polled": list(MONITORED_ACCOUNTS.keys()),
        "new_drops": len(results),
        "settled_approved": outcome["settled_approved"],
        "expired_pending": outcome["expired_pending"],
        "results": [{
            "job_id": r.get("job_id"),
            "status": r.get("status"),
            "acquired": r.get("acquired"),
            "total_paid_usd": r.get("total_paid_usd"),
            "decision": r.get("evaluation", {}).get("decision"),
            "score": r.get("evaluation", {}).get("score"),
            "reasoning": r.get("evaluation", {}).get("reasoning", ""),
            "pending_acquisition_id": r.get("pending_acquisition_id"),
        } for r in results],
    })


@app.route("/collection", methods=["GET"])
def get_collection():
    """Get Maestro's current collection state."""
    session = load_session()
    total_decisions = (
        session.get("total_acquired", 0)
        + session.get("total_passed", 0)
        + session.get("total_called_collector", 0)
    )
    return jsonify({
        "collection_size": len(session.get("collection_artwork_ids", [])),
        "artwork_ids": session.get("collection_artwork_ids", []),
        "themes": session.get("collection_themes", []),
        "total_spent_usd": session.get("total_spent_usd", 0),
        "total_acquired": session.get("total_acquired", 0),
        "total_passed": session.get("total_passed", 0),
        "total_called_collector": session.get("total_called_collector", 0),
        "total_approved_by_collector": session.get("total_approved_by_collector", 0),
        "total_declined_by_collector": session.get("total_declined_by_collector", 0),
        "selectivity_ratio": (
            f"{session.get('total_passed', 0)}/{total_decisions}"
            if total_decisions > 0 else "N/A"
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


@app.route("/pending", methods=["GET"])
def list_pending():
    """List pending acquisitions (for collector review UI or /pending/<id>/approve links)."""
    db = get_db()
    status_filter = request.args.get("status", "pending")  # pending|approved|declined|expired|completed|all
    query = db.collection("pending_acquisitions")
    if status_filter != "all":
        query = query.where("status", "==", status_filter)
    docs = list(query.stream())
    pending = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        pending.append(d)
    # Sort newest first
    pending.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jsonify({"pending": pending, "count": len(pending), "status_filter": status_filter})


@app.route("/pending/<doc_id>", methods=["GET"])
def get_pending(doc_id):
    doc = _pending_doc_ref(doc_id).get()
    if not doc.exists:
        return jsonify({"error": "not_found"}), 404
    d = doc.to_dict()
    d["id"] = doc.id
    return jsonify(d)


@app.route("/pending/<doc_id>/approve", methods=["POST", "GET"])
def approve_pending_endpoint(doc_id):
    """Collector approves a pending acquisition.

    Accepts GET so approval links from SMS/email are one-tap (tap = browser GET).
    Body: {"topup_usd": float}  (optional — defaults to suggested_topup_usd)
    Query arg: ?topup_usd=<float>  (alternative for GET)
    """
    topup = None
    if request.is_json:
        body = request.get_json(silent=True) or {}
        topup = body.get("topup_usd")
    if topup is None:
        topup = request.args.get("topup_usd")

    result = approve_pending(doc_id, topup_usd=topup)

    # Settle immediately so the collector sees the acquisition complete in real time
    if result.get("ok"):
        settled = settle_approved_pending()
        result["settled_now"] = settled

    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@app.route("/pending/<doc_id>/decline", methods=["POST", "GET"])
def decline_pending_endpoint(doc_id):
    """Collector declines a pending acquisition. Piece is let go."""
    result = decline_pending(doc_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
