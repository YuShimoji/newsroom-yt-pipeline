from __future__ import annotations

from newsroom.store.models import Article


def competitor_ratio(articles: list[Article]) -> float:
    """Fraction of articles tagged as competitor sources within a group."""
    if not articles:
        return 0.0
    competitor_count = sum(1 for article in articles if article.source_type == "competitor")
    return competitor_count / len(articles)
