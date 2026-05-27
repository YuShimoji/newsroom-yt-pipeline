from __future__ import annotations

from dataclasses import replace

from newsroom.clustering.story_clusterer import StoryClusterer
from newsroom.cli.main import main
from newsroom.store.db import (
    list_articles_by_ids,
    list_articles_in_date_range,
    replace_clusters_for_date,
    upsert_article,
)
from newsroom.store.models import Article, StoryCluster


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


def test_multi_day_cluster_members_resolve_by_id(tmp_path):
    db_path = tmp_path / "test.sqlite"
    articles = [
        _article("a", "2026-05-01T01:00:00+00:00"),
        _article("b", "2026-05-05T01:00:00+00:00"),
    ]
    for article in articles:
        upsert_article(db_path, article)

    resolved = list_articles_by_ids(db_path, {article.id for article in articles})

    assert {article.id for article in resolved} == {article.id for article in articles}


def test_script_draft_uses_multi_day_cluster_member_ids(tmp_path):
    db_path = tmp_path / "test.sqlite"
    script_root = tmp_path / "scripts"
    articles = [
        replace(_article("official", "2026-05-01T01:00:00+00:00"), source_type="official"),
        _article("news", "2026-05-05T01:00:00+00:00"),
    ]
    for article in articles:
        upsert_article(db_path, article)

    cluster = StoryCluster(
        id="story_20260526_multiday",
        title="Copilot announcement multi-day",
        summary=None,
        article_ids=[article.id for article in articles],
        primary_sources=[articles[0].source_name],
        related_series=["series/copilot"],
        entities=["copilot"],
        content_farm_overlap=0.0,
        cluster_date="2026-05-26",
        created_at="2026-05-26T00:00:00+00:00",
        updated_at="2026-05-26T00:00:00+00:00",
    )
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

    exit_code = main(
        [
            "--db",
            str(db_path),
            "script",
            "draft",
            "--story",
            cluster.id,
            "--format",
            "anchor",
            "--script-root",
            str(script_root),
        ]
    )

    assert exit_code == 0
    assert list(script_root.iterdir())


def test_script_draft_still_works_for_single_day_cluster(tmp_path):
    db_path = tmp_path / "test.sqlite"
    script_root = tmp_path / "single_day_scripts"
    article = _article("single", "2026-05-26T01:00:00+00:00")
    upsert_article(db_path, article)
    cluster = StoryCluster(
        id="story_20260526_single",
        title="Copilot announcement single day",
        summary=None,
        article_ids=[article.id],
        primary_sources=[article.source_name],
        related_series=["series/copilot"],
        entities=["copilot"],
        content_farm_overlap=0.0,
        cluster_date="2026-05-26",
        created_at="2026-05-26T00:00:00+00:00",
        updated_at="2026-05-26T00:00:00+00:00",
    )
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

    exit_code = main(
        [
            "--db",
            str(db_path),
            "script",
            "draft",
            "--story",
            cluster.id,
            "--format",
            "anchor",
            "--script-root",
            str(script_root),
        ]
    )

    assert exit_code == 0
    assert list(script_root.iterdir())
