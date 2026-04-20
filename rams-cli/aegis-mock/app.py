"""
Aegis Mock -- Provenance verification service for RAMS demo.
Returns perceptual hash match + C2PA Soulmark status.
"""

import hashlib
import json
import random
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# ANSI colors
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""
{MAGENTA}{BOLD}
    ___    ___  _______________
   /   |  / _ \\/ ___/  _/ ___/
  / /| | / __/ (_ // / \\__ \\
 /_/ |_|/___/\\___/___//____/
{RESET}{DIM}  Provenance Verification Service v1.0{RESET}
{DIM}  Golden Codex Protocol -- RAMS Demo{RESET}
"""


def fake_phash(artwork_id: str) -> str:
    """Generate a deterministic fake perceptual hash."""
    h = hashlib.sha256(artwork_id.encode()).hexdigest()
    return f"ph:{h[:16]}"


def fake_c2pa_status() -> dict:
    """Return mock C2PA / Soulmark verification."""
    return {
        "c2pa_signed": True,
        "soulmark_present": True,
        "soulmark_sha256": hashlib.sha256(
            str(time.time()).encode()
        ).hexdigest()[:16],
        "issuer": "Golden Codex Protocol",
        "signing_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "aegis-mock", "version": "1.0.0"})


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True)
    artwork_id = data.get("artwork_id", "UNKNOWN")
    source_hash = data.get("source_hash", "")

    # Simulate verification delay
    time.sleep(random.uniform(0.1, 0.4))

    phash = fake_phash(artwork_id)
    match_score = round(random.uniform(0.91, 0.99), 4)
    c2pa = fake_c2pa_status()

    result = {
        "artwork_id": artwork_id,
        "perceptual_hash": phash,
        "match_score": match_score,
        "hash_matched": match_score > 0.85,
        "c2pa": c2pa,
        "verdict": "VERIFIED",
        "chain": "Kite Testnet (2368)",
    }

    print(
        f"{CYAN}[Aegis]{RESET} {GREEN}VERIFY{RESET} {artwork_id} "
        f"-- pHash {BOLD}{phash}{RESET} "
        f"-- match {BOLD}{match_score}{RESET} "
        f"-- C2PA {GREEN}SIGNED{RESET}"
    )

    return jsonify(result)


if __name__ == "__main__":
    print(BANNER)
    print(f"{CYAN}[Aegis]{RESET} Verification service listening on :5002")
    print(f"{CYAN}[Aegis]{RESET} Chain: Kite Testnet (ID 2368)")
    print(f"{CYAN}[Aegis]{RESET} Endpoint: POST /verify\n")
    app.run(host="0.0.0.0", port=5002)
