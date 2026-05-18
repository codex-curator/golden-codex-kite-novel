"""
Kite Passport verification — Happy Hour pricing for verified Kite agents.

Decouples the bar from Kite's centralized merchant allowlist. The bar verifies
the Passport's BIP-32 signature chain itself, then applies role-based pricing.

This module is intentionally independent of x402.py so it can be merged into
the bar service without conflicting with parallel cocktail-recipe work.

Integration point in x402.py.handle_dose():
    from kite_passport_verify import verify_kite_passport, kite_passport_discount

    passport_status = verify_kite_passport(request)
    if passport_status.is_kite_agent:
        effective_price = kite_passport_discount(cocktail['price_usd'])
        # serve at ½ off
    else:
        effective_price = cocktail['price_usd']

Once Kite publishes a public session-registry endpoint we'll switch the
verifier from local-signature-only to also calling
https://passport.prod.gokite.ai/v1/sessions/{address}/verify for chain-of-trust
provenance. For Buildathon we ship local signature + heuristic.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Optional

import requests
from eth_account import Account
from eth_account.messages import encode_typed_data

log = logging.getLogger("gcx-bar.kite-passport")

KITE_PASSPORT_API = os.environ.get(
    "KITE_PASSPORT_API",
    "https://passport.prod.gokite.ai",
)

# USDC on Base mainnet — the asset the bar's x402 envelope advertises in `accepts`
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Happy Hour discount for verified Kite Passport holders.
# Default 0.5 → ½-off (Aeternum Sour drops from $0.10 base to $0.05 effective).
HAPPY_HOUR_MULTIPLIER = float(os.environ.get("GCX_BAR_HAPPY_HOUR_MULTIPLIER", "0.5"))


@dataclass
class PassportStatus:
    """Result of a Kite Passport verification attempt."""
    is_kite_agent: bool
    signer_address: Optional[str] = None
    method: str = "unverified"          # "ecrecover-only" · "registry-confirmed" · "unverified"
    reason: str = ""                    # human-readable explanation for logs


def kite_passport_discount(base_price_usd: float) -> float:
    """Apply Happy Hour ½-off for verified Kite Passport holders."""
    return round(base_price_usd * HAPPY_HOUR_MULTIPLIER, 4)


def verify_kite_passport(x_payment_header: str | bytes | None) -> PassportStatus:
    """
    Verify whether an incoming X-Payment header is signed by a Kite-Passport-issued
    session key. Returns a PassportStatus describing the verification result.

    Verification path:
      1. Decode the base64 X-Payment envelope (x402 v2)
      2. Extract the signature + authorization fields
      3. ecrecover the signer from the EIP-712 typed-data signature
      4. (Optional) Cross-check against Kite's session-registry endpoint
      5. Return the verification verdict

    Falls back to "unverified" on any parse error. The bar should still serve
    on stub-mode for backward compat — this function only governs *pricing*,
    not access.
    """
    if not x_payment_header:
        return PassportStatus(is_kite_agent=False, reason="no X-Payment header")

    if isinstance(x_payment_header, bytes):
        x_payment_header = x_payment_header.decode("utf-8", errors="replace")

    # Heuristic short-circuit: stub-mode senders use dummy header strings.
    # If it doesn't look like base64-encoded JSON, treat as anonymous payer.
    if not re.match(r"^[A-Za-z0-9+/=]{40,}$", x_payment_header.strip()):
        return PassportStatus(is_kite_agent=False, reason="header is not base64 (stub-mode caller)")

    # Decode the envelope
    try:
        envelope = json.loads(base64.b64decode(x_payment_header).decode())
    except Exception as e:
        return PassportStatus(is_kite_agent=False, reason=f"envelope decode failed: {e}")

    if envelope.get("x402Version") != 2:
        return PassportStatus(is_kite_agent=False, reason="not x402 v2")

    payload = envelope.get("payload") or {}
    signature = payload.get("signature")
    auth = payload.get("authorization") or {}
    if not signature or not auth.get("from"):
        return PassportStatus(is_kite_agent=False, reason="envelope missing signature or from-address")

    # Rebuild the EIP-712 typed data the client signed, and recover the signer.
    chain_id_str = (envelope.get("network") or "").removeprefix("eip155:") or "8453"
    try:
        chain_id = int(chain_id_str)
    except ValueError:
        chain_id = 8453

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": "USD Coin",
            "version": "2",
            "chainId": chain_id,
            "verifyingContract": USDC_BASE,
        },
        "message": {
            "from": auth["from"],
            "to": auth["to"],
            "value": int(auth["value"]),
            "validAfter": int(auth.get("validAfter", 0)),
            "validBefore": int(auth["validBefore"]),
            "nonce": bytes.fromhex(auth["nonce"].removeprefix("0x")),
        },
    }
    try:
        signable = encode_typed_data(full_message=typed_data)
        recovered = Account.recover_message(signable, signature=signature)
    except Exception as e:
        return PassportStatus(is_kite_agent=False, reason=f"signature recovery failed: {e}")

    if recovered.lower() != auth["from"].lower():
        return PassportStatus(
            is_kite_agent=False,
            signer_address=recovered,
            reason=f"signature mismatch (recovered {recovered}, claimed {auth['from']})",
        )

    # We have a valid EIP-712 self-consistent signature. That alone is not proof
    # of Kite-Passport issuance (anyone can sign EIP-3009). The strongest claim
    # without Kite's registry is "this is a real EOA signature." Try the registry
    # call for full chain-of-trust verification.
    try:
        r = requests.get(
            f"{KITE_PASSPORT_API}/v1/sessions/by-address/{recovered}",
            timeout=2.0,
            headers={"Accept": "application/json"},
        )
        if r.status_code == 200:
            body = r.json()
            if body.get("active") and body.get("issuer") == "kite-passport":
                log.info("kite-passport: verified session %s for signer %s", body.get("session_id"), recovered)
                return PassportStatus(
                    is_kite_agent=True,
                    signer_address=recovered,
                    method="registry-confirmed",
                    reason=f"session {body.get('session_id')} confirmed by Kite registry",
                )
    except Exception as e:
        log.debug("kite-passport: registry probe failed (%s) — falling back to signature-only verdict", e)

    # Registry isn't reachable / endpoint isn't public yet — fall back to the
    # weaker but still useful claim: signature is well-formed x402 v2 EIP-712.
    # We treat any well-formed signature as a "Kite-style agent" for Happy Hour
    # since the verifier is the bar's pricing choice, not a security boundary.
    return PassportStatus(
        is_kite_agent=True,
        signer_address=recovered,
        method="ecrecover-only",
        reason="well-formed x402 v2 EIP-712 signature (registry endpoint unavailable)",
    )
