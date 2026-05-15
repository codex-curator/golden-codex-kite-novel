"""
GCX Bar cocktail registry.

Each entry maps a slug to display metadata and a recipe file path.
Recipe content is loaded lazily so the menu endpoint stays fast.
"""
from __future__ import annotations

from pathlib import Path

RECIPES_DIR = Path(__file__).parent / "recipes"

COCKTAILS = {
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
        "pairs_with": "Metavolve research sessions · paper-and-experiment hybrid work",
        "recipe_file": "double-density-martini.md",
    },
    "einstein-spritzer": {
        "name": "Einstein Spritzer",
        "category": "academic",
        "tagline": "Citation-heavy, primary-source forward, sparkling historiography.",
        "token_budget": 48_000,
        "price_usd": 0.10,
        "pairs_with": "TMLR · NeurIPS · ICLR submissions · grant drafting",
        "recipe_file": "einstein-spritzer.md",
    },
    "prose-daiquiri": {
        "name": "Prose Daiquiri",
        "category": "fiction",
        "tagline": "Sweet, balanced, literary-voice forward.",
        "token_budget": 40_000,
        "price_usd": 0.10,
        "pairs_with": "NaNoWriMo · novel drafts · screenplay sessions",
        "recipe_file": "prose-daiquiri.md",
    },
    "claudesmopolitan": {
        "name": "Claudesmopolitan",
        "category": "coding",
        "tagline": "Strong architectural stamina, bitter with edge cases, clean finish.",
        "token_budget": 60_000,
        "price_usd": 0.25,
        "pairs_with": "6-hour build sessions · production rewrites · migration projects",
        "recipe_file": "claudesmopolitan.md",
    },
    "boulevardier": {
        "name": "Founder's Boulevardier",
        "category": "investor-pitch",
        "tagline": "Heavy, memorable, long finish, slight burn.",
        "token_budget": 50_000,
        "price_usd": 0.25,
        "pairs_with": "Y Combinator · seed raises · strategic partnership opens",
        "recipe_file": "boulevardier.md",
    },
    "socratic": {
        "name": "The Socratic",
        "category": "coaching",
        "tagline": "Question-first, minimal assertion, let the student arrive.",
        "token_budget": 24_000,
        "price_usd": 0.05,
        "pairs_with": "New-hire onboarding · intro teaching · executive coaching",
        "recipe_file": "socratic.md",
    },
    "old-fashioned": {
        "name": "Reviewer's Old Fashioned",
        "category": "adversarial-review",
        "tagline": "Double bitters, no sweetener, orange peel of dissent.",
        "token_budget": 32_000,
        "price_usd": 0.10,
        "pairs_with": "Pre-submission stress test of papers, proposals, pitches",
        "recipe_file": "old-fashioned.md",
    },
    "nova-collins": {
        "name": "The Nova Collins",
        "category": "image-prompts",
        "tagline": "Cinematic-grade visual reasoning, Artiswa-tuned.",
        "token_budget": 36_000,
        "price_usd": 0.10,
        "pairs_with": "SD 3.5 · DALL-E · Midjourney · Veo prompt engineering",
        "recipe_file": "nova-collins.md",
    },
    "verifiers-neat": {
        "name": "The Verifier's Neat",
        "category": "formal-verification",
        "tagline": "Pure verifier-grounded, zero judge-scored content.",
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
