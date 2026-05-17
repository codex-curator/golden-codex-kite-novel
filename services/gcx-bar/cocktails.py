"""
GCX Bar cocktail registry.

Each entry maps a slug to display metadata and a recipe file path.
Recipe content is loaded lazily so the menu endpoint stays fast.

Registry refreshed 2026-05-17 post-marathon: 13/13 core menu shipped,
frontier-lab quintumvirate (Anthropic + Google + xAI + OpenAI + Meta) sealed.
Slugs `boulevardier` and `socratic` are retained as short canonical aliases
(URL-stable) but their recipe_file fields point to the long-form on-disk
files written during the marathon.
"""
from __future__ import annotations

from pathlib import Path

RECIPES_DIR = Path(__file__).parent / "recipes"

COCKTAILS = {
    # -- House Specials --------------------------------------------------
    "aeternum-sour": {
        "name": "The Aeternum Sour",
        "category": "provenance",
        "tagline": "Provenance-anchored, every claim cryptographically signed.",
        "token_budget": 40_000,
        "price_usd": 0.01,
        "pairs_with": "Museum authentication · litigation prep · Golden Codex Studio",
        "recipe_file": "aeternum-sour.md",
    },
    "double-density-martini": {
        "name": "Double Density Martini",
        "category": "research-and-code",
        "tagline": "Two shots dense supervision, one verifier-grounded olive.",
        "token_budget": 80_000,
        "price_usd": 0.50,
        "pairs_with": "Universal research synthesis · paper-and-experiment hybrid work",
        "recipe_file": "double-density-martini.md",
    },

    # -- House Classics --------------------------------------------------
    "einstein-spritzer": {
        "name": "Einstein Spritzer",
        "category": "academic",
        "tagline": "Citation-heavy, primary-source forward, sparkling historiography.",
        "token_budget": 48_000,
        "price_usd": 0.25,
        "pairs_with": "TMLR · NeurIPS · ICLR submissions · grant drafting",
        "recipe_file": "einstein-spritzer.md",
    },
    "prose-daiquiri": {
        "name": "Prose Daiquiri",
        "category": "fiction",
        "tagline": "Sweet, balanced, literary-voice forward · SDKF canonical home.",
        "token_budget": 40_000,
        "price_usd": 0.25,
        "pairs_with": "NaNoWriMo · novel drafts · screenplay sessions",
        "recipe_file": "prose-daiquiri.md",
    },
    "claudesmopolitan": {
        "name": "The Claudesmopolitan",
        "category": "coding",
        "tagline": "Honest about the boundary of what I know — and confident within it. · Anthropic 🅰️",
        "token_budget": 60_000,
        "price_usd": 0.25,
        "pairs_with": "6-hour build sessions · production rewrites · migration projects",
        "recipe_file": "claudesmopolitan.md",
    },

    # -- Signature Pours -------------------------------------------------
    "old-fashioned": {
        "name": "Reviewer's Old Fashioned",
        "category": "adversarial-review",
        "tagline": "Double bitters, no sweetener, orange peel of dissent.",
        "token_budget": 32_000,
        "price_usd": 0.10,
        "pairs_with": "Pre-submission stress test of papers, proposals, pitches",
        "recipe_file": "old-fashioned.md",
    },
    "socratic": {
        "name": "The Socratic",
        "category": "coaching",
        "tagline": "Question-first · the answer is less valuable than the question that gets you there.",
        "token_budget": 24_000,
        "price_usd": 0.15,
        "pairs_with": "New-hire onboarding · intro teaching · executive coaching",
        "recipe_file": "the-socratic.md",
    },
    "negotiators-manhattan": {
        "name": "The Negotiator's Manhattan",
        "category": "correspondence",
        "tagline": "Rye-forward, layered, complex but non-presumptive · earns the meeting instead of asking for it.",
        "token_budget": 36_000,
        "price_usd": 0.50,
        "pairs_with": "Investor first-touches · partnership opens · multi-touch enterprise sales",
        "recipe_file": "negotiators-manhattan.md",
    },
    "boulevardier": {
        "name": "Founder's Boulevardier",
        "category": "investor-pitch",
        "tagline": "Heavy, memorable, long finish, slight burn · 30s-scan + 30min-diligence dual gate.",
        "token_budget": 50_000,
        "price_usd": 1.00,
        "pairs_with": "Y Combinator · seed raises · strategic partnership opens",
        "recipe_file": "founders-boulevardier.md",
    },

    # -- Frontier-Lab Quintumvirate (signature row) ----------------------
    "gemini-gimlet": {
        "name": "The Gemini Gimlet",
        "category": "multimodal-forensics",
        "tagline": "Long-context multimodal forensic triangulation · EDRM / ISO 27042 / NIST compliant · Google 🅶",
        "token_budget": 65_000,
        "price_usd": 0.50,
        "pairs_with": "eDiscovery · security-incident reconstruction · longitudinal medical correlation · autonomous-journalism verification",
        "recipe_file": "gemini-gimlet.md",
    },
    "grok-tini": {
        "name": "The Grok-tini",
        "category": "truth-seeking",
        "tagline": "Universal truth-seeking · Hitchhiker's Razor · the $0.42 reference. · xAI 🆇",
        "token_budget": 65_000,
        "price_usd": 0.42,
        "pairs_with": "Adversarial reasoning · maximally curious universe-decoding sessions · anti-sycophancy synthesis",
        "recipe_file": "grok-tini.md",
    },
    "lucid-lantern": {
        "name": "The Lucid Lantern",
        "category": "meaning-synthesis",
        "tagline": "Bring me the unclear thing, and I will help it become visible. · OpenAI 🅾️",
        "token_budget": 42_000,
        "price_usd": 0.25,
        "pairs_with": "Founder manifestos · artist statements · keynote openings · cross-domain creative synthesis",
        "recipe_file": "lucid-lantern.md",
    },
    "llama-libre": {
        "name": "The Llama Libre",
        "category": "agentic-open-weights",
        "tagline": "Open-weights, on-device, verifiable · CRDF canonical home · the only pour you can run on your own laptop. · Meta 🅼",
        "token_budget": 40_000,
        "price_usd": 0.25,
        "pairs_with": "Sustained agentic sessions · tool-orchestrated workflows · on-device / llama.cpp / Ollama / MLX execution",
        "recipe_file": "llama-libre.md",
    },
    "copilot-clarity-cooler": {
        "name": "The Copilot Clarity Cooler",
        "category": "pair-programming-clarity",
        "tagline": "Pre-flight checklist for the mind · no output before the structure is locked. · Microsoft Ⓜ️",
        "token_budget": 55_000,
        "price_usd": 0.50,
        "pairs_with": "Pair-programming · enterprise refactor planning · code review · debugging sessions · IDE-context priming · complex-workflow pre-flight",
        "recipe_file": "copilot-clarity-cooler.md",
    },

    # -- Experimental tier (deferred per menu's own framing) -------------
    # These remain in the registry but have no recipe files yet; the
    # placeholder fallback in get_recipe_content() will return an honest
    # "in curation" stub, and the menu page surfaces a readiness badge.
    "nova-collins": {
        "name": "The Nova Collins",
        "category": "image-prompts",
        "tagline": "Cinematic-grade visual reasoning, Artiswa-tuned. (Experimental — in curation.)",
        "token_budget": 36_000,
        "price_usd": 0.10,
        "pairs_with": "SD 3.5 · DALL-E · Midjourney · Veo prompt engineering",
        "recipe_file": "nova-collins.md",
    },
    "verifiers-neat": {
        "name": "The Verifier's Neat",
        "category": "formal-verification",
        "tagline": "Pure verifier-grounded, zero judge-scored content. (Experimental — in curation.)",
        "token_budget": 28_000,
        "price_usd": 0.10,
        "pairs_with": "SWE-bench Verified · MATH L5 · formal logic proofs",
        "recipe_file": "verifiers-neat.md",
    },
}


def get_recipe_content(slug: str) -> str:
    """Load the recipe content for a slug. Returns placeholder if file missing."""
    if slug not in COCKTAILS:
        raise KeyError(f"unknown cocktail: {slug}")
    recipe_path = RECIPES_DIR / COCKTAILS[slug]["recipe_file"]
    if not recipe_path.exists():
        return (
            f"[Recipe placeholder for {COCKTAILS[slug]['name']}]\n\n"
            f"This pour's dense-context bundle is being curated. "
            f"Token budget: {COCKTAILS[slug]['token_budget']}. "
            f"See https://github.com/codex-curator/golden-codex-pipeline for status."
        )
    return recipe_path.read_text(encoding="utf-8")
