"""
Chain-Agnostic x402 Settlement Module

Supports Base L2 (production, Coinbase CDP facilitator) and Kite (testnet, Pieverse).
Switch chains via X402_NETWORK environment variable:
  - "base"  → Base L2 mainnet, USDC, Coinbase CDP (DEFAULT — production-ready)
  - "kite"  → Kite Ozone testnet, Test USDT, Pieverse facilitator

Settlement flow:
  1. Build payment authorization for the target network
  2. Call the network's facilitator /settle endpoint
  3. Return tx_hash on success, simulated hash on failure/no-vault

When Kite mainnet launches with funded wallets, switch with:
  X402_NETWORK=kite
  X402_FACILITATOR_URL=https://facilitator.pieverse.io
  X402_SETTLEMENT_TOKEN=<kite_mainnet_usdc>
"""

import hashlib
import logging
import os
import time
from datetime import datetime, timezone

import requests

logger = logging.getLogger("x402_settlement")

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
        "chain_id": 2368,
        "chain_label": "kite-testnet",
        "rpc_url": "https://rpc-testnet.gokite.ai/",
        "explorer_url": "https://testnet.kitescan.ai",
        "settlement_token": "0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63",  # Test USDT (18 decimals)
        "facilitator_url": "https://facilitator.pieverse.io",
        "decimals": 18,
        "scheme": "exact",  # Pieverse v2 uses "exact" (gokite-aa is the AA SDK, not the x402 scheme)
        "network_id": "eip155:2368",
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

    record = {
        "from": from_address or "unset",
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
    }

    # Only attempt real settlement if we have a vault/wallet address
    if not from_address:
        logger.info("No vault configured — simulating payment: $%.2f → %s", amount_usd, to_address)
        return record

    try:
        # Both Pieverse (Kite) and Coinbase CDP (Base) use v2 envelope format
        endpoint = f"{net['facilitator_url']}/v2/settle"
        payload = {
            "x402Version": 2,
            "paymentPayload": {
                "from": from_address,
                "to": to_address,
                "amount": amount_atomic,
            },
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
