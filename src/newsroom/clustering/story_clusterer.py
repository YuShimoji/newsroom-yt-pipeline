from __future__ import annotations

import re
from datetime import UTC, datetime
from hashlib import sha256

from newsroom.clustering.entities import extract_entities
from newsroom.store.models import Article, StoryCluster


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at",
        "for", "by", "with", "from", "is", "are", "was", "were", "be", "been",
        "has", "have", "had", "do", "does", "did", "this", "that", "these",
        "those", "it", "its", "as", "if", "than", "then", "so", "into", "via",
        "via", "vs", "new", "news", "report",
    }
)


def tokenize_title(title: str) -> set[str]:
    lowered = title.lower()
    return {token for token in _TOKEN_PATTERN.findall(lowered) if token not in _STOPWORDS and len(token) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    if intersection == 0:
        return 0.0
    return intersection / len(a | b)


def similarity(article_a: Article, article_b: Article) -> float:
    """Combined title-token Jaccard with an entity-overlap bonus.

    A shared entity between two titles is a strong signal that two
    different headlines refer to the same story, so the entity overlap is
    blended with the token Jaccard before the threshold check.
    """
    tokens_a = tokenize_title(article_a.title)
    tokens_b = tokenize_title(article_b.title)
    token_score = jaccard(tokens_a, tokens_b)

    entities_a = set(extract_entities(article_a.title))
    entities_b = set(extract_entities(article_b.title))
    if entities_a and entities_b:
        entity_score = jaccard(entities_a, entities_b)
    else:
        entity_score = 0.0

    return 0.7 * token_score + 0.3 * entity_score


class StoryClusterer:
    """Group daily articles by title-token similarity and shared entities."""

    def __init__(self, threshold: float = 0.4) -> None:
        self.threshold = threshold

    def cluster(self, articles: list[Article], cluster_date: str) -> list[StoryCluster]:
        if not articles:
            return []

        parents = list(range(len(articles)))

        def find(node: int) -> int:
            while parents[node] != node:
                parents[node] = parents[parents[node]]
                node = parents[node]
            return node

        def union(left: int, right: int) -> None:
            root_left = find(left)
            root_right = find(right)
            if root_left != root_right:
                parents[root_right] = root_left

        for i in range(len(articles)):
            for j in range(i + 1, len(articles)):
                if similarity(articles[i], articles[j]) >= self.threshold:
                    union(i, j)

        groups: dict[int, list[int]] = {}
        for index in range(len(articles)):
            root = find(index)
            groups.setdefault(root, []).append(index)

        now = datetime.now(UTC).isoformat()
        clusters: list[StoryCluster] = []
        for indices in groups.values():
            members = [articles[i] for i in indices]
            clusters.append(_build_cluster(members, cluster_date, now))

        clusters.sort(key=lambda c: (-len(c.article_ids), c.title))
        return clusters


def _build_cluster(members: list[Article], cluster_date: str, now: str) -> StoryCluster:
    sorted_members = sorted(members, key=lambda a: (a.published_at or "", a.title))
    representative = sorted_members[0]

    article_ids = [article.id for article in sorted_members]
    primary_sources = sorted(
        {
            article.source_name
            for article in members
            if article.source_type in {"official", "news"}
        }
    )
    if not primary_sources:
        primary_sources = sorted({article.source_name for article in members})

    related_series = sorted(
        {
            tag
            for article in members
            for tag in article.tags
            if tag.startswith("series/")
        }
    )

    entities = sorted(
        {entity for article in members for entity in extract_entities(article.title)}
    )

    competitor_count = sum(1 for a in members if a.source_type == "competitor")
    content_farm_overlap = competitor_count / max(len(members), 1)

    digest_seed = "|".join(sorted(article_ids)) + f"|{cluster_date}"
    digest = sha256(digest_seed.encode("utf-8")).hexdigest()[:16]

    return StoryCluster(
        id=f"story_{cluster_date.replace('-', '')}_{digest}",
        title=representative.title,
        summary=None,
        article_ids=article_ids,
        primary_sources=primary_sources,
        related_series=related_series,
        entities=entities,
        content_farm_overlap=round(content_farm_overlap, 4),
        cluster_date=cluster_date,
        created_at=now,
        updated_at=now,
    )
