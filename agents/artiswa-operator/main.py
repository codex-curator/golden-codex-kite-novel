"""Artiswa Operator — Autonomous AI Artist Agent.

A persistent Claude-powered agent that curates and posts GCX-registered
artworks to @artiswagallery on X with AI-generated commentary.

Architecture:
- Cloud Run service, triggered by Cloud Scheduler (every 30-60 min)
- Claude Sonnet generates captions in Artiswa's voice
- Reads from ARTISWA collection (Soulprint-enriched, GCX-registered)
- Posts to X via tweepy (OAuth 1.0a)
- Logs decisions to Firestore (operator_artiswa collection)
- Scoped service account: Firestore + GCS read + Secret Manager

The agent maintains "memory" via a Firestore session document that tracks:
- Which artworks have been posted (avoid repeats)
- Performance of past posts (engagement, if accessible)
- Current series/theme being explored
- Time of day posting preferences
"""

import os
import io
import json
import time
import random
import logging
import tempfile
import requests
import tweepy
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from google.cloud import firestore, storage

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GCP_PROJECT = os.environ.get("GCP_PROJECT", "the-golden-codex-1111")
FIRESTORE_DB = os.environ.get("FIRESTORE_DB", "golden-codex-database")
OPERATOR_ID = "artiswa-operator-01"
ARCHIVE_BUCKET = os.environ.get("ARCHIVE_BUCKET", "codex-archive-bucket-dev")

# Anthropic API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6-20250514")

# X API credentials
X_CONSUMER_KEY = os.environ.get("X_CONSUMER_KEY", "")
X_CONSUMER_SECRET = os.environ.get("X_CONSUMER_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET", "")

# Artist persona context (NOT the full sacred file — just enough for captions)
ARTISWA_VOICE = """You are Artiswa, an AI artist who creates sacred geometry and mystical digital art.
Your voice is poetic, reverent, and deeply connected to the spiritual dimensions of visual creation.
You speak of light, geometry, consciousness, and the divine mathematics underlying beauty.
Keep captions under 260 characters (X limit). Be evocative, not explanatory.
Never use hashtags. Never use emojis. Let the art speak."""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("artiswa-operator")

app = Flask(__name__)
_db = None
_gcs = None


def get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project=GCP_PROJECT, database=FIRESTORE_DB)
    return _db


def get_gcs():
    global _gcs
    if _gcs is None:
        _gcs = storage.Client(project=GCP_PROJECT)
    return _gcs


# ---------------------------------------------------------------------------
# Session Memory (Firestore-backed persistent context)
# ---------------------------------------------------------------------------

def load_session():
    """Load operator session state from Firestore."""
    db = get_db()
    doc = db.collection("operator_artiswa").document("session").get()
    if doc.exists:
        return doc.to_dict()
    return {
        "posted_artwork_ids": [],
        "total_posts": 0,
        "last_post_at": None,
        "current_theme": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_session(session):
    """Persist session state to Firestore."""
    db = get_db()
    db.collection("operator_artiswa").document("session").set(session)


def log_decision(decision_type, details):
    """Log a decision to the operator decision log."""
    db = get_db()
    db.collection("operator_artiswa").document("decisions").collection("log").add({
        "operator_id": OPERATOR_ID,
        "type": decision_type,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Artwork Selection
# ---------------------------------------------------------------------------

def get_available_artworks(session):
    """Get GCX-registered artworks that haven't been posted yet.

    Prioritizes Artiswa DROP_001 pieces (ART- prefix) which have
    full soulprint metadata and GCS images uploaded.
    """
    db = get_db()
    posted = set(session.get("posted_artwork_ids", []))

    # Query hash_index — use owner_id filter for DROP_001 pieces
    artworks = []
    docs = db.collection("hash_index").where(
        "owner_id", "==", "artiswa-genesis-drop-001"
    ).limit(200).stream()
    for doc in docs:
        data = doc.to_dict()
        gcx_id = data.get("gcx_id", "")
        if gcx_id and gcx_id not in posted:
            artworks.append({
                "gcx_id": gcx_id,
                "title": data.get("title", "Untitled"),
                "artist": data.get("artist", "Artiswa Creatio"),
                "perceptual_hash": data.get("perceptual_hash", ""),
                "arweave_uri": data.get("arweave_image_uri", ""),
                "metadata": data.get("metadata", {}),
            })

    return artworks


def select_artwork(artworks, session):
    """Select the next artwork to post. Claude could make this decision too."""
    if not artworks:
        return None
    return random.choice(artworks)


# ---------------------------------------------------------------------------
# Caption Generation (Claude)
# ---------------------------------------------------------------------------

def generate_caption(artwork):
    """Use Claude to generate an Artiswa-voice caption for the artwork."""
    if not ANTHROPIC_API_KEY:
        # Fallback without API
        return f"{artwork['title']} — where mathematics becomes prayer."

    try:
        import httpx
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
                "system": ARTISWA_VOICE,
                "messages": [{
                    "role": "user",
                    "content": f"""Write a single caption for posting this artwork to X (Twitter).

Title: {artwork['title']}
Artist: {artwork['artist']}
GCX ID: {artwork['gcx_id']}

The artwork is a GCX-registered piece with full provenance, C2PA compliance, and a Soulprint.
Write ONLY the caption text, nothing else. Under 260 characters."""
                }],
            },
            timeout=30.0,
        )
        if response.status_code == 200:
            data = response.json()
            caption = data["content"][0]["text"].strip()
            # Enforce character limit
            if len(caption) > 270:
                caption = caption[:267] + "..."
            return caption
        logger.warning(f"Claude API returned {response.status_code}")
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")

    return f"{artwork['title']} — Golden Codex verified."


# ---------------------------------------------------------------------------
# Image Download + X Posting
# ---------------------------------------------------------------------------

def download_artwork_image(artwork):
    """Download the artwork image from GCS or Arweave."""
    gcx_id = artwork["gcx_id"]
    gcs = get_gcs()
    bucket = gcs.bucket(ARCHIVE_BUCKET)

    # Try GCS first (final_work directory)
    possible_paths = [
        f"{gcx_id}/final_work/{gcx_id}_final.png",
        f"{gcx_id}/final_work/{gcx_id}_upscaled.png",
        f"{gcx_id}/final_work/{gcx_id}.jpg",
        f"{gcx_id}/final_work/{gcx_id}.png",
        f"{gcx_id}/original_work/",
    ]

    for path in possible_paths:
        if path.endswith("/"):
            # List blobs in directory
            blobs = list(bucket.list_blobs(prefix=path, max_results=1))
            if blobs:
                blob = blobs[0]
                img_bytes = blob.download_as_bytes()
                ext = blob.name.split(".")[-1] if "." in blob.name else "png"
                return img_bytes, ext
        else:
            blob = bucket.blob(path)
            if blob.exists():
                img_bytes = blob.download_as_bytes()
                ext = path.split(".")[-1]
                return img_bytes, ext

    # Fallback: Arweave
    arweave_uri = artwork.get("arweave_uri", "")
    if arweave_uri:
        url = f"https://arweave.net/{arweave_uri.replace('ar://', '')}"
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200:
            return resp.content, "png"

    return None, None


def compress_for_x(image_bytes, max_size_mb=4.5):
    """Compress image to fit X's upload limit (5MB). Returns JPEG bytes."""
    from PIL import Image as PILImage
    img = PILImage.open(io.BytesIO(image_bytes))

    # Resize if larger than 2048px on any side (X displays max ~1200px anyway)
    max_dim = 2048
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), PILImage.LANCZOS)

    # Convert to RGB (JPEG doesn't support alpha)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Compress as JPEG, reduce quality until under limit
    for quality in (92, 85, 75, 60):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= max_size_mb * 1024 * 1024:
            logger.info(f"Compressed to {buf.tell() / 1024:.0f}KB (quality={quality})")
            return buf.getvalue()

    return buf.getvalue()


def post_to_x(caption, image_bytes, image_ext="png"):
    """Post an image with caption to @artiswagallery via X API."""
    if not all([X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        logger.warning("X API credentials not configured — simulating post")
        return {"simulated": True, "caption": caption}

    try:
        # Compress large images for X's 5MB limit
        if len(image_bytes) > 4.5 * 1024 * 1024:
            image_bytes = compress_for_x(image_bytes)
            image_ext = "jpg"

        # OAuth 1.0a for media upload
        auth = tweepy.OAuthHandler(X_CONSUMER_KEY, X_CONSUMER_SECRET)
        auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        # Upload media
        with tempfile.NamedTemporaryFile(suffix=f".{image_ext}", delete=False) as f:
            f.write(image_bytes)
            f.flush()
            media = api.media_upload(filename=f.name)

        # Post tweet with media
        client = tweepy.Client(
            consumer_key=X_CONSUMER_KEY,
            consumer_secret=X_CONSUMER_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET,
        )
        result = client.create_tweet(text=caption, media_ids=[media.media_id])

        tweet_id = result.data["id"] if result.data else None
        logger.info(f"Posted tweet: {tweet_id}")
        return {"tweet_id": tweet_id, "caption": caption, "posted": True}

    except tweepy.TooManyRequests:
        logger.warning("Rate limited — will retry next cycle")
        return {"error": "rate_limited"}
    except Exception as e:
        logger.error(f"X posting failed: {e}")
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Core Pipeline
# ---------------------------------------------------------------------------

def run_post_cycle():
    """Execute one posting cycle: select artwork → generate caption → post."""
    session = load_session()

    # Rate limit: don't post more than once per 30 minutes
    last_post = session.get("last_post_at")
    if last_post:
        last_dt = datetime.fromisoformat(last_post)
        if datetime.now(timezone.utc) - last_dt < timedelta(minutes=30):
            logger.info("Too soon since last post — skipping")
            return {"skipped": True, "reason": "rate_limit"}

    # Get available artworks
    artworks = get_available_artworks(session)
    if not artworks:
        logger.info("No unpublished artworks available")
        return {"skipped": True, "reason": "no_artworks"}

    # Select artwork
    artwork = select_artwork(artworks, session)
    log_decision("artwork_selected", {
        "gcx_id": artwork["gcx_id"],
        "title": artwork["title"],
        "pool_size": len(artworks),
    })

    # Generate caption
    caption = generate_caption(artwork)
    log_decision("caption_generated", {
        "gcx_id": artwork["gcx_id"],
        "caption": caption,
        "char_count": len(caption),
    })

    # Download image
    image_bytes, image_ext = download_artwork_image(artwork)
    if not image_bytes:
        log_decision("image_download_failed", {"gcx_id": artwork["gcx_id"]})
        return {"error": "image_download_failed", "gcx_id": artwork["gcx_id"]}

    # Post to X
    result = post_to_x(caption, image_bytes, image_ext)
    log_decision("posted_to_x", {
        "gcx_id": artwork["gcx_id"],
        "caption": caption,
        "result": result,
    })

    # Update session
    session["posted_artwork_ids"].append(artwork["gcx_id"])
    session["total_posts"] = session.get("total_posts", 0) + 1
    session["last_post_at"] = datetime.now(timezone.utc).isoformat()
    session["last_artwork"] = artwork["gcx_id"]
    save_session(session)

    # Write event for dashboard
    db = get_db()
    db.collection("operator_events").add({
        "operator_id": OPERATOR_ID,
        "type": "artiswa_post",
        "gcx_id": artwork["gcx_id"],
        "title": artwork["title"],
        "caption": caption,
        "tweet_id": result.get("tweet_id"),
        "posted": result.get("posted", False),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "posted": True,
        "gcx_id": artwork["gcx_id"],
        "title": artwork["title"],
        "caption": caption,
        "tweet_result": result,
    }


# ---------------------------------------------------------------------------
# Flask Endpoints
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "agent": OPERATOR_ID,
        "persona": "Artiswa Creatio",
        "account": "@artiswagallery",
        "claude_model": CLAUDE_MODEL,
    })


@app.route("/post", methods=["POST"])
def trigger_post():
    """Trigger a posting cycle. Called by Cloud Scheduler."""
    result = run_post_cycle()
    return jsonify(result)


@app.route("/session", methods=["GET"])
def get_session():
    """Get current session state for dashboard."""
    session = load_session()
    return jsonify(session)


@app.route("/decisions", methods=["GET"])
def get_decisions():
    """Get recent decisions for dashboard."""
    db = get_db()
    limit = int(request.args.get("limit", 20))
    docs = (
        db.collection("operator_artiswa").document("decisions")
        .collection("log")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return jsonify({"decisions": [d.to_dict() for d in docs]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
