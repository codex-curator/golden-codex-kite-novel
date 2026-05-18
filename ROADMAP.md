# ROADMAP.md — What ships next

This repo is the **Kite Buildathon Novel Track submission state**. The following
items are intentionally deferred to post-submission so the demo stays clean and
reproducible. Each line is a real next ship, not aspirational marketing.

## Q2 2026 — immediately post-Buildathon

### Pluggable `ModelAdapter` (model-agnostic core)
- **Why**: Today `CLAUDE_MODEL` lets you swap Anthropic models. Real model-portability means swapping providers — Llama 4 via Together, Qwen via Replicate, Gemini via Vertex, GPT via OpenAI, local Ollama.
- **Shape**: `agents/maestra/model_adapter.py` with `LLM_PROVIDER` + `LLM_MODEL` env-var matrix. Maestra reasoning loop is provider-agnostic; only `model_adapter.infer()` changes.
- **Cocktail bar already model-agnostic** — recipes are dense-context bundles served as raw markdown. Any model can consume them.

### MCP server wrapper for the Cocktail Bar
- **Why**: The bar is already Smithery-discoverable in spirit (a public x402 merchant) but not yet an MCP-protocol resource. Wrap `/menu` + `/dose` as MCP tools so any MCP-capable client (Claude Desktop, Cline, Continue, etc.) can order directly.
- **Shape**: `services/gcx-bar/mcp-server.py` — exposes `list_cocktails`, `order_cocktail(slug)` as MCP tools. Same backing service, additional protocol surface.

### Azure Container Instances parity guide
- **Why**: Buildathon submission deploys on GCP Cloud Run; production should run anywhere. Microsoft-aligned shops want Azure parity.
- **Shape**: `docs/deploy-azure.md` — env-var equivalents, ACI deployment script, Azure Key Vault for `KITE_PASSPORT_JWT`, OIDC federation pattern. Mirror exists for AWS Fargate.

### Atlas `hash_index.py` open-source release
- **Why**: The LSH 16×4-band indexing pattern that scales Aegis verification to 100K+ assets is currently private (in `golden_codex_pipeline/agents/atlas-agent/`). Generalizable; should be public.
- **Shape**: New repo `codex-curator/atlas-hash-index` — BSD-3-Clause, Python package, with a worked example and benchmark.

### Live demo manifest JSON contract
- **Why**: `public/live-demo-manifest.json` (over in golden-codex-website) drives the replay page. The JSON contract is currently undocumented.
- **Shape**: JSON schema + examples published as `docs/manifest-schema.md` so anyone can fork the replay page for their own agent demo.

### Kite Demo React components (live page source)
- **Why**: `golden-codex.com/kite-demo` is the canonical live demo. Components currently live in the private website repo.
- **Shape**: Extract `src/components/KiteDemo/` + `src/pages/KiteDemoPage.jsx` into this repo under `web/kite-demo/`, with a `pnpm dev` quickstart.

## Q3 2026

### Pour signing + soulmark
- **Why**: Today a pour is a JSON response. To make pours non-fungible artifacts, sign each pour with a C2PA-style manifest (issuer = bar, soulmark = SHA-256(content + tx_hash)). Then any LLM downstream can verify the pour came from this bar at this time for this price.
- **Shape**: `services/gcx-bar/pour_signer.py`.

### Cocktail-feedback loop → Firestore
- **Why**: The live demo's cocktail-feedback widget already collects judge taste-ratings; backend writes are currently blocked by Firestore rules. Wire a Cloud Function fallback or open the security rule with rate-limiting.
- **Shape**: `services/cocktail-feedback-fn/` Cloud Function + Firestore rule.

### Frontier-lab fingerprint audit (research artifact)
- **Why**: Recipes contain authored content acknowledging the lab whose model they're tuned for (Claudesmopolitan ← Anthropic, Gemini Gimlet ← Google, Grok-tini ← xAI, Lucid Lantern ← OpenAI, Llama Libre ← Meta, Copilot Clarity Cooler ← Microsoft). Run a measured ablation showing per-lab performance lift per pour.
- **Shape**: Companion paper extending the Cognitive Nutrition framework (DOI 10.5281/zenodo.18667742).

## What stays proprietary (out of scope for open-sourcing)

- **Aegis full source** — C2PA + LSH 16×4 registry stays in `golden_codex_pipeline/agents/aegis-agent/`. The kite-novel repo calls it as a service.
- **Golden Codex Schema** — NEST 111-field definition + pigment library + provenance lineage. The competitive moat.
- **Nova system instructions** — Gemini prompts for asset enrichment. Proprietary artisan IP.
- **Artiswa persona** — GPT-4o curator persona file. Proprietary operational knowledge.
- **Curation pipeline orchestration** — `services/campaign-orchestrator/`, the 6-stage value chain that turns raw generations into Aeternum Assets.

## How to propose a roadmap addition

Open a GitHub issue with the `roadmap` label. Reasoning that helps:
- What it unlocks for users of this repo
- Whether it preserves the permissionless-merchant pattern
- What proprietary boundary it does or doesn't cross
