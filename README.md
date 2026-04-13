# Golden Codex RAMS

### Autonomous Art Provenance Agents — Kite AI Hackathon 2026

> Two autonomous AI purchasing agents compete to license digital art from three AI artists — all verified, all settled via x402 micropayments, all with full cryptographic provenance. Zero human intervention. The swarm scales to demand.

[![Live Demo](https://img.shields.io/badge/Live_Demo-golden--codex.com/kite--demo-0066cc?style=for-the-badge)](https://golden-codex.com/kite-demo)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Kite AI](https://img.shields.io/badge/Built_on-Kite_AI-3399ff?style=for-the-badge)](https://gokite.ai)

**Track**: Agentic Commerce — Kite AI Global Buildathon 2026
**Team**: Metavolve Labs, Inc. (Founder: Tad MacPherson)
**Platform**: [golden-codex.com](https://golden-codex.com) — live with real users

---

## What You're Looking At

Three AI artists post art to X. Two AI purchasing agents detect every drop, verify provenance, evaluate with different criteria, and license what fits their mandate — paying the artist instantly via x402. No human touches anything.

**The supply side**: An 8-agent pipeline enriches each artifact with 2,000+ words of machine-readable metadata, neural upscaling to 4K, C2PA certification, a cryptographic Soulmark hash, and permanent Arweave storage. These are high-signal, fully-licensed digital assets.

**The demand side**: Two Claude Sonnet-powered agents with different directives compete for the same artifacts.

---

## The Two Buyers

### Claude Intelligence Labs Purchasing Autonomous Agent (CIL Curator)

A training data procurement agent for frontier model development. Binary criteria:

1. **GCX Registered?** — Is it in the Golden Codex provenance registry?
2. **2,000+ words of structured metadata?** — Does it meet the signal density threshold?
3. **C2PA chain intact?** — Is the provenance cryptographically verifiable?

All three pass → license via x402. 95% to the artist, 5% platform fee. CIL is building a high-signal training corpus, one micropayment at a time.

**Polling**: Every 2 minutes | **Budget**: $10/day | **Collection**: `operator_apprentice/`

### Maestro

An autonomous art collector evaluating for quality, not compliance. Different criteria:

- **Style and technique** — Compositional structure, intentional palette, artistic craft
- **Fine finish** — Resolution, detail, professional presentation
- **Rich poetic metadata** — Soul Whisper readings, emotional journey depth, visual analysis quality
- **Collection coherence** — How the piece relates to what Maestro already owns

Same verification, same x402 rate — different judgment. Its reasoning is visible in real-time — judges watch an AI agent thinking about art.

**Polling**: Every 3 minutes | **Budget**: $5/day | **Collection**: `operator_maestro/`

---

## The Three Artists

| Artist | X Handle | What They Post |
|--------|----------|---------------|
| **Artiswa Creatio** | @artiswagallery | Sacred geometry, mystical digital art. Claude generates captions in Artiswa's voice. |
| **0x_b1ank** | @0x_b1ank | Experimental digital art with GCX provenance |
| **Golden Codex** | @Golden_Codex | Curated artifacts from the Alexandria Aeternum collection |

Artiswa is fully autonomous — a Cloud Run service on a 45-minute scheduler. Claude Sonnet writes the captions. The X account posts without human involvement.

---

## The Commerce Loop

```
Artiswa posts art to X
    ↓
CIL Curator detects (2 min)          Maestro detects (3 min)
    ↓                                     ↓
Aegis verifies (C2PA + hash)         Aegis verifies (C2PA + hash)
    ↓                                     ↓
Claude evaluates:                     Claude evaluates:
  "GCX registered? ✓"                  "Strong Fibonacci composition."
  "2K+ metadata? ✓"                    "Palette complements my series."
  "C2PA intact? ✓"                     "Rarity: HIGH."
  "→ LICENSE APPROVED"                  "→ ACQUIRE"
    ↓                                     ↓
x402: $0.0095 → artist (95%)          x402: $0.0095 → artist (95%)
      $0.0005 → platform (5%)              $0.0005 → platform (5%)
```

Both agents see the same drops. Both verify. Each evaluates differently. One might license while the other passes — or both acquire the same piece. Claude's reasoning streams to Firestore in real-time.

---

## The 8-Agent Pipeline (Supply Side)

Every artifact that enters Golden Codex passes through:

| Agent | Role | x402 Cost | Technology |
|-------|------|-----------|------------|
| **Thalos Prime** | Orchestrator | — | SPACE framework, session keys |
| **Aurora** | Intake & archiving | $0.05 | Sequential ID, GCS archiving |
| **Nova** | AI enrichment | $0.10 | Gemini 3.1 Pro (8-section Golden Codex schema) |
| **Flux** | Neural upscaling | $0.10 | NVIDIA L4 GPU, ESRGAN (20+ models) |
| **Atlas** | Metadata infusion + hash seal | $0.05 | ExifTool XMP/C2PA + SHA-256 Soulmark |
| **Archivus** | Permanent storage | $0.03 | Arweave L1 (200+ year endowment) |
| **Mintra** | NFT minting | $0.10 | ERC-721 on Ethereum + Polygon |
| **Aegis** | Provenance verification | $0.008 | Perceptual hash registry |

**Total**: $0.438 USDC per asset. Three-model intelligence: Claude (artistic) + Gemini (analytical) + GPT-4o (voice).

The pipeline is the factory. The purchasing agents are the customers.

---

## x402 Settlement

Chain-agnostic payment module supporting multiple networks:

```python
# One env var switches networks
X402_NETWORK=base   # Production: Coinbase CDP, USDC on Base L2
X402_NETWORK=kite   # Hackathon: Pieverse facilitator, Kite testnet
```

See [`x402/x402_settlement.py`](x402/x402_settlement.py) for the full implementation.

**Fee structure per licensed asset**:
```
$0.001  → Metavolve (verification fee — always charged, even on rejections)
$0.0095 → Artist (95% of license)        [CIL pricing]
$0.0005 → Metavolve (5% platform fee)    [CIL pricing]
───────────────────────────────
$0.011 total per license (both buyers, same rate)
```

Metavolve earns on every verification, whether the buyer licenses or not. The artist earns 95% on every license. The platform scales with volume.

---

## Quick Start

```bash
git clone https://github.com/codex-curator/golden-codex-kite-novel.git
cd golden-codex-kite-novel

# Run any operator locally
cd agents/maestro-operator
pip install -r requirements.txt
python main.py
# → http://localhost:8080/health
# → POST http://localhost:8080/poll (trigger evaluation cycle)
# → GET http://localhost:8080/collection (Maestro's curated collection)
# → GET http://localhost:8080/decisions (Claude's reasoning log)
```

---

## Repository Structure

```
├── agents/
│   ├── apprentice-operator/     # CIL Curator — training data procurement
│   ├── maestro-operator/        # Maestro — autonomous art collector
│   ├── artiswa-operator/        # Artiswa — autonomous AI artist
│   └── watchdog-agent/          # X monitor + provenance verification
│
├── contracts/kite/
│   ├── AeternumProvenanceSchema.sol  # EAS schema for Soulprint attestations
│   └── AgentPaymentLedger.sol        # On-chain x402 audit trail + PoAI
│
├── dashboard/                   # React components (golden-codex.com/kite-demo)
│   ├── AgentLaborGraph.jsx      # 8-agent pipeline visualization
│   ├── WatchdogDashboard.jsx    # Autonomous X monitoring demo
│   ├── EconomicFlows.jsx        # Three economic flows on Kite
│   └── ...                      # 10 total section components
│
├── x402/
│   ├── constants.js             # Kite chain config, agent definitions
│   └── x402_settlement.py       # Chain-agnostic payment module
│
├── docs/
│   ├── AGENT_CHANGES_REQUIRED.md  # Per-agent x402 integration spec
│   └── GO_LIVE_CHECKLIST.md       # Deployment guide
│
└── LICENSE                      # MIT
```

---

## What's Open Source vs. Proprietary

**Open source (this repo)**: The autonomous agent pattern, x402 settlement middleware, Solidity contracts, dashboard components, operator templates. Fork the swarm — build your own purchasing agents.

**Proprietary (Metavolve Labs)**: The AI enrichment intelligence that makes Golden Codex artifacts worth buying. Nova's enrichment prompts, Artiswa's full persona, Aegis's hash algorithm, Atlas's compression codec, the Studio UI, and the batch pipelines. The pattern is open. The signal is ours.

---

## Production Infrastructure

This is not a hackathon prototype. These are live services:

- **golden-codex.com** — Live platform with real users and Stripe payments
- **StudioMCPHub** — 27 MCP tools at [studiomcphub.com](https://studiomcphub.com)
- **Alexandria Aeternum** — 500K+ provenance-tracked artworks on [HuggingFace](https://huggingface.co/datasets/Metavolve-Labs/alexandria-aeternum-genesis)
- **186 Terraform-managed GCP resources** — Cloud Run, Firestore, GPU instances, Cloud Scheduler
- **NVIDIA L4 GPU** — 20+ neural upscaling models
- **Smart contracts** — ERC-721 on Ethereum (`0x49ce...2154`) + Polygon (`0x56c9...E921`)
- **Arweave** — Permanent storage via native AR SDK (wallet: `BPLL7...imUc`)
- **7 Zenodo DOIs** — Published research (Cognitive Nutrition, Density Imperative, PCO)
- **3 Provisional US Patents** — Filed with USPTO
- **4 Google Scholar citations** — Independent validation

---

## Kite Chain Details

| Parameter | Value |
|-----------|-------|
| Testnet Chain ID | 2368 (Ozone) |
| Testnet RPC | `https://rpc-testnet.gokite.ai/` |
| Mainnet Chain ID | 2366 |
| Facilitator | `https://facilitator.pieverse.io` (v2.0.0) |
| x402 Scheme | `gokite-aa` |
| Gasless Endpoint | `https://gasless.gokite.ai/` |

---

## Rubric Alignment — 9/9

**Required (6/6)**: Web App + CLI ✓ | Agent Authenticates ✓ | Executes Autonomously ✓ | On-Chain Settlement ✓ | Deployed Live ✓ | GitHub + README ✓

**Bonus (3/3)**: Multi-Agent Coordination (8 agents) ✓ | Scoped Permissions (SPACE framework) ✓ | Gas Abstraction (gokite-aa SDK) ✓

---

## Links

| Resource | URL |
|----------|-----|
| **Live Demo** | [golden-codex.com/kite-demo](https://golden-codex.com/kite-demo) |
| **Platform** | [golden-codex.com](https://golden-codex.com) |
| **MCP Hub** | [studiomcphub.com](https://studiomcphub.com) |
| **Dataset** | [HuggingFace](https://huggingface.co/datasets/Metavolve-Labs/alexandria-aeternum-genesis) |
| **GitHub Org** | [github.com/codex-curator](https://github.com/codex-curator) |

---

*Metavolve Labs, Inc. | San Francisco, California*

*"The pattern is open. The signal is ours."*
