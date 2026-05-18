from __future__ import annotations

from newsroom.scoring.topic_scorer import TopicScorer
from newsroom.store.models import Article, StoryCluster


def _make_article(seed: str, source_type: str = "news") -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Headline {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        published_at="2026-05-18T01:00:00+00:00",
        fetched_at="2026-05-18T02:00:00+00:00",
    )


def _make_cluster(article_ids: list[str]) -> StoryCluster:
    return StoryCluster(
        id="story_test_001",
        title="Test cluster",
        summary=None,
        article_ids=article_ids,
        primary_sources=[],
        related_series=[],
        entities=[],
        content_farm_overlap=0.0,
        cluster_date="2026-05-18",
        created_at="2026-05-18T02:00:00+00:00",
        updated_at="2026-05-18T02:00:00+00:00",
    )


def test_score_cluster_is_deterministic():
    articles = [_make_article("a", source_type="official"), _make_article("b"), _make_article("c")]
    cluster = _make_cluster([article.id for article in articles])

    scorer = TopicScorer()
    first = scorer.score_cluster(cluster, articles)
    second = scorer.score_cluster(cluster, articles)

    assert first.score_total == second.score_total
    assert first.components == second.components
