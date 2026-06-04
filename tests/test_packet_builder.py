from __future__ import annotations

import json

from newsroom.notebook.exporters import write_packet
from newsroom.notebook.packet_builder import NotebookPacketBuilder
from newsroom.store.models import Article, StoryCluster


def _make_article(seed: str, source_type: str = "news", source: str | None = None) -> Article:
    suffix = seed[-1]
    hour_seed = int(suffix) if suffix.isdigit() else 0
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Copilot announcement {seed}",
        source_name=source or f"Source {seed}",
        source_type=source_type,
        published_at=f"2026-05-18T0{hour_seed % 9 + 1}:00:00+00:00",
        fetched_at="2026-05-18T12:00:00+00:00",
        tags=["series/copilot"],
    )


def _make_cluster(articles: list[Article]) -> StoryCluster:
    return StoryCluster(
        id="story_20260518_test",
        title="Copilot announcement",
        summary=None,
        article_ids=[article.id for article in articles],
        primary_sources=[a.source_name for a in articles if a.source_type == "official"],
        related_series=["series/copilot"],
        entities=["microsoft", "copilot"],
        content_farm_overlap=0.0,
        cluster_date="2026-05-18",
        created_at="2026-05-18T12:00:00+00:00",
        updated_at="2026-05-18T12:00:00+00:00",
    )


def test_packet_build_emits_full_artifact_bundle(tmp_path):
    articles = [
        _make_article("a", source_type="official", source="Microsoft Blog"),
        _make_article("b", source_type="news", source="The Verge"),
    ]
    cluster = _make_cluster(articles)

    builder = NotebookPacketBuilder()
    packet = builder.build(cluster, articles, packet_root=tmp_path)
    output_dir = write_packet(packet)

    for filename in ("packet.md", "sources.json", "timeline.md", "glossary.md", "questions.md", "operator_notes.md"):
        assert (output_dir / filename).exists(), f"missing {filename}"

    sources = json.loads((output_dir / "sources.json").read_text(encoding="utf-8"))
    assert sources["story_cluster_id"] == cluster.id
    assert len(sources["primary_sources"]) == 1
    assert sources["primary_sources"][0]["source_name"] == "Microsoft Blog"
    assert len(sources["news_sources"]) == 1

    glossary_text = (output_dir / "glossary.md").read_text(encoding="utf-8")
    assert "microsoft" in glossary_text
    assert "copilot" in glossary_text

    questions_text = (output_dir / "questions.md").read_text(encoding="utf-8")
    assert "Copilot announcement" in questions_text


def test_packet_build_carries_critical_views_into_artifacts(tmp_path):
    articles = [
        _make_article("a", source_type="official", source="Microsoft Blog"),
        _make_article("b", source_type="competitor", source="Rival Blog"),
    ]
    manual_critical = _make_article(
        "manual-critical",
        source_type="commentary",
        source="Independent Analyst",
    )
    cluster = _make_cluster(articles)

    builder = NotebookPacketBuilder()
    packet = builder.build(
        cluster,
        articles,
        packet_root=tmp_path,
        critical_articles=[manual_critical],
    )
    output_dir = write_packet(packet)

    critical_ids = [ref.article_id for ref in packet.critical_views]
    assert critical_ids == [articles[1].id, manual_critical.id]

    sources = json.loads((output_dir / "sources.json").read_text(encoding="utf-8"))
    assert [ref["source_name"] for ref in sources["critical_views"]] == [
        "Rival Blog",
        "Independent Analyst",
    ]

    packet_md = (output_dir / "packet.md").read_text(encoding="utf-8")
    assert "## Critical views" in packet_md
    operator_notes = (output_dir / "operator_notes.md").read_text(encoding="utf-8")
    assert "Critical-view source count: 2" in operator_notes


def test_format_hint_resolves_from_series_index(tmp_path):
    from newsroom.config import Series

    articles = [_make_article("a", source_type="official")]
    cluster = _make_cluster(articles)

    series_index = {
        "copilot": Series(
            id="copilot",
            title="Copilot Watch",
            description="",
            tags=["series/copilot"],
            default_format="yukkuri",
            strategic_question=None,
        )
    }

    builder = NotebookPacketBuilder(series_index=series_index)
    packet = builder.build(cluster, articles, packet_root=tmp_path)
    assert packet.format_hint == "yukkuri"
