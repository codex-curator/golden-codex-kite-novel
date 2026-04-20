"""
Artiswa Operator -- Autonomous artist agent for RAMS demo.
Posts simulated art to a shared feed every ~15 seconds.
"""

import hashlib
import json
import os
import random
import time

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

WALLET = os.environ.get("WALLET_ADDRESS", "0xFE141943a93c184606F3060103D975662327063B")
CHAIN_ID = os.environ.get("KITE_CHAIN_ID", "2368")
SETTLEMENT_TOKEN = os.environ.get("SETTLEMENT_TOKEN", "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63")
FACILITATOR = os.environ.get("FACILITATOR", "https://facilitator.pieverse.io")
FEED_DIR = "/feed"

# Curated artwork catalog (real titles from the Artiswa collection)
ARTWORKS = [
    ("ARTISWA-0089", "Sovereign Flame Ascending", "oil-on-canvas, celestial, 4096x4096"),
    ("ARTISWA-0042", "Cathedral of Forgotten Waves", "digital-mixed, oceanic, 4096x4096"),
    ("ARTISWA-0055", "The Dreaming Codex", "watercolor-fusion, mystical, 4096x4096"),
    ("ARTISWA-0071", "Luminous Thread Unraveling", "generative-abstract, fiber, 4096x4096"),
    ("ARTISWA-0023", "Echoes in the Glass Garden", "photo-composite, botanical, 4096x4096"),
    ("ARTISWA-0097", "Gravity's Last Embrace", "charcoal-digital, cosmic, 4096x4096"),
    ("ARTISWA-0108", "Whispers of the Iron Tree", "mixed-media, arboreal, 4096x4096"),
    ("ARTISWA-0034", "Meridian of Stillness", "ink-wash, meditative, 4096x4096"),
    ("ARTISWA-0061", "Portrait of an Unborn Star", "oil-digital, astral, 4096x4096"),
    ("ARTISWA-0115", "The Weight of Light", "acrylic-generative, luminous, 4096x4096"),
    ("ARTISWA-0003", "Fractured Horizon", "digital-collage, landscape, 4096x4096"),
    ("ARTISWA-0079", "Silk Roads of Memory", "textile-digital, cultural, 4096x4096"),
    ("ARTISWA-0126", "Anthem for the Quiet Ones", "pastel-ai, figurative, 4096x4096"),
    ("ARTISWA-0018", "Dissolving into Birdsong", "watercolor-gen, nature, 4096x4096"),
    ("ARTISWA-0091", "Architecture of Longing", "3d-render, emotional, 4096x4096"),
]

BANNER = f"""
{MAGENTA}{BOLD}
    ___    ____  ____________________       ___
   /   |  / __ \\/_  __/  _/ ___/ |     / /   |
  / /| | / /_/ / / /  / / \\__ \\| | /| / / /| |
 / ___ |/ _, _/ / / _/ / ___/ /| |/ |/ / ___ |
/_/  |_/_/ |_| /_/ /___//____/ |__/|__/_/  |_|
{RESET}{DIM}  Autonomous Artist Operator v1.0{RESET}
{DIM}  Golden Codex Protocol -- RAMS Demo{RESET}
"""


def generate_soulmark(artwork_id: str) -> str:
    return hashlib.sha256(f"soulmark:{artwork_id}:{time.time()}".encode()).hexdigest()[:16]


def authenticate_kite():
    """Simulate Kite Agent Passport authentication."""
    short_wallet = f"{WALLET[:6]}...{WALLET[-4:]}"
    print(f"\n{YELLOW}[Auth]{RESET} Authenticating via Kite Agent Passport...")
    time.sleep(0.8)
    print(f"{YELLOW}[Auth]{RESET} Wallet: {BOLD}{short_wallet}{RESET}")
    print(f"{YELLOW}[Auth]{RESET} Chain: Kite Testnet (ID {CHAIN_ID})")
    print(f"{YELLOW}[Auth]{RESET} Settlement Token: {SETTLEMENT_TOKEN[:10]}...{SETTLEMENT_TOKEN[-4:]}")
    print(f"{YELLOW}[Auth]{RESET} Facilitator: {FACILITATOR}")
    time.sleep(0.5)
    passport_id = hashlib.sha256(WALLET.encode()).hexdigest()[:12]
    print(f"{GREEN}[Auth]{RESET} {BOLD}Kite Passport verified.{RESET} UID: {passport_id}")
    print(f"{GREEN}[Auth]{RESET} Agent role: {BOLD}ARTIST_OPERATOR{RESET}")
    print(f"{GREEN}[Auth]{RESET} x402 payment capability: {GREEN}ENABLED{RESET}")
    print(f"{GREEN}[Auth]{RESET} Revenue split: 85% artist / 15% platform\n")
    return passport_id


def post_artwork(idx: int) -> dict:
    """Simulate posting an artwork to the feed."""
    artwork_id, title, medium = ARTWORKS[idx % len(ARTWORKS)]
    soulmark = generate_soulmark(artwork_id)
    price = round(random.uniform(0.50, 2.50), 2)

    post = {
        "artwork_id": artwork_id,
        "title": title,
        "medium": medium,
        "artist": "@artiswagallery",
        "soulmark": soulmark,
        "price_usd": price,
        "license": "x402-commercial",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "chain_id": int(CHAIN_ID),
        "settlement_token": SETTLEMENT_TOKEN,
    }

    # Write to shared feed volume
    os.makedirs(FEED_DIR, exist_ok=True)
    feed_file = os.path.join(FEED_DIR, f"{artwork_id}_{int(time.time())}.json")
    with open(feed_file, "w") as f:
        json.dump(post, f)

    print(
        f"{MAGENTA}[Post]{RESET} {BOLD}{artwork_id}{RESET} "
        f'"{WHITE}{title}{RESET}" '
        f"-- ${price:.2f} x402"
    )
    print(
        f"{DIM}       medium: {medium} | soulmark: {soulmark} | "
        f"license: x402-commercial{RESET}"
    )

    return post


def main():
    print(BANNER)

    # Authenticate
    passport_id = authenticate_kite()

    print(f"{MAGENTA}[Artiswa]{RESET} Operator online. Posting art every ~15s.")
    print(f"{MAGENTA}[Artiswa]{RESET} Feed directory: {FEED_DIR}")
    print(f"{DIM}{'=' * 65}{RESET}\n")

    idx = 0
    while True:
        post_artwork(idx)
        idx += 1
        # Wait 12-18 seconds between posts
        wait = random.uniform(12, 18)
        print(f"{DIM}       next post in {wait:.0f}s...{RESET}\n")
        time.sleep(wait)


if __name__ == "__main__":
    main()
