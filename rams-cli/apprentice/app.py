"""
Apprentice Operator -- Autonomous buyer agent for RAMS demo.
Discovers art, verifies provenance via Aegis, evaluates with mock Claude,
settles x402 payment on Kite testnet.
"""

import hashlib
import json
import os
import random
import time
import requests

# ANSI colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

WALLET = os.environ.get("WALLET_ADDRESS", "0x6fc0A8d050dAF686e93e2eb0Fa1e41f5D8DE1E1E")
CHAIN_ID = os.environ.get("KITE_CHAIN_ID", "2368")
SETTLEMENT_TOKEN = os.environ.get("SETTLEMENT_TOKEN", "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63")
FACILITATOR = os.environ.get("FACILITATOR", "https://facilitator.pieverse.io")
AEGIS_URL = os.environ.get("AEGIS_URL", "http://aegis-mock:5002")
FEED_DIR = "/feed"

# Track what we've already processed
processed_files = set()
# Accumulate receipts for batching
receipt_buffer = []
BATCH_SIZE = 3

BANNER = f"""
{BLUE}{BOLD}
    ___    ____  ____  ____  ________   ____________ _________
   /   |  / __ \\/ __ \\/ __ \\/ ____/ | / /_  __/  _/ ____/ __/
  / /| | / /_/ / /_/ / /_/ / __/ /  |/ / / /  / // /   / __/
 / ___ |/ ____/ ____/ _, _/ /___/ /|  / / / _/ // /___/ /___
/_/  |_/_/   /_/   /_/ |_/_____/_/ |_/ /_/ /___/\\____/_____/
{RESET}{DIM}  Autonomous Buyer Operator v1.0{RESET}
{DIM}  Golden Codex Protocol -- RAMS Demo{RESET}
"""

# Mock Claude evaluation responses
CLAUDE_EVALUATIONS = [
    {"verdict": "APPROVED", "quality": 0.94, "relevance": "high",
     "reasoning": "Exceptional compositional balance with rich symbolic depth."},
    {"verdict": "APPROVED", "quality": 0.91, "relevance": "high",
     "reasoning": "Strong color theory and emotional resonance. Clear provenance."},
    {"verdict": "APPROVED", "quality": 0.87, "relevance": "medium",
     "reasoning": "Technically proficient with interesting conceptual framework."},
    {"verdict": "APPROVED", "quality": 0.96, "relevance": "high",
     "reasoning": "Museum-quality execution. Rare stylistic innovation detected."},
    {"verdict": "APPROVED", "quality": 0.89, "relevance": "high",
     "reasoning": "Compelling narrative layering with sophisticated technique."},
    {"verdict": "DECLINED", "quality": 0.62, "relevance": "low",
     "reasoning": "Below quality threshold. Derivative composition detected."},
    {"verdict": "APPROVED", "quality": 0.92, "relevance": "high",
     "reasoning": "Distinctive voice. Strong collector appeal and cultural relevance."},
]


def authenticate_kite():
    """Simulate Kite Agent Passport authentication."""
    short_wallet = f"{WALLET[:6]}...{WALLET[-4:]}"
    print(f"\n{YELLOW}[Auth]{RESET} Authenticating via Kite Agent Passport...")
    time.sleep(0.8)
    print(f"{YELLOW}[Auth]{RESET} Wallet: {BOLD}{short_wallet}{RESET}")
    print(f"{YELLOW}[Auth]{RESET} Chain: Kite Testnet (ID {CHAIN_ID})")
    print(f"{YELLOW}[Auth]{RESET} Settlement Token: {SETTLEMENT_TOKEN[:10]}...{SETTLEMENT_TOKEN[-4:]}")
    time.sleep(0.5)
    passport_id = hashlib.sha256(WALLET.encode()).hexdigest()[:12]
    print(f"{GREEN}[Auth]{RESET} {BOLD}Kite Passport verified.{RESET} UID: {passport_id}")
    print(f"{GREEN}[Auth]{RESET} Agent role: {BOLD}BUYER_OPERATOR{RESET}")
    print(f"{GREEN}[Auth]{RESET} x402 payment capability: {GREEN}ENABLED{RESET}")
    print(f"{GREEN}[Auth]{RESET} Budget: $50.00 USDC (testnet)\n")
    return passport_id


def discover_new_posts() -> list:
    """Scan the shared feed directory for new artwork posts."""
    found = []
    if not os.path.exists(FEED_DIR):
        return found
    for fname in sorted(os.listdir(FEED_DIR)):
        if fname.endswith(".json") and fname not in processed_files:
            fpath = os.path.join(FEED_DIR, fname)
            try:
                with open(fpath) as f:
                    post = json.load(f)
                found.append((fname, post))
            except (json.JSONDecodeError, IOError):
                pass
    return found


def verify_with_aegis(post: dict) -> dict:
    """Call Aegis mock to verify provenance."""
    try:
        resp = requests.post(
            f"{AEGIS_URL}/verify",
            json={
                "artwork_id": post["artwork_id"],
                "source_hash": post.get("soulmark", ""),
            },
            timeout=5,
        )
        return resp.json()
    except Exception as e:
        return {"verdict": "ERROR", "error": str(e)}


def mock_claude_evaluate(post: dict) -> dict:
    """Simulate Claude Sonnet evaluation of artwork."""
    time.sleep(random.uniform(0.3, 0.8))
    # Weighted towards approval (6/7 positive)
    return random.choice(CLAUDE_EVALUATIONS)


def settle_x402_payment(post: dict) -> dict:
    """Simulate x402 payment settlement."""
    price = post.get("price_usd", 1.00)
    artist_cut = round(price * 0.85, 2)
    platform_cut = round(price * 0.13, 2)
    verify_fee = round(price * 0.02, 2)

    tx_hash = hashlib.sha256(
        f"x402:{post['artwork_id']}:{time.time()}".encode()
    ).hexdigest()[:16]

    receipt = {
        "tx_hash": f"0x{tx_hash}",
        "artwork_id": post["artwork_id"],
        "total": price,
        "artist_payment": artist_cut,
        "platform_fee": platform_cut,
        "verify_fee": verify_fee,
        "chain_id": int(CHAIN_ID),
        "settlement_token": SETTLEMENT_TOKEN,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    return receipt


def batch_receipts(receipts: list) -> dict:
    """Create a Merkle root from batched receipts."""
    leaves = [
        hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
        for r in receipts
    ]
    # Simple mock Merkle: hash all leaves together
    combined = "".join(leaves)
    merkle_root = hashlib.sha256(combined.encode()).hexdigest()[:16]

    eas_uid = hashlib.sha256(f"eas:{merkle_root}:{time.time()}".encode()).hexdigest()[:16]

    return {
        "merkle_root": f"0x{merkle_root}",
        "receipt_count": len(receipts),
        "eas_attestation": f"0x{eas_uid}",
        "chain_id": int(CHAIN_ID),
    }


def process_artwork(fname: str, post: dict):
    """Full pipeline: detect -> verify -> evaluate -> settle."""
    global receipt_buffer

    artwork_id = post["artwork_id"]
    title = post.get("title", "Untitled")
    artist = post.get("artist", "unknown")
    price = post.get("price_usd", 1.00)

    # Step 1: Detection
    print(
        f"{BLUE}[Detect]{RESET} Apprentice detected new artwork from "
        f"{BOLD}{artist}{RESET}: {BOLD}{artwork_id}{RESET}"
    )
    print(
        f'{DIM}         "{title}" -- ${price:.2f} x402 license{RESET}'
    )

    # Step 2: Verification via Aegis
    print(f"{CYAN}[Verify]{RESET} Querying Aegis provenance service...")
    verification = verify_with_aegis(post)

    if verification.get("verdict") == "VERIFIED":
        match_score = verification.get("match_score", 0)
        phash = verification.get("perceptual_hash", "?")
        print(
            f"{CYAN}[Verify]{RESET} {GREEN}Aegis: perceptual hash MATCHED.{RESET} "
            f"C2PA Soulmark {GREEN}VERIFIED{RESET}. "
            f"(score: {BOLD}{match_score}{RESET})"
        )
    else:
        print(f"{CYAN}[Verify]{RESET} {RED}Aegis: verification FAILED.{RESET} Skipping.")
        processed_files.add(fname)
        print()
        return

    # Step 3: Claude evaluation
    print(f"{YELLOW}[Evaluate]{RESET} Querying Claude Sonnet 4.6 for quality assessment...")
    evaluation = mock_claude_evaluate(post)
    verdict = evaluation["verdict"]
    quality = evaluation["quality"]
    relevance = evaluation["relevance"]
    reasoning = evaluation["reasoning"]

    if verdict == "APPROVED":
        print(
            f"{YELLOW}[Evaluate]{RESET} Claude Sonnet: {GREEN}{BOLD}APPROVED{RESET} "
            f"(quality: {BOLD}{quality}{RESET}, relevance: {BOLD}{relevance}{RESET})"
        )
        print(f"{DIM}           \"{reasoning}\"{RESET}")
    else:
        print(
            f"{YELLOW}[Evaluate]{RESET} Claude Sonnet: {RED}{BOLD}DECLINED{RESET} "
            f"(quality: {quality}, relevance: {relevance})"
        )
        print(f"{DIM}           \"{reasoning}\"{RESET}")
        processed_files.add(fname)
        print()
        return

    # Step 4: x402 Payment Settlement
    print(f"{GREEN}[Settle]{RESET} Initiating x402 payment on Kite chain {CHAIN_ID}...")
    time.sleep(random.uniform(0.2, 0.5))
    receipt = settle_x402_payment(post)

    print(
        f"{GREEN}[Settle]{RESET} {BOLD}x402 payment:{RESET} "
        f"${receipt['artist_payment']:.2f} -> artist, "
        f"${receipt['platform_fee']:.2f} -> platform, "
        f"${receipt['verify_fee']:.2f} -> verify"
    )
    print(
        f"{DIM}         tx: {receipt['tx_hash']} | "
        f"token: {SETTLEMENT_TOKEN[:10]}...{SETTLEMENT_TOKEN[-4:]}{RESET}"
    )

    receipt_buffer.append(receipt)

    # Step 5: Batch & Seal (every BATCH_SIZE receipts)
    if len(receipt_buffer) >= BATCH_SIZE:
        print(f"\n{MAGENTA}[Bundle]{RESET} {len(receipt_buffer)} receipts batched...")
        time.sleep(0.3)
        batch = batch_receipts(receipt_buffer)
        print(
            f"{MAGENTA}[Bundle]{RESET} {BOLD}{batch['receipt_count']} receipts{RESET} -> "
            f"Merkle root: {BOLD}{batch['merkle_root']}{RESET}"
        )
        print(
            f"{MAGENTA}[Seal]{RESET} EAS attestation registered on "
            f"{BOLD}Kite chain {batch['chain_id']}{RESET}: "
            f"{BOLD}{batch['eas_attestation']}{RESET}"
        )
        receipt_buffer = []

    processed_files.add(fname)
    print()


def main():
    print(BANNER)

    # Wait for artiswa to start posting
    print(f"{BLUE}[Apprentice]{RESET} Waiting for Artiswa operator to come online...")
    time.sleep(5)

    # Authenticate
    passport_id = authenticate_kite()

    print(f"{BLUE}[Apprentice]{RESET} Operator online. Scanning feed every ~8s.")
    print(f"{BLUE}[Apprentice]{RESET} Aegis endpoint: {AEGIS_URL}")
    print(f"{BLUE}[Apprentice]{RESET} Batch size: {BATCH_SIZE} receipts per Merkle bundle")
    print(f"{DIM}{'=' * 65}{RESET}\n")

    while True:
        new_posts = discover_new_posts()
        for fname, post in new_posts:
            process_artwork(fname, post)
            time.sleep(random.uniform(1, 3))

        # Poll interval
        time.sleep(random.uniform(6, 10))


if __name__ == "__main__":
    main()
