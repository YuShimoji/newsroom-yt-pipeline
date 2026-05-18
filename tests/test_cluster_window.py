from __future__ import annotations

from newsroom.clustering.story_clusterer import StoryClusterer
from newsroom.store.db import (
    list_articles_in_date_range,
    upsert_article,
)
from newsroom.store.models import Article


def _article(seed: str, published_at: str) -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Copilot announcement {seed}",
        source_name=f"Source {seed}",
        source_type="news",
        published_at=published_at,
        fetched_at="2026-05-18T12:00:00+00:00",
    )


def test_list_articles_in_date_range_includes_endpoints(tmp_path):
    db_path = tmp_path / "test.sqlite"
    a = _article("a", "2026-05-08T01:00:00+00:00")
    b = _article("b", "2026-04-28T01:00:00+00:00")
    c = _article("c", "2026-03-09T01:00:00+00:00")
    upsert_article(db_path, a)
    upsert_article(db_path, b)
    upsert_article(db_path, c)

    in_range = list_articles_in_date_range(db_path, "2026-04-01", "2026-05-08")
    ids = {article.id for article in in_range}
    assert ids == {a.id, b.id}


def test_list_articles_in_date_range_handles_single_day(tmp_path):
    db_path = tmp_path / "test.sqlite"
    a = _article("a", "2026-04-28T01:00:00+00:00")
    b = _article("b", "2026-04-29T01:00:00+00:00")
    upsert_article(db_path, a)
    upsert_article(db_path, b)

    same_day = list_articles_in_date_range(db_path, "2026-04-28", "2026-04-28")
    assert {article.id for article in same_day} == {a.id}


def test_clusterer_groups_multi_day_articles_into_one_cluster(tmp_path):
    """Multi-day window should let related articles on different days merge."""
    articles = [
        _article("a", "2026-05-01T01:00:00+00:00"),  # Copilot
        _article("b", "2026-05-05T01:00:00+00:00"),  # Copilot
        Article.create(
            url="https://example.com/x",
            title="Apple announces new iPad release",
            source_name="Apple Newsroom",
            source_type="official",
            published_at="2026-05-03T01:00:00+00:00",
            fetched_at="2026-05-18T12:00:00+00:00",
        ),
    ]

    clusters = StoryClusterer(threshold=0.4).cluster(articles, "2026-05-08")
    multi = [c for c in clusters if len(c.article_ids) > 1]
    assert len(multi) == 1
    assert multi[0].cluster_date == "2026-05-08"
    assert len(multi[0].article_ids) == 2
