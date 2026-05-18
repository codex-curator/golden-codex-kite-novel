# Cocktail Recipes — Cognitive Nutrition Bar

This directory contains the 14 fully-authored cocktail recipes served by the
GCX Bar. Each recipe is a **dense-context bundle** — a single Markdown file,
typically 8K–55K tokens, that primes a calling LLM on a specific kind of work.

A recipe is **not** a fine-tune, **not** RAG, **not** a prompt template. It's
a one-shot session-level structured payload — *Ephemeral Structured Elicitation*
in the formal terminology of the framework paper.

## License + attribution

All recipes are released under the same **MIT License** as the rest of this
repository. Authored by **Metavolve Labs, Inc.** Use, fork, and remix freely.

When you fork a recipe or build on the pattern, the following two citations
keep the framework attributable upstream:

- **The Density Imperative** — Zenodo [10.5281/zenodo.20162589](https://doi.org/10.5281/zenodo.20162589)
  Empirical demonstration that dense, structured context elevates reasoning where sparse data degrades it.
- **The Supervision Tradeoff** — Zenodo [10.5281/zenodo.20162594](https://doi.org/10.5281/zenodo.20162594)
  Structural mechanism determining when session-level context injection beats weight-update fine-tuning.

And, if relevant to your work, the broader Cognitive Nutrition framework:
- **Cognitive Nutrition** — Zenodo [10.5281/zenodo.18667742](https://doi.org/10.5281/zenodo.18667742)

## The menu

| Recipe | Purpose | Hero lab |
|---|---|---|
| `aeternum-sour.md` | Provenance authentication (NEST 111-Field + XRF pigment chronology) | — |
| `double-density-martini.md` | Unbounded research synthesis | — |
| `einstein-spritzer.md` | Physics + first-principles reasoning | — |
| `prose-daiquiri.md` | Long-form writing — contains SDKF formal spec | — |
| `negotiators-manhattan.md` | Multi-party negotiation modeling | — |
| `founders-boulevardier.md` | Startup operating decisions | — |
| `old-fashioned.md` | Code review and refactor judgment | — |
| `the-socratic.md` | Step-by-step pedagogical breakdown | — |
| `claudesmopolitan.md` | Anthropic-flavored reasoning | Anthropic |
| `gemini-gimlet.md` | Multimodal forensic triangulation | Google |
| `grok-tini.md` | Wry irreverent first-principles | xAI |
| `lucid-lantern.md` | "No sentence may remain merely beautiful" — narrative discipline | OpenAI |
| `llama-libre.md` | On-device-executable + contains CRDF formal spec | Meta |
| `copilot-clarity-cooler.md` | Code-as-spec + IDE-aware reasoning | Microsoft |

## How to order a pour

```bash
# Public menu — no auth, no payment
curl https://gcx-bar-172867820131.us-west1.run.app/menu | jq

# Order a pour — first hit returns x402 v2 402 + payment-required envelope
curl -v "https://gcx-bar-172867820131.us-west1.run.app/dose?cocktail=aeternum-sour"

# Re-submit with X-Payment header (EIP-712 TransferWithAuthorization, base64)
curl -H "X-Payment: <base64-envelope>" \
     "https://gcx-bar-172867820131.us-west1.run.app/dose?cocktail=aeternum-sour"
```

Verified Kite Passport holders pay ½-off Happy Hour — verified locally by the
bar via EIP-712 ecrecover (see `../kite_passport_verify.py`). No Kite catalog
allowlist required: the bar is a **permissionless x402 merchant**.

## Forking a recipe

The recipe format is intentionally minimal:

```markdown
---
slug: my-recipe
name: My Recipe Name
price_usd: 0.25
token_budget: 12000
category: my-category
tagline: One-liner describing what this pour does
pairs_with: ["task-A", "task-B"]
---

# Actual dense-context content here
```

To register your fork with the running bar, add the slug + frontmatter to
`../cocktails.py` and rebuild. Pull requests welcome.
