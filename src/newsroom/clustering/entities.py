from __future__ import annotations


ENTITY_TERMS: dict[str, tuple[str, ...]] = {
    "microsoft": ("microsoft", "msft"),
    "copilot": ("copilot",),
    "office": ("office", "outlook", "teams"),
    "google": ("google", "alphabet"),
    "youtube": ("youtube",),
    "workspace": ("workspace",),
    "openai": ("openai",),
    "chatgpt": ("chatgpt", "gpt"),
    "anthropic": ("anthropic",),
    "claude": ("claude",),
    "meta": ("meta", "facebook", "instagram", "threads"),
    "apple": ("apple", "iphone", "ipad", "macos"),
    "x_twitter": ("twitter", "x.com"),
    "tiktok": ("tiktok",),
    "amazon": ("amazon", "aws"),
    "github": ("github",),
}


def extract_entities(text: str) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    hits: list[str] = []
    for entity, aliases in ENTITY_TERMS.items():
        for alias in aliases:
            if alias in lowered:
                hits.append(entity)
                break
    return hits
