"""
x402 v2 helpers for GCX Bar.

build_payment_required_envelope(): construct the base64-encoded JSON
that goes into the `payment-required` HTTP header on a 402 response.
Shape mirrors the production examples we observed at weather.hugen.tokyo.

verify_payment_header(): forward the agent's X-Payment header to a
facilitator (Pieverse v2 or Kite-native) for settlement validation.
If GCX_BAR_FACILITATOR_URL is unset, runs in stub-mode (always passes,
logs a warning) so the scaffold is testable without a facilitator wired.
"""
from __future__ import annotations

import base64
import binascii
import json
import logging
import os
from typing import Any

import requests

logger = logging.getLogger("gcx-bar.x402")


def build_payment_required_envelope(
    *,
    url: str,
    description: str,
    accepted_payments: list[dict[str, Any]],
    pay_to: str,
    category: str,
    tags: list[str],
    example_input: dict[str, Any],
    example_output: dict[str, Any],
    max_timeout_seconds: int = 300,
) -> str:
    """
    Build an x402 v2 envelope advertising one or more chains the merchant accepts.

    `accepted_payments` is a list of dicts, each with keys `network`, `asset`, `amount`.
    The bar advertises Base (USDC, 6 decimals) and Kite chain (Kite USDT, 18 decimals)
    so an agent can settle on whichever wallet has funds — permissionless cross-chain.
    """
    accepts = [
        {
            "scheme": "exact",
            "network": p["network"],
            "asset": p["asset"],
            "amount": p["amount"],
            "payTo": pay_to,
            "maxTimeoutSeconds": max_timeout_seconds,
            "extra": p.get("extra", {"name": "USD Coin", "version": "2"}),
        }
        for p in accepted_payments
    ]
    envelope = {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": url,
            "description": description,
            "mimeType": "application/json",
        },
        "accepts": accepts,
        "extensions": {
            "bazaar": {
                "discoverable": True,
                "category": category,
                "tags": tags,
                "info": {
                    "input": example_input,
                    "output": {"type": "json", "example": example_output},
                },
                "schema": {
                    "properties": {
                        "input": {"required": ["method"]},
                    }
                },
            }
        },
    }
    raw = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def verify_payment_header(
    *,
    payment_header: str,
    accepted_payments: list[dict[str, Any]],
    expected_pay_to: str,
    facilitator_url: str = "",
) -> bool:
    """
    Validate the X-Payment header against the merchant's accepted-payment matrix.

    In stub mode (no facilitator), any header that decodes as base64 JSON and
    targets one of the accepted networks passes. The bar's pricing decision
    (Happy Hour ½-off) is governed by `kite_passport_verify`, not this gate.

    In facilitator mode, the matched accepted_payment entry's amount/asset/network
    is forwarded as the paymentRequirements to /v2/settle.
    """
    if not facilitator_url:
        logger.warning(
            "GCX_BAR_FACILITATOR_URL unset — running in STUB MODE. "
            "Any X-Payment header passes verification. Wire a real facilitator before production."
        )
        return True

    try:
        decoded = json.loads(base64.b64decode(payment_header))
    except (ValueError, binascii.Error) as e:
        logger.error(f"invalid X-Payment header: {e}")
        return False

    payment_payload = decoded.get("paymentPayload", decoded)
    payload_network = decoded.get("network") or payment_payload.get("network", "")

    # Pick the accepted_payment that matches the network the agent is settling on.
    matched = next(
        (p for p in accepted_payments if p["network"] == payload_network),
        None,
    )
    if not matched:
        logger.error(
            f"settlement network '{payload_network}' not in accepted set "
            f"{[p['network'] for p in accepted_payments]}"
        )
        return False

    try:
        resp = requests.post(
            f"{facilitator_url.rstrip('/')}/v2/settle",
            json={
                "x402Version": 2,
                "paymentPayload": payment_payload,
                "paymentRequirements": {
                    "scheme": "exact",
                    "network": matched["network"],
                    "asset": matched["asset"],
                    "amount": matched["amount"],
                    "payTo": expected_pay_to,
                    "maxTimeoutSeconds": 300,
                },
            },
            timeout=15,
        )
    except requests.RequestException as e:
        logger.error(f"facilitator request failed: {e}")
        return False

    if resp.status_code != 200:
        logger.error(f"facilitator returned {resp.status_code}: {resp.text[:200]}")
        return False

    try:
        body = resp.json()
    except ValueError:
        logger.error("facilitator returned non-JSON response")
        return False

    return bool(body.get("settled") or body.get("status") == "settled")
