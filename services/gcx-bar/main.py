"""
GCX Bar — Cognitive Nutrition pours via x402 / Kite Passport
=============================================================
Metavolve Labs - The Bar is Open.

Each "pour" is a curated dense-context bundle (10-50K tokens) for
a specific kind of work. Agents pay $0.10-$1.00 USDC per pour
(Happy Hour ½-off for verified Kite Passport holders).

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
from kite_passport_verify import verify_kite_passport, kite_passport_discount

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gcx-bar")

app = Flask(__name__)

# -- Config -----------------------------------------------------------------

PAY_TO = os.environ.get("GCX_BAR_PAY_TO", "0xFE141943a93c184606F3060103D975662327063B")

# Bar advertises both Kite mainnet (USDC.e) and Base mainnet (USDC) — both
# real money, both live. Kite Passport's two-wallet routing (agent_wallet on
# Kite → treasury_wallet on Base) lets an agent settle on whichever chain has
# funds, with the merchant accepting either. The 2026-05-17 anchor tx
# (0x5cbb738b…abc616, on-chain at kitescan.ai/tx/) was Bridged USDC on Kite
# at 0x7aB6f3ed…149e — real money, $0.01 transferred.
NETWORK = os.environ.get("GCX_BAR_NETWORK", "eip155:8453")
ASSET = os.environ.get("GCX_BAR_ASSET", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")  # USDC, Base mainnet (6 dec)

# Kite mainnet — Bridged USDC (USDC.e), 6 decimals (USDC standard).
KITE_NETWORK = os.environ.get("GCX_BAR_KITE_NETWORK", "eip155:2366")
KITE_ASSET = os.environ.get("GCX_BAR_KITE_ASSET", "0x7aB6f3ed87C42eF0aDb67Ed95090f8bF5240149e")

FACILITATOR_URL = os.environ.get("GCX_BAR_FACILITATOR_URL", "")  # Pieverse / Coinbase CDP
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
    base_price = cocktail["price_usd"]

    payment_header = request.headers.get("X-Payment") or request.headers.get("X-PAYMENT")

    # Happy Hour — verified Kite Passport holders get ½-off. The status also
    # affects what amount we'll accept as settlement (base OR discounted).
    passport_status = verify_kite_passport(payment_header)
    effective_price = (
        kite_passport_discount(base_price)
        if passport_status.is_kite_agent
        else base_price
    )

    # Bar advertises both Kite mainnet (USDC.e) and Base mainnet (USDC) —
    # both 6-decimal real USDC. Kite Passport routes whichever-chain the
    # agent's wallet is funded on (two-wallet routing is the killer feature).
    def _accepted(price: float) -> list[dict]:
        atomic = str(int(price * 1_000_000))
        return [
            {"network": KITE_NETWORK, "asset": KITE_ASSET, "amount": atomic,
             "extra": {"name": "Bridged USDC (Kite AI)", "version": "2"}},
            {"network": NETWORK, "asset": ASSET, "amount": atomic,
             "extra": {"name": "USD Coin", "version": "2"}},
        ]

    if not payment_header:
        envelope = build_payment_required_envelope(
            url=f"{SERVICE_BASE_URL}/dose?cocktail={slug}",
            description=(
                f"GCX Bar — {cocktail['name']}. {cocktail['tagline']} "
                f"{cocktail['token_budget']} dense tokens. One pour, sealed. "
                f"${base_price:.2f} base · ${kite_passport_discount(base_price):.2f} with verified Kite Passport (½-off Happy Hour)."
            ),
            accepted_payments=_accepted(base_price),
            pay_to=PAY_TO,
            category="agent-priming",
            tags=["cocktail", "cognitive-nutrition", "gcx", cocktail["category"]],
            example_input={"method": "GET", "queryParams": {"cocktail": slug}},
            example_output={"cocktail": slug, "content": "<dense-context-bundle>", "tokens": cocktail["token_budget"]},
        )
        return (
            jsonify({
                "_notice": f"Payment required (${base_price:.2f} USDC base · ${kite_passport_discount(base_price):.2f} with verified Kite Passport — ½-off Happy Hour). "
                           f"Settle on Kite mainnet 2366 (USDC.e) or Base mainnet 8453 (USDC) — both real money, Kite Passport routes either.",
            }),
            402,
            {"payment-required": envelope},
        )

    # Verify payment with facilitator (or stub if not configured).
    # Accept either the base-price or the discounted-price entry — Happy Hour status
    # determines which the caller is allowed to settle for.
    settled = verify_payment_header(
        payment_header=payment_header,
        accepted_payments=_accepted(effective_price),
        expected_pay_to=PAY_TO,
        facilitator_url=FACILITATOR_URL,
    )
    if not settled:
        return jsonify({"error": "payment verification failed"}), 402

    if passport_status.is_kite_agent:
        logger.info(
            "Happy Hour ½-off applied: signer=%s paid $%.4f (base $%.2f) — verifier=%s",
            passport_status.signer_address, effective_price, base_price, passport_status.method,
        )

    # Serve the pour
    content = get_recipe_content(slug)
    return jsonify({
        "_version": "1",
        "cocktail": slug,
        "name": cocktail["name"],
        "served_at": cocktail["token_budget"],
        "happy_hour_applied": passport_status.is_kite_agent,
        "effective_price_usd": effective_price,
        "passport_verifier": passport_status.method,
        "terms": "One pour, sealed dose, don't copy. (Social contract — not DRM.)",
        "paper": "https://doi.org/10.5281/zenodo.18667742",
        "content": content,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
