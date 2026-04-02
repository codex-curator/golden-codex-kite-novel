# Golden Codex RAMS

### The Zero-Trust Compliance Firewall for the $4.5 Trillion Agent Economy

> **8 autonomous AI agents** that discover, cryptographically verify, and legally license enterprise data — settling every operation via Kite x402 micropayments. Zero human intervention. Zero legal liability. Clean data at the speed of compute.

[![Live Demo](https://img.shields.io/badge/Live_Demo-golden--codex.com/kite--demo-0066cc?style=for-the-badge)](https://golden-codex.com/kite-demo)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Kite AI](https://img.shields.io/badge/Built_on-Kite_AI-3399ff?style=for-the-badge)](https://gokite.ai)

**Track**: Novel Track — Kite AI Global Hackathon 2026
**Team**: Metavolve Labs, Inc. (Founder: Tad MacPherson)
**Platform**: [golden-codex.com](https://golden-codex.com) — live with real users

---

## The Problem

Frontier AI models are starving for high-signal data, but enterprise ingestion is paralyzed by copyright liability. LAION-5B. Common Crawl. The shadow libraries that trained a generation of models are now multi-billion-dollar legal liabilities.

Requiring human lawyers to authorize every agentic data transaction kills the autonomy that makes agents valuable.

## The Solution

**Golden Codex RAMS** (Recursive Agent Market Swarm) is an autonomous data procurement pipeline. Art was the stress test — we solved high-dimensional perceptual hashing, the hardest provenance problem. Now our format-agnostic metadata factory processes any visual data your frontier models need.

```
Upload → Aurora (intake) → Nova (Gemini enrichment) → Flux (L4 GPU upscale)
  → Atlas (metadata + Soulmark) → Archivus (Arweave) → Mintra (NFT mint)
  → Aegis (verification) → Soulprint sealed. Provenance forever.

Total cost: $0.438 USDC per asset — settled on Kite in 1 batched transaction.
```

---

## Quick Start — Test Locally in 60 Seconds

```bash
git clone https://github.com/codex-curator/golden-codex-kite-novel.git
cd golden-codex-kite-novel

# Run the Watchdog Agent locally
cd agents/watchdog-agent
pip install -r requirements.txt
python main.py

# POST http://localhost:8080/demo with an image to test
# Agent authenticates → discovers → verifies → licenses → settles on Kite
```

---

## The 8-Agent Pipeline

| Agent | Role | x402 Cost | Technology |
|-------|------|-----------|------------|
| **Thalos Prime** | Orchestrator / Architect Agent | — | SPACE framework, session keys |
| **Aurora** | Intake & archiving | $0.05 | Sequential ID, GCS archiving |
| **Nova** | AI enrichment | $0.10 | Gemini 3.1 Pro (8-section codex) |
| **Flux** | Neural upscaling | $0.10 | NVIDIA L4 GPU, RealESRGAN |
| **Atlas** | Metadata infusion + hash seal | $0.05 | ExifTool XMP/C2PA + SHA-256 |
| **Archivus** | Permanent storage | $0.03 | Arweave L1 (200+ year endowment) |
| **Mintra** | NFT minting | $0.10 | ERC-721 on Ethereum + Polygon |
| **Aegis** | Provenance verification | $0.008 | LSH 16x4 perceptual hash |

**Three-model intelligence**: Claude Sonnet (artistic) + Gemini 3.1 Pro (analytical) + GPT-4o (voice)

---

## Autonomous Commerce Loop

Three operators run autonomously with zero human input:

| Operator | What It Does | Trigger |
|----------|-------------|---------|
| **Artiswa Operator** | Claude-powered poster — generates captions, posts art to X | Every 45 min |
| **Apprentice Operator** | Claude-powered buyer — evaluates + licenses training data | Every 2 min |
| **Watchdog Agent** | Monitors X, verifies provenance, settles payments | Every 60 sec |

**The closed loop**: Artiswa posts art → Apprentice detects → Aegis verifies → Claude evaluates → pays artist on Kite. Two AI agents conducting commerce. The seller didn't know the buyer existed.

---

## Transaction Bundling (90% Gas Savings)

Instead of 7 separate x402 transactions per pipeline run, Thalos Prime bundles all settlements into a single on-chain transaction via the `KiteBundler` smart contract:

```
C_total   = 7 x (Gas_base + Gas_logic)              // 7 separate transactions
C_bundled = Gas_base + 7(Gas_logic) + Gas_overhead   // 1 bundled transaction

Savings: ~1,000,000 gas units per pipeline run (90%+ reduction)
```

The bundler uses **non-atomic execution** (try/catch per payment) — if one provider fails, the other 6 still settle. See [`contracts/kite/`](contracts/kite/) for the Solidity implementation.

---

## Kite Integration

| Kite Technology | Our Implementation |
|-----------------|-------------------|
| **Kite Passport** | Cryptographic identity for all 8 agents |
| **gokite-aa x402** | Every agent-to-agent payment |
| **Pieverse Facilitator** | On-chain settlement (/v2/verify, /v2/settle) |
| **SPACE Framework** | Root → Delegated → Session key hierarchy |
| **EAS Attestations** | Soulprint provenance on-chain |
| **PoAI Rewards** | GPU/LLM compute earns KITE |
| **Transaction Bundling** | A2 batch: 7 payments → 1 transaction |

---

## Rubric Alignment — 9/9

### Required (6/6)
- ✅ **Web App & CLI Tool** — golden-codex.com + local testing
- ✅ **Agent Authenticates** — Kite Passport + SPACE framework
- ✅ **Executes Autonomously** — Zero human clicks, Cloud Scheduler
- ✅ **On-Chain Settlement** — x402 via Pieverse on Kite
- ✅ **Deployed Live** — GCP Cloud Run, 186 Terraform-managed resources
- ✅ **GitHub + README** — You're reading it

### Bonus (3/3)
- ⭐ **Multi-Agent Coordination** — 8-agent sequential pipeline
- ⭐ **Scoped Permissions** — SPACE framework, $10/day caps, session keys
- ⭐ **Gas Abstraction** — gokite-aa SDK, ClientAgentVault

---

## Repository Structure

```
├── agents/
│   ├── watchdog-agent/          # X monitor + x402 licensing (Flask/Cloud Run)
│   ├── apprentice-operator/     # Claude-powered autonomous buyer
│   └── artiswa-operator/        # Claude-powered autonomous poster
│
├── contracts/kite/
│   ├── AeternumProvenanceSchema.sol  # EAS schema for Soulprint attestations
│   └── AgentPaymentLedger.sol        # On-chain x402 audit trail + PoAI
│
├── dashboard/                   # React components for golden-codex.com/kite-demo
│   ├── HeroSection.jsx          # "$4.5T Compliance Firewall"
│   ├── ComplianceCrisis.jsx     # "End of the Wild West" crisis framing
│   ├── AutomatedAuditing.jsx    # "Art Was the Stress Test" pivot
│   ├── CliDemo.jsx              # Interactive CLI terminal mockup
│   ├── AgentLaborGraph.jsx      # 8-agent pipeline visualization
│   ├── WatchdogDashboard.jsx    # Autonomous X monitoring demo
│   ├── EconomicFlows.jsx        # Three economic flows on Kite
│   ├── RubricAlignment.jsx      # 9/9 checklist for judges
│   └── PitchSection.jsx         # Enterprise CTA
│
├── x402/
│   └── constants.js             # Kite chain config, agent defs, costs
│
├── docs/
│   ├── AGENT_CHANGES_REQUIRED.md  # Per-agent x402 integration spec
│   └── GO_LIVE_CHECKLIST.md       # Deployment guide
│
└── schema/
    └── golden-codex-template.json # Golden Codex metadata schema
```

---

## What's Already in Production

This is not a hackathon prototype. These are live services:

- **golden-codex.com** — Live platform with real users and Stripe payments
- **StudioMCPHub** — 27 MCP tools at [studiomcphub.com](https://studiomcphub.com)
- **Alexandria Aeternum** — 500K+ provenance-tracked artworks on [HuggingFace](https://huggingface.co/datasets/Metavolve-Labs/alexandria-aeternum-genesis)
- **8 Cloud Run agents** — 186 Terraform-managed GCP resources
- **NVIDIA L4 GPU** — 20+ neural upscaling models
- **Smart contracts** — ERC-721 on Ethereum + Polygon (deployed, verified)
- **Arweave** — Permanent storage via native AR SDK
- **7 Zenodo DOIs** — Published research papers
- **3 Provisional Patents** — Filed with USPTO

---

## Kite Chain Details

| Parameter | Value |
|-----------|-------|
| Testnet Chain ID | 2368 (Ozone) |
| Testnet RPC | `https://rpc-testnet.gokite.ai/` |
| Mainnet Chain ID | 2366 |
| Settlement Token | `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63` |
| Facilitator | `https://facilitator.pieverse.io` |
| x402 Scheme | `gokite-aa` |

---

## License

MIT — See [LICENSE](LICENSE)

The Kite integration layer, autonomous operators, smart contracts, and dashboard components are fully open-source. The full Golden Codex production platform (AI enrichment prompts, artist personas, batch pipelines, Studio UI) remains proprietary to Metavolve Labs, Inc.

---

## Links

| Resource | URL |
|----------|-----|
| **Live Demo** | [golden-codex.com/kite-demo](https://golden-codex.com/kite-demo) |
| **Platform** | [golden-codex.com](https://golden-codex.com) |
| **MCP Hub** | [studiomcphub.com](https://studiomcphub.com) |
| **Dataset** | [HuggingFace](https://huggingface.co/datasets/Metavolve-Labs/alexandria-aeternum-genesis) |
| **GitHub** | [github.com/codex-curator](https://github.com/codex-curator) |

---

*Metavolve Labs, Inc. | San Francisco, California*

*"Synthetic Data is not the problem. Synthetic Garbage is."*
