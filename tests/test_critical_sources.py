from __future__ import annotations

import json

from newsroom.cli.main import main
from newsroom.store.db import (
    add_story_critical_source,
    init_db,
    list_story_critical_source_articles,
    replace_clusters_for_date,
    upsert_article,
)
from newsroom.store.models import Article, StoryCluster


def _article(seed: str, source_type: str = "official") -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Source article {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        published_at="2026-05-18T01:00:00+00:00",
        fetched_at="2026-05-18T02:00:00+00:00",
    )


def _cluster(article: Article) -> StoryCluster:
    return StoryCluster(
        id="story_20260518_test",
        title="Copilot announcement",
        summary=None,
        article_ids=[article.id],
        primary_sources=[article.source_name],
        related_series=[],
        entities=[],
        content_farm_overlap=0.0,
        cluster_date="2026-05-18",
        created_at="2026-05-18T02:00:00+00:00",
        updated_at="2026-05-18T02:00:00+00:00",
    )


def test_packet_add_critical_manual_source_flows_into_packet_artifact(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    packet_root = tmp_path / "packets"
    primary = _article("primary", source_type="official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

    add_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "add-critical",
            "--story",
            cluster.id,
            "--url",
            "https://example.com/critical",
            "--title",
            "Critical analysis",
            "--source-name",
            "Independent Analyst",
            "--source-type",
            "commentary",
            "--note",
            "skeptical counterpoint",
        ]
    )
    assert add_exit == 0

    build_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "build",
            "--story",
            cluster.id,
            "--packet-root",
            str(packet_root),
        ]
    )
    assert build_exit == 0

    packet_dirs = list(packet_root.iterdir())
    assert len(packet_dirs) == 1
    sources = json.loads((packet_dirs[0] / "sources.json").read_text(encoding="utf-8"))
    assert sources["critical_views"][0]["source_name"] == "Independent Analyst"
    assert sources["critical_views"][0]["title"] == "Critical analysis"


def test_packet_add_critical_existing_article_flows_into_packet_artifact(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    packet_root = tmp_path / "packets"
    primary = _article("primary", source_type="official")
    critical = _article("critical", source_type="news")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    upsert_article(db_path, critical)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

    add_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "add-critical",
            "--story",
            cluster.id,
            "--article",
            critical.id,
        ]
    )
    assert add_exit == 0

    build_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "build",
            "--story",
            cluster.id,
            "--packet-root",
            str(packet_root),
        ]
    )
    assert build_exit == 0

    packet_dirs = list(packet_root.iterdir())
    assert len(packet_dirs) == 1
    sources = json.loads((packet_dirs[0] / "sources.json").read_text(encoding="utf-8"))
    assert sources["critical_views"][0]["article_id"] == critical.id
    assert sources["critical_views"][0]["source_name"] == critical.source_name


def test_story_critical_sources_schema_is_idempotent_for_existing_db(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    article = _article("critical", source_type="commentary")
    cluster = _cluster(article)

    init_db(db_path)
    init_db(db_path)
    upsert_article(db_path, article)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])
    add_story_critical_source(
        db_path,
        cluster_id=cluster.id,
        article_id=article.id,
        note="first note",
        created_at="2026-05-18T03:00:00+00:00",
    )
    init_db(db_path)
    add_story_critical_source(
        db_path,
        cluster_id=cluster.id,
        article_id=article.id,
        note="updated note",
        created_at="2026-05-18T04:00:00+00:00",
    )

    critical_sources = list_story_critical_source_articles(db_path, cluster.id)
    assert [source.id for source in critical_sources] == [article.id]
