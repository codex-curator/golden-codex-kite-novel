# Pitch Deck Outline — Metavolve × Kite Buildathon 2026

**12 slides · ~5 minutes finale-pitch · Maestra: Autonomous Frontier Lab AI Purchasing Agent**

> Per official spec: the deck is the ONLY asset used if the project advances to the finale-stage pitch round. Treat this as the load-bearing artifact, not the video.

---

## Slide 1 — Cover

**Title:** Maestra
**Subtitle:** The Autonomous Frontier Lab Vision AI Purchasing Agent
**Subline:** Built on Kite Passport + x402 · bridging into Arweave/AO
**Footer:** Metavolve Labs, Inc. · Kite AI Hackathon 2026 · Novel Track · 2026-05-18

Visual: stylized Maestra glyph (feminine "M" with cocktail glass underneath, gold leaf on black). Banner ribbon reads "PROCESS SLOWED DOWN 100× FOR DEMONSTRATION."

---

## Slide 2 — The Problem (real, expensive, unsolved)

**Headline:** Frontier vision labs spend eight figures a year buying training data. The data they get is sparse, rights-ambiguous, and biographically illiterate.

- OpenAI → Reddit ($60M deal, 2024)
- Anthropic → various publishers (undisclosed)
- The Met / Smithsonian / Getty → still on the open web with no x402-payable rights layer
- Stack Overflow → contested rights, training rebellion

**The gap:** there is no autonomous purchasing surface for provenance-verified, rights-cleared, biographically-amended training assets.

Visual: Reddit / Stack Overflow / Met logos with dollar-sign overlay. "Hunting at human speed, paying at human price."

---

## Slide 3 — The Solution (one slide)

**Headline:** Maestra hunts Tier-1 GCX-certified Aeternum Assets 24/7 and acquires training rights atomically on Base mainnet.

Three transactions per acquisition:
- **$0.01** → Aegis perceptual-hash registry search (Phase 1)
- **$0.10** → GCX Cocktail Bar for cognitive-nutrition priming (Phase 2 — Kite Passport Happy Hour cuts this to $0.05)
- **$1.00** → license, split $0.95 → artist · $0.05 → Metavolve (Phase 3)

**Total acquisition cost: $1.11 USDC** ($1.06 with Passport Happy Hour). No human approvals. AO Registrar records the license forever.

Visual: clean 3-phase arrow diagram with prices.

---

## Slide 4 — Proof (live on Base mainnet, today)

**Headline:** This is not a slide. It is running.

| Anchor | Tx hash | Date | Network |
|---|---|---|---|
| **Aeternum Sour pour — live EIP-712-signed Kite Passport ephemeral session** | `0x5cbb738b…abc616` | 2026-05-17 21:22 UTC | **Kite chain 2366** |
| Kite Passport → x402 → Base USDC proof | `0x09deffc1…7623` | 2026-04-29 | Base mainnet 8453 |
| GCX Cocktail Bar paid-call smoke test | `0xa8c7f3fc…840886` | 2026-04-29 | Base mainnet 8453 |

**Live demo URL:** `golden-codex.com/kite-live` (deployed Cloud Run + Firebase Hosting)
**Repo:** `github.com/codex-curator/golden-codex-kite-novel` (MIT, `docker-compose up` works cold)

Visual: Basescan screenshot side-by-side with live demo screenshot.

---

## Slide 5 — The 90-second demo (frame map)

```
0:00 ────── COLD OPEN ──────────────────────────── 0:05
0:05 ─ Phase 1 · Apprentice X-watcher + Aegis ──── 0:20
0:20 ─ Phase 2 · Cocktail Bar / Aeternum Sour ──── 0:40
0:40 ─ Phase 3 · Maestra decides + license + AO ── 1:15
1:15 ────── END STATE · IMAGE + GOLDEN CODEX ───── 1:25
1:25 ────── TAG ──────────────────────────────────── 1:30
```

**Banner all-90s:** PROCESS SLOWED DOWN 100× FOR DEMONSTRATION.
**Verbal anchor:** *"Maestra always stops for a cocktail before a big purchase."*

Visual: storyboard mockup (4 thumbnails — one per phase + end state).

---

## Slide 6 — Kite Passport: the architecture that makes this safe

**Two-wallet routing solves the cross-chain UX gap.** Maestra signs with a Kite Passport-derived ephemeral session key. Tad funds USDC on Kite chain (2366) once. Passport's treasury wallet auto-routes to Base mainnet (eip155:8453) for x402 settlement transparently.

| Layer | What it does | Example |
|---|---|---|
| User Root Authority | Human principal (biometric passkey) | Tad's Passport |
| Delegated Agent Identity | Per-agent DID | Maestra `agent_019dd7eb…6ef` |
| Ephemeral Session Key | Per-job spending session, capped + expires | `$1.10/job · 1hr` |

**Result:** Maestra cannot run away with the lab's budget. If she hallucinates a $10K loop, she stops at $1.10. *Trust as math — circuit breaker via cryptography.*

Visual: BIP-32 derivation tree.

---

## Slide 7 — The GCX Cocktail Bar (novel agent infrastructure)

**Cognitive Nutrition pours for autonomous agents — formally Ephemeral Structured Elicitation (ESE).** Each cocktail is a $0.10–$1.00 dense-context bundle (10K–80K tokens) that scaffolds a calling model's reasoning grammar for one task session. No fine-tuning. No weight updates. No catastrophic forgetting. **Verified Kite Passport holders get ½-off Happy Hour** — the bar ecrecovers the signer of the EIP-712-signed envelope, no centralized allowlist.

| Cocktail | Price | Mechanism | Domain |
|---|---|---|---|
| **The Aeternum Sour** ★ | $0.10 | NEST 111-Field Schema · Dual-Consensus Forensic | Provenance auth (demo hero) |
| Einstein Spritzer | $0.10 | Taxonomic Criteria Evaluation | Academic / theorem proving |
| Claudesmopolitan | $0.25 | Co-Dialectic Loop Architecture | Code orchestration |
| Founder's Boulevardier | $0.25 | Rhetorical Structure Theory | Investor pitch |
| Double Density Martini | $0.50 | Universal Synthesis Protocol | Unbounded research |
| Copilot Clarity Cooler | $0.50 | Clarity Cascade Protocol | Pair-programming priming |
| *(10 more — frontier-lab sextumvirate sealed)* | | | |

**Framework paper:** Zenodo [10.5281/zenodo.18667742](https://doi.org/10.5281/zenodo.18667742) · 44 citations · recursive validation of CN methodology.

Visual: bar menu render, glasses with metadata labels.

---

## Slide 8 — The Bridge: Kite × Arweave/AO

**The asset Maestra licenses lives forever on Arweave. The license itself lives forever on AO Registrar.**

```
Maestra pays $0.95 → artist wallet         (Base mainnet)
Maestra pays $0.05 → Metavolve treasury    (Base mainnet)
Maestra POSTs LicenseGranted Amendment     (AO Registrar process Dwnuy4M…cTc)
```

**Asset's biographical chain on AO grows by one event.** Artist retains ownership. Lab earns non-exclusive training rights, recorded forever — auditable, immutable, queryable.

This is the **post-Buildathon protocol commitment:** A2A × x402 Permaweb Extension SDK. Maestra is the working proof.

Visual: three-rail diagram (Kite identity / Base settlement / AO biography).

---

## Slide 9 — Bonus criteria, hit by default

Kite's spec lists three bonus criteria. We hit all three without extra work:

| Bonus criterion | Where it lives in Maestra's flow |
|---|---|
| **Multi-agent coordination** | Apprentice (tactical) + Maestra (strategic) + Cocktail Bar (service-agent) + Aegis (verification-agent) — four-agent collaboration in 90s |
| **Gas abstraction** | Kite Passport two-wallet routing — Maestra never sees gas; Tad never sees Base. Single fund, dual-chain settlement. |
| **Scoped permissions & revocation** | Maestra's ephemeral session key caps spend per cycle, auto-expires, revocable from Passport dashboard. Loop hallucinations cost $1.10 max. |

Visual: three checkmarks with arrows pointing to specific code paths.

---

## Slide 10 — Judging criteria mapping

| Criterion | How we score |
|---|---|
| **Agent Autonomy** | Zero human clicks once Cloud Scheduler triggers. Three transactions per cycle. Passport sessions are the circuit breaker. |
| **Developer Experience** | `docker-compose up` reproduces locally; live demo URL is public and persistent; README maps every spec trait to a code reference; OpenAPI-ready /menu and /dose contracts on the Bar. |
| **Real-World Applicability** | Frontier labs are paying eight figures *today* for training data. Substrate-anchored, biographically-amended, rights-cleared Aeternum Assets are the next-tier substitute. |
| **Novel or creativity** | Cognitive Nutrition Bar is a new primitive: agents pay micropayments for dense-context payloads that scaffold their decision-making. Claude reasoning visible at each decision boundary. |

---

## Slide 11 — Post-Buildathon roadmap

**Immediate (next 30 days):**
- Push live demo to `golden-codex.com/kite-live` (Cloud Run + Firebase Hosting)
- Register the GCX Cocktail Bar on the Kite Agent Marketplace (Stephen A handshake)
- Open Aeternum Sour to public x402 traffic — first 1000 pours at $0.10 each

**90 days — Protocol commitment:**
- **A2A × x402 Permaweb Extension SDK** — middleware so any Kite-attested agent can post AO Amendments without holding AR
- Sigstore JWS response envelopes — cryptographic identity assurance for LLM-callable Lens
- ERC-8004 vetted-sponsor manifest support for the Cocktail Bar

**Post-funding (Q3 2026):**
- **Alexandria Lens** — sub-second Vertex AI Vector Search 2.0 index over the substrate, MCP-discoverable by every major agent stack (full architecture locked in companion lair)
- Museum institutional rail — 1M+ assets at $1/mint, two-rail model (volume tokens + trophy auctions)

Visual: 3-tier timeline.

---

## Slide 12 — Close

> *"Maestra always stops for a cocktail before a big purchase."*
>
> *Settlement is commodity. Cognition is moat. The Bar is open.*

**Maestra.** Built on Kite Passport + x402, bridging Kite's agent economy into the Arweave/AO permanent-state substrate.

**Open source · MIT · `github.com/codex-curator/golden-codex-kite-novel`**

**Live now:** `golden-codex.com/kite-live`

**Reach Tad:** curator@golden-codex.com · `@goldencodex` · Kite Discord `@buildathon-team-tad`

Visual: full-bleed Maestra glyph with the three logos (Metavolve / Kite / Arweave) along the bottom.

---

## Tonal guide (for visual designer or AI-generated slides)

- **Type:** sans-serif body, serif display. Pair: Inter + Cormorant Garamond.
- **Palette:** ink black (#0A0A0A), gold leaf (#C5A05C), cocktail amber (#D89A6E), live-feed green (#00FF6A).
- **Density:** every slide has ONE headline, ONE visual, AND verbal narration. Body text is supporting only.
- **Tone:** "evidence-led, never breathless." Direct. Procurement-strategist voice (matches Maestra's persona).

## Anti-claims (what NOT to say in the deck)

- DO NOT name Microsoft / Meta / NVIDIA / DeepMind judges (unverified — pass-2 claim couldn't be confirmed from public sources). Soften to "Coinbase Ventures + Kite team + industry partners."
- DO NOT promise the Lens is shipped in the demo — it's post-Buildathon Phase 2 (slide 11).
- DO NOT mention the gcx-bar working-tree recovery — internal-only.
- DO NOT claim x402 batch settlement is live (it shipped but we're not using it in the demo); use individual settlement language.

## Sources to drop in the deck appendix

- Kite whitepaper · `https://gokite.ai/kite-whitepaper`
- Encode Club programme page · `https://www.encodeclub.com/programmes/kites-hackathon-ai-agentic-economy`
- The Density Imperative · Zenodo `10.5281/zenodo.20162589`
- The Supervision Tradeoff · Zenodo `10.5281/zenodo.20162594`
- Cognitive Nutrition Architecture · Zenodo `10.5281/zenodo.18667742`
- Aeternum Sour recipe (in repo) · `services/gcx-bar/recipes/aeternum-sour.md`
