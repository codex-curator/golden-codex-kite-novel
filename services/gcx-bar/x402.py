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
    network: str,
    asset: str,
    amount_atomic: str,
    pay_to: str,
    category: str,
    tags: list[str],
    example_input: dict[str, Any],
    example_output: dict[str, Any],
    max_timeout_seconds: int = 300,
) -> str:
    envelope = {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": url,
            "description": description,
            "mimeType": "application/json",
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": network,
                "asset": asset,
                "amount": amount_atomic,
                "payTo": pay_to,
                "maxTimeoutSeconds": max_timeout_seconds,
                "extra": {"name": "USD Coin", "version": "2"},
            }
        ],
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
    expected_amount: str,
    expected_pay_to: str,
    expected_asset: str,
    expected_network: str,
    facilitator_url: str = "",
) -> bool:
    if not facilitator_url:
        logger.warning(
            "GCX_BAR_FACILITATOR_URL unset — running in STUB MODE. "
            "Any X-Payment header passes verification. Wire a real facilitator before production."
        )
        return True

    try:
        resp = requests.post(
            f"{facilitator_url.rstrip('/')}/v2/settle",
            json={
                "x402Version": 2,
                "payment": payment_header,
                "expected": {
                    "amount": expected_amount,
                    "payTo": expected_pay_to,
                    "asset": expected_asset,
                    "network": expected_network,
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
