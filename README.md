# Golden Codex RAMS — Kite AI Hackathon 2026 (Novel Track)

> **Recursive Agent Market Swarm**: 8 autonomous AI agents settling x402 micropayments on Kite chain for digital art provenance, AI training data licensing, and cultural preservation.

**Development Period**: March 27 — April 26, 2026
**Team**: Metavolve Labs, Inc. (Solo Founder: Tad MacPherson)
**Live Platform**: [golden-codex.com](https://golden-codex.com)
**Demo**: [golden-codex.com/kite-demo](https://golden-codex.com/kite-demo)

---

## What This Is

A production AI creative supply chain where autonomous agents:
1. **Monitor** artist X accounts for new image drops (Watchdog Agent)
2. **Verify** C2PA signatures + perceptual hash against the Golden Codex Registry (Aegis)
3. **Pay artists** automatically for training data licenses via x402 on Kite ($0.10/image)
4. **Settle** every operation on Kite L1 via the Pieverse facilitator (`gokite-aa` scheme)
5. **Attest** provenance on-chain via EAS (Ethereum Attestation Service)

No human clicks. No API keys. **Payment IS authorization.**

---

## Architecture

```
[ X IMAGE DROP ] → Watchdog Agent (polls @artiswagallery, @0x_b1ank, @Golden_Codex)
       │
       ├─ x402 $0.02 → [ AEGIS ] Perceptual hash verification (LSH 16×4, 100K+ scale)
       │                    ├─ C2PA: ✓/✗
       │                    └─ GCX Registered: ✓/✗
       │
       ├─ License evaluation (training terms from Soulprint metadata)
       │
       └─ x402 $0.10 → [ ARTIST WALLET ] Training data license fee
                              │
                        All settled on Kite L1
                        via Pieverse facilitator
```

### Full 8-Agent Pipeline

| Agent | Role | x402 Cost | Scheme |
|-------|------|-----------|--------|
| Aurora | Intake & archiving | $0.01 | gokite-aa |
| Nova | AI enrichment (Gemini 3.1 Pro) | $0.05 | gokite-aa |
| Flux | GPU upscaling (NVIDIA L4) | ≤$0.20 | gokite-aa |
| Atlas | Metadata infusion + hash registration | $0.02 | gokite-aa |
| Archivus | Arweave permanent storage | $0.03 | gokite-aa |
| Mintra | NFT minting (Ethereum) | $0.10 | gokite-aa |
| Aegis | Provenance verification | $0.008 | gokite-aa |
| Watchdog | X monitoring + licensing | — | orchestrator |

**Total per artwork: $0.448 USDC**

---

## Kite Integration Points

| Kite Technology | Our Implementation |
|-----------------|-------------------|
| **Kite Passport** | Cryptographic identity for all 8 agents |
| **gokite-aa x402** | Every agent-to-agent payment |
| **Pieverse Facilitator** | On-chain settlement (/v2/verify, /v2/settle) |
| **ClientAgentVault** | ERC-4337 smart account per agent |
| **Standing Intent** | Daily budget constraint for Thalos Prime |
| **Session Keys** | Ephemeral per-job authorization |
| **EAS Attestations** | Soulprint provenance on-chain |
| **gokite-aa-sdk** | Vault deployment + spending rules |

---

## Repository Contents

```
├── agents/
│   └── watchdog-agent/           # X Image Watchdog — autonomous monitoring + licensing
│       ├── main.py               # Flask service: /poll, /demo, /events, /stats
│       ├── Dockerfile
│       ├── requirements.txt
│       └── deploy.sh
│
├── contracts/kite/
│   ├── AeternumProvenanceSchema.sol   # EAS schema for Soulprint attestations
│   └── AgentPaymentLedger.sol         # On-chain x402 payment audit trail
│
├── extensions/gcx-detector/      # Chrome extension — detect GCX artworks anywhere
│   ├── manifest.json             # Chrome MV3
│   ├── src/
│   │   ├── background.js         # Service worker
│   │   ├── content.js            # Page scanner + golden halo
│   │   ├── hash.js               # Client-side 256-bit DCT pHash
│   │   ├── popup.html
│   │   └── popup.js
│   └── styles/overlay.css        # Golden halo + provenance panel
│
├── dashboard/                    # React components for /kite-demo page
│   ├── AgentLaborGraph.jsx       # Interactive 9-node pipeline visualization
│   ├── WatchdogDashboard.jsx     # Split-screen X drops + agent pipeline
│   ├── HeroSection.jsx
│   ├── EconomicFlows.jsx
│   ├── ProvenanceWatchdog.jsx
│   ├── LiveStatsDashboard.jsx
│   ├── TechnicalArchitecture.jsx
│   └── PitchSection.jsx
│
├── schema/
│   ├── golden-codex-template.json     # Golden Codex metadata schema (v1.1)
│   └── golden_codex_reader.py         # Open-source Soulprint reader (Python)
│
├── x402/
│   ├── kite_config.py            # Kite chain configuration (testnet + mainnet)
│   └── x402_middleware.py        # HTTP 402 payment flow reference implementation
│
└── docs/
    ├── AGENT_CHANGES_REQUIRED.md  # Per-agent x402 integration spec
    └── GO_LIVE_CHECKLIST.md       # Step-by-step deployment guide
```

---

## Quick Start

### Install the Extension
```bash
# Clone this repo
git clone https://github.com/codex-curator/golden-codex-kite-novel.git

# Load in Chrome
# 1. Open chrome://extensions
# 2. Enable Developer Mode
# 3. Click "Load unpacked" → select extensions/gcx-detector/
# 4. Visit golden-codex.com/alexandria-aeternum → golden halos appear on registered artworks
```

### Run the Watchdog Agent Locally
```bash
cd agents/watchdog-agent
pip install -r requirements.txt
export X_BEARER_TOKEN="your_token"
export ARTISWA_USER_ID="2019690975011172361"
python main.py
# POST http://localhost:8080/demo with an image to test
```

### Deploy to Cloud Run
```bash
cd agents/watchdog-agent
./deploy.sh  # Requires gcloud auth
```

---

## Three Economic Flows

1. **Internal Settlement** — Our agents paying our agents on Kite (pipeline processing)
2. **External Consumption** — Thalos discovering + paying StudioMCPHub tools via MCP
3. **External Provision** — Outside agents paying Aegis for verification + training data licensing

---

## Judging Criteria Mapping

| Criteria | Evidence |
|----------|---------|
| **Agent Autonomy** | Watchdog: zero human input. Standing Intent budget caps. Session Keys per job. |
| **Developer Experience** | This README. Docker. One-line deploy. Extension loads in 30 seconds. |
| **Real-World Applicability** | Production platform at golden-codex.com. Real art, real collectors, real GPU. |
| **Novel or Creative** | Claude + Gemini + GPT-4o three-model stack. Browser extension with golden halo. Training data licensing via x402. |

---

## Kite Chain Details

| Parameter | Value |
|-----------|-------|
| Testnet Chain ID | 2368 |
| Testnet RPC | https://rpc-testnet.gokite.ai/ |
| Mainnet Chain ID | 2366 |
| Mainnet RPC | https://rpc.gokite.ai/ |
| Settlement Token (testnet) | `0x0fF5393387ad2f9f691FD6Fd28e07E3969e27e63` |
| USDC on Mainnet | `0x7aB6f3ed87C42eF0aDb67Ed95090f8bF5240149e` |
| Facilitator | https://facilitator.pieverse.io |
| AA SDK | `npm install gokite-aa-sdk` |
| Passport MCP | https://neo.dev.gokite.ai/v1/mcp |

---

## License

MIT — See [LICENSE](LICENSE)

**Note**: This repository contains the open-source Kite integration layer. The full Golden Codex production platform (AI enrichment prompts, artist personas, batch pipelines, Studio UI) remains proprietary to Metavolve Labs, Inc.

---

## Links

- **Live Platform**: [golden-codex.com](https://golden-codex.com)
- **Kite Demo**: [golden-codex.com/kite-demo](https://golden-codex.com/kite-demo)
- **StudioMCPHub**: [studiomcphub.com](https://studiomcphub.com)
- **Alexandria Aeternum**: [golden-codex.com/alexandria-aeternum](https://golden-codex.com/alexandria-aeternum)
- **Kite Docs**: [docs.gokite.ai](https://docs.gokite.ai)

---

*Metavolve Labs, Inc. — San Francisco, California*
*"The agentic economy needs culture. We're bringing it."*
