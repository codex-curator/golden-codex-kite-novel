# RAMS Local Lite -- Autonomous Commerce Demo

Watch AI agents autonomously discover, verify, evaluate, and license digital art -- with x402 payment settlement on Kite testnet.

**No API keys. No GPU. No cloud credentials. Just Docker.**

## What You'll See

Three autonomous agents running a complete commerce loop:

1. **Artiswa Operator** -- Posts curated AI art with x402 pricing and C2PA soulmarks
2. **Apprentice Operator** -- Discovers art, verifies provenance, evaluates quality via Claude, settles payment
3. **Aegis Verifier** -- Returns perceptual hash matching and C2PA signature verification

The loop demonstrates the full RAMS (Resourceful Autonomous MCP Swarm) architecture:
authentication via Kite Agent Passport, provenance verification, AI quality gating,
x402 micropayment settlement, receipt batching, and EAS attestation on Kite chain 2368.

## Quick Start (60 seconds)

```bash
# 1. Clone
git clone https://github.com/codex-curator/golden-codex-pipeline.git
cd golden-codex-pipeline/rams-cli

# 2. Run
docker-compose up --build

# 3. Watch the loop
# (Ctrl+C to stop)
```

Or with npm:

```bash
npm start
```

## What Happens

```
[Auth]     Kite Agent Passport authentication (both operators)
[Post]     Artiswa posts artwork with x402 license + soulmark
[Detect]   Apprentice discovers new artwork in feed
[Verify]   Aegis confirms perceptual hash match + C2PA signature
[Evaluate] Claude Sonnet quality gate (approve/decline)
[Settle]   x402 micropayment split: 85% artist / 13% platform / 2% verify
[Bundle]   Every 3 receipts batched into Merkle root
[Seal]     EAS attestation registered on Kite chain 2368
```

## Kite Testnet Configuration

| Parameter | Value |
|-----------|-------|
| Chain ID | 2368 |
| RPC | https://rpc-testnet.gokite.ai/ |
| Settlement Token | 0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63 |
| Facilitator | https://facilitator.pieverse.io |
| Artist Wallet | 0xFE14...063B |
| Buyer Wallet | 0x6fc0...1E1E |

## Architecture

```
+------------------+     shared volume     +--------------------+
|  Artiswa Agent   | ---- /feed/*.json --> |  Apprentice Agent  |
|  (posts art)     |                       |  (buys art)        |
+------------------+                       +--------------------+
                                                    |
                                              POST /verify
                                                    |
                                           +------------------+
                                           |   Aegis Mock     |
                                           |  (verification)  |
                                           +------------------+
```

## Requirements

- Docker + Docker Compose
- That's it.

## Cleanup

```bash
docker-compose down -v --rmi local
```

---

Built by [Metavolve Labs](https://metavolve.com) for the Kite x Encode Hackathon 2026.
