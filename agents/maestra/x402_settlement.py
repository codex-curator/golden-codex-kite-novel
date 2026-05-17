"""
Chain-Agnostic x402 Settlement Module

Supports Base L2 (production, Coinbase CDP facilitator) and Kite (testnet, Pieverse).
Switch chains via X402_NETWORK environment variable:
  - "base"  → Base L2 mainnet, USDC, Coinbase CDP (DEFAULT — production-ready)
  - "kite"  → Kite Ozone testnet, Test USDT, Pieverse facilitator

Settlement flow:
  1. Build EIP-712 typed-data TransferWithAuthorization
  2. Sign with the agent's ephemeral session key (Kite Passport pattern)
  3. Base64-encode the signed envelope as the x402 v2 payment_token (X-Payment header)
  4. Forward unsigned JSON to the facilitator's /v2/settle for on-chain settlement
  5. Return both the payment_token (signed envelope) and tx_hash in the record

Permissionless-merchant pattern: the bar verifies the signed envelope itself via
ecrecover — no Kite catalog allowlist needed. The session key can be supplied via
KITE_SESSION_PRIVATE_KEY env var; otherwise an ephemeral key is generated at module
load and logged for the run.

When Kite mainnet launches with funded wallets, switch with:
  X402_NETWORK=kite
  X402_FACILITATOR_URL=https://facilitator.pieverse.io
  X402_SETTLEMENT_TOKEN=<kite_mainnet_usdc>
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone

import requests
from eth_account import Account
from eth_account.messages import encode_typed_data

logger = logging.getLogger("x402_settlement")

# ---------------------------------------------------------------------------
# Ephemeral Session Signer (Kite Passport pattern)
# ---------------------------------------------------------------------------
# In production, Kite Passport derives a BIP-32 ephemeral session key from the
# delegated agent key. For Buildathon shipping, we either:
#   1. Use a provided KITE_SESSION_PRIVATE_KEY (deterministic, reproducible), OR
#   2. Generate a fresh ephemeral key on module load (per-run rotation).
# The signature is real EIP-712 either way — the bar's kite_passport_verify
# ecrecovers a valid signer address and applies Happy Hour.

_session_pk = os.environ.get("KITE_SESSION_PRIVATE_KEY", "").strip()
if _session_pk and not _session_pk.startswith("0x"):
    _session_pk = "0x" + _session_pk
if not _session_pk or len(_session_pk) != 66:
    _session_pk = "0x" + secrets.token_hex(32)
    logger.info(
        "KITE_SESSION_PRIVATE_KEY unset — generated ephemeral session key for this run."
    )
else:
    logger.info("Using deterministic KITE_SESSION_PRIVATE_KEY from env.")

_SESSION_ACCOUNT = Account.from_key(_session_pk)
SESSION_SIGNER_ADDRESS = _SESSION_ACCOUNT.address
logger.info("Maestra ephemeral session signer: %s", SESSION_SIGNER_ADDRESS)

# ---------------------------------------------------------------------------
# Network Configuration
# ---------------------------------------------------------------------------

NETWORK_CONFIGS = {
    "base": {
        "chain_id": 8453,
        "chain_label": "base-mainnet",
        "rpc_url": "https://mainnet.base.org",
        "explorer_url": "https://basescan.org",
        "settlement_token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC (6 decimals)
        "facilitator_url": "https://x402.org/facilitator",
        "decimals": 6,
        "scheme": "exact",
        "network_id": "eip155:8453",
    },
    "kite": {
        "chain_id": 2366,
        "chain_label": "kite-chain",
        "rpc_url": "https://rpc-testnet.gokite.ai/",
        "explorer_url": "https://testnet.kitescan.ai",
        "settlement_token": "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63",  # USDT (18 decimals)
        "facilitator_url": "https://facilitator.pieverse.io",
        "decimals": 18,
        "scheme": "exact",  # Pieverse v2 uses "exact" (gokite-aa is the AA SDK, not the x402 scheme)
        "network_id": "eip155:2366",
    },
}

# Active network — switch with a single env var
X402_NETWORK = os.environ.get("X402_NETWORK", "base")
X402_FACILITATOR_URL = os.environ.get("X402_FACILITATOR_URL", "")
X402_SETTLEMENT_TOKEN = os.environ.get("X402_SETTLEMENT_TOKEN", "")


def get_network_config():
    """Get active network configuration with env var overrides."""
    config = NETWORK_CONFIGS.get(X402_NETWORK, NETWORK_CONFIGS["base"]).copy()
    if X402_FACILITATOR_URL:
        config["facilitator_url"] = X402_FACILITATOR_URL
    if X402_SETTLEMENT_TOKEN:
        config["settlement_token"] = X402_SETTLEMENT_TOKEN
    return config


# ---------------------------------------------------------------------------
# EIP-712 envelope builder
# ---------------------------------------------------------------------------

def build_signed_x402_envelope(
    *,
    network_config: dict,
    to_address: str,
    amount_atomic: str,
    valid_seconds: int = 300,
) -> tuple[str, dict]:
    """
    Build + EIP-712-sign an x402 v2 TransferWithAuthorization envelope.

    Returns (base64_envelope, decoded_envelope) so callers can both forward
    the header AND log/inspect the decoded payload.

    The signer is the Maestra ephemeral session key (Kite Passport-style).
    The bar's kite_passport_verify ecrecovers this signature and applies
    Happy Hour pricing — no Kite catalog allowlist needed (permissionless
    merchant pattern).
    """
    now = int(time.time())
    nonce_bytes = secrets.token_bytes(32)
    nonce_hex = "0x" + nonce_bytes.hex()

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
            "chainId": network_config["chain_id"],
            "verifyingContract": network_config["settlement_token"],
        },
        "message": {
            "from": SESSION_SIGNER_ADDRESS,
            "to": to_address,
            "value": int(amount_atomic),
            "validAfter": 0,
            "validBefore": now + valid_seconds,
            "nonce": nonce_bytes,
        },
    }

    signable = encode_typed_data(full_message=typed_data)
    signed = _SESSION_ACCOUNT.sign_message(signable)
    sig_hex = signed.signature.hex()
    if not sig_hex.startswith("0x"):
        sig_hex = "0x" + sig_hex

    envelope = {
        "x402Version": 2,
        "network": network_config["network_id"],
        "payload": {
            "signature": sig_hex,
            "authorization": {
                "from": SESSION_SIGNER_ADDRESS,
                "to": to_address,
                "value": amount_atomic,
                "validAfter": "0",
                "validBefore": str(now + valid_seconds),
                "nonce": nonce_hex,
            },
        },
    }
    raw = json.dumps(envelope, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii"), envelope


# ---------------------------------------------------------------------------
# Settlement
# ---------------------------------------------------------------------------

def settle_payment(
    from_address: str,
    to_address: str,
    amount_usd: float,
    service: str,
    job_id: str,
) -> dict:
    """Settle an x402 payment on the active network.

    Returns a payment record dict with:
      - status: "settled", "simulated", or "settlement_error"
      - tx_hash: on-chain tx hash or simulated hash
      - chain: network label
      - amount_usd: payment amount
      - explorer_url: link to transaction (if settled)
    """
    net = get_network_config()
    amount_atomic = str(int(amount_usd * (10 ** net["decimals"])))

    # Always build a signed EIP-712 envelope. This is the bar's payment_token —
    # the bar's kite_passport_verify ecrecovers the signer and applies Happy Hour.
    # The signed envelope works regardless of whether facilitator settlement succeeds.
    try:
        payment_token, decoded_envelope = build_signed_x402_envelope(
            network_config=net,
            to_address=to_address,
            amount_atomic=amount_atomic,
        )
        logger.info(
            "Signed x402 v2 envelope: signer=%s amount=%s atomic on %s (job_id=%s)",
            SESSION_SIGNER_ADDRESS, amount_atomic, net["network_id"], job_id,
        )
    except Exception as e:
        logger.error("Failed to build signed envelope: %s", e)
        payment_token = ""
        decoded_envelope = {}

    record = {
        "from": SESSION_SIGNER_ADDRESS,  # The EIP-712 signer — what bar ecrecovers
        "from_vault": from_address or "unset",  # The original treasury/operator vault
        "to": to_address,
        "amount_usd": amount_usd,
        "amount_atomic": amount_atomic,
        "service": service,
        "job_id": job_id,
        "chain": net["chain_label"],
        "chain_id": net["chain_id"],
        "network": X402_NETWORK,
        "settlement_token": net["settlement_token"],
        "facilitator": net["facilitator_url"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "simulated",
        "tx_hash": _simulated_hash(job_id, amount_usd),
        "payment_token": payment_token,  # ★ base64 EIP-712 envelope — for X-Payment header
        "envelope_decoded": decoded_envelope,  # Decoded form for ledger logging
        "signer_address": SESSION_SIGNER_ADDRESS,
        "signing_method": "eip712-ephemeral-session-key",
    }

    # Only attempt facilitator settlement if we have a vault/wallet address.
    # The signed envelope above is sufficient for the bar to accept payment
    # (permissionless merchant pattern); facilitator settlement is the optional
    # on-chain finality leg.
    if not from_address:
        logger.info("No vault configured — payment_token built, skipping facilitator. signer=%s",
                    SESSION_SIGNER_ADDRESS)
        return record

    try:
        # Forward the signed envelope to the facilitator's /v2/settle.
        endpoint = f"{net['facilitator_url']}/v2/settle"
        payload = {
            "x402Version": 2,
            "paymentPayload": decoded_envelope.get("payload", {
                "from": from_address,
                "to": to_address,
                "amount": amount_atomic,
            }),
            "paymentRequirements": {
                "scheme": net["scheme"],
                "network": net["network_id"],
                "asset": net["settlement_token"],
                "amount": amount_atomic,
                "payTo": to_address,
                "maxTimeoutSeconds": 300,
            },
        }
        resp = requests.post(endpoint, json=payload, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            tx_hash = _extract_tx_hash(result)
            if tx_hash:
                record["status"] = "settled"
                record["tx_hash"] = tx_hash
                record["explorer_url"] = f"{net['explorer_url']}/tx/{tx_hash}"
                logger.info(
                    "x402 settled on %s: $%.3f → %s tx=%s",
                    net["chain_label"], amount_usd, to_address[:10], tx_hash[:18],
                )
        else:
            record["status"] = "settlement_error"
            record["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
            logger.warning("x402 settlement failed: %s", record["error"])

    except Exception as e:
        record["status"] = "settlement_error"
        record["error"] = str(e)
        logger.warning("x402 settlement exception: %s", e)

    return record


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simulated_hash(job_id: str, amount: float) -> str:
    """Generate a deterministic simulated tx hash."""
    return "0x" + hashlib.sha256(
        f"{job_id}-{amount}-{time.time()}".encode()
    ).hexdigest()


def _extract_tx_hash(result) -> str:
    """Extract tx hash from various facilitator response formats."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        # Coinbase CDP: {"success": true, "transaction": {"txHash": "0x..."}}
        tx = result.get("transaction", result.get("txHash", ""))
        if isinstance(tx, dict):
            return tx.get("txHash", "")
        if isinstance(tx, str):
            return tx
        # Pieverse: {"transactionHash": "0x..."}
        return result.get("transactionHash", "")
    return ""


def get_settlement_info() -> dict:
    """Return current settlement configuration for health endpoints."""
    net = get_network_config()
    return {
        "network": X402_NETWORK,
        "chain_id": net["chain_id"],
        "chain_label": net["chain_label"],
        "facilitator": net["facilitator_url"],
        "settlement_token": net["settlement_token"],
        "scheme": net["scheme"],
        "explorer": net["explorer_url"],
    }
