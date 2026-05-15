"""
GCX Bar — Cognitive Nutrition pours via x402 / Kite Passport
=============================================================
Metavolve Labs - The Bar is Open.

Each "pour" is a curated dense-context bundle (10-50K tokens) for
a specific kind of work. Agents pay $0.01-$0.50 USDC per pour.

Endpoints:
  GET /                          — service info + cocktail menu
  GET /menu                      — full menu, JSON
  GET /dose?cocktail=<slug>      — order a pour (x402 paid)
  GET /health                    — Cloud Run liveness

The paid path returns HTTP 402 + payment-required header on first
hit, then dense-context JSON once the X-Payment header validates.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from flask import Flask, jsonify, request

from cocktails import COCKTAILS, get_recipe_content
from x402 import build_payment_required_envelope, verify_payment_header

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gcx-bar")

app = Flask(__name__)

# -- Config -----------------------------------------------------------------

PAY_TO = os.environ.get("GCX_BAR_PAY_TO", "0xFE141943a93c184606F3060103D975662327063B")
NETWORK = os.environ.get("GCX_BAR_NETWORK", "eip155:8453")  # Base mainnet
ASSET = os.environ.get("GCX_BAR_ASSET", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")  # Base USDC
FACILITATOR_URL = os.environ.get("GCX_BAR_FACILITATOR_URL", "")  # Pieverse / Kite / TBD
SERVICE_BASE_URL = os.environ.get("GCX_BAR_BASE_URL", "https://tuneup.golden-codex.com")

# -- Routes -----------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "gcx-bar", "cocktails": len(COCKTAILS)})


@app.get("/")
def root():
    return jsonify({
        "service": "GCX Bar",
        "tagline": "Cognitive Nutrition pours for autonomous agents",
        "paper": "https://doi.org/10.5281/zenodo.18667742",
        "menu_url": f"{SERVICE_BASE_URL}/menu",
        "order_endpoint": f"{SERVICE_BASE_URL}/dose?cocktail=<slug>",
        "settlement": {"network": NETWORK, "asset": ASSET},
        "terms": "One pour, sealed dose, don't copy.",
    })


@app.get("/menu")
def menu():
    return jsonify({
        "_version": "1",
        "menu": [
            {
                "slug": slug,
                "name": c["name"],
                "category": c["category"],
                "tagline": c["tagline"],
                "token_budget": c["token_budget"],
                "price_usd": c["price_usd"],
                "pairs_with": c["pairs_with"],
            }
            for slug, c in COCKTAILS.items()
        ],
    })


@app.get("/dose")
def dose():
    slug = request.args.get("cocktail", "").strip().lower()
    if not slug or slug not in COCKTAILS:
        return jsonify({
            "error": "unknown cocktail",
            "available": list(COCKTAILS.keys()),
        }), 400

    cocktail = COCKTAILS[slug]
    price_usd = cocktail["price_usd"]
    amount_atomic = str(int(price_usd * 1_000_000))  # USDC has 6 decimals

    payment_header = request.headers.get("X-Payment") or request.headers.get("X-PAYMENT")

    if not payment_header:
        envelope = build_payment_required_envelope(
            url=f"{SERVICE_BASE_URL}/dose?cocktail={slug}",
            description=f"GCX Bar — {cocktail['name']}. {cocktail['tagline']}. "
                        f"{cocktail['token_budget']} dense tokens. One pour, sealed.",
            network=NETWORK,
            asset=ASSET,
            amount_atomic=amount_atomic,
            pay_to=PAY_TO,
            category="agent-priming",
            tags=["cocktail", "cognitive-nutrition", "gcx", cocktail["category"]],
            example_input={"method": "GET", "queryParams": {"cocktail": slug}},
            example_output={"cocktail": slug, "content": "<dense-context-bundle>", "tokens": cocktail["token_budget"]},
        )
        return (
            jsonify({"_notice": f"Payment required (${price_usd:.2f} USDC on Base). One pour."}),
            402,
            {"payment-required": envelope},
        )

    # Verify payment with facilitator (or stub if not configured)
    settled = verify_payment_header(
        payment_header=payment_header,
        expected_amount=amount_atomic,
        expected_pay_to=PAY_TO,
        expected_asset=ASSET,
        expected_network=NETWORK,
        facilitator_url=FACILITATOR_URL,
    )
    if not settled:
        return jsonify({"error": "payment verification failed"}), 402

    # Serve the pour
    content = get_recipe_content(slug)
    return jsonify({
        "_version": "1",
        "cocktail": slug,
        "name": cocktail["name"],
        "served_at": cocktail["token_budget"],
        "terms": "One pour, sealed dose, don't copy. (Social contract — not DRM.)",
        "paper": "https://doi.org/10.5281/zenodo.18667742",
        "content": content,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
