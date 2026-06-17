from __future__ import annotations

import json

import yaml

from newsroom.cli.main import _build_packet_for_cluster, main
from newsroom.store.db import (
    add_story_critical_source,
    init_db,
    load_notebook_packet_for_story,
    list_story_critical_sources,
    list_story_critical_source_articles,
    replace_clusters_for_date,
    upsert_article,
    upsert_notebook_packet,
)
from newsroom.store.models import Article, GlossaryTerm, NotebookPacket, SourceRef, StoryCluster


def _article(
    seed: str,
    source_type: str = "official",
    source_role: str | None = None,
    source_pool_id: str | None = None,
) -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Source article {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        source_role=source_role,
        source_pool_id=source_pool_id,
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


def test_packet_critical_list_reads_back_recorded_sources(tmp_path, capsys):
    db_path = tmp_path / "newsroom.sqlite"
    primary = _article("primary", source_type="official")
    critical = _article(
        "critical",
        source_type="commentary",
        source_role="critical_view_candidate",
        source_pool_id="critical_view_candidates",
    )
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    upsert_article(db_path, critical)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])
    add_story_critical_source(
        db_path,
        cluster_id=cluster.id,
        article_id=critical.id,
        note="counter framing",
        created_at="2026-05-18T03:00:00+00:00",
    )

    markdown_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "critical-list",
            "--story",
            cluster.id,
        ]
    )
    markdown_output = capsys.readouterr().out

    assert markdown_exit == 0
    assert f"Critical-view sources for {cluster.id}: 1" in markdown_output
    assert critical.id in markdown_output
    assert "critical_view_candidate" in markdown_output
    assert "counter framing" in markdown_output
    assert "2026-05-18T03:00:00+00:00" in markdown_output
    assert "https://example.com" not in markdown_output

    json_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "critical-list",
            "--story",
            cluster.id,
            "--format",
            "json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert json_exit == 0
    assert payload["critical_view_count"] == 1
    assert payload["critical_views"][0]["article_id"] == critical.id
    assert payload["critical_views"][0]["source_pool_id"] == "critical_view_candidates"
    assert payload["critical_views"][0]["note"] == "counter framing"
    assert payload["critical_views"][0]["recorded_at"] == "2026-05-18T03:00:00+00:00"
    assert "url" not in payload["critical_views"][0]


def test_packet_build_persists_packet_and_show_reads_back(tmp_path, capsys):
    db_path = tmp_path / "newsroom.sqlite"
    packet_root = tmp_path / "packets"
    primary = _article("primary", source_type="official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

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

    persisted = load_notebook_packet_for_story(db_path, cluster.id)
    assert persisted is not None
    assert persisted.story_cluster_id == cluster.id
    assert persisted.primary_sources[0].article_id == primary.id

    show_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "show",
            "--story",
            cluster.id,
        ]
    )
    captured = capsys.readouterr()

    assert show_exit == 0
    assert f"Packet: {persisted.id}" in captured.out
    assert "Primary sources: 1" in captured.out


def test_downstream_packet_helper_reuses_persisted_operator_packet(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    primary = _article("primary", source_type="official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])
    persisted = NotebookPacket(
        id="packet_operator_edited",
        story_cluster_id=cluster.id,
        primary_sources=[
            SourceRef(
                article_id=primary.id,
                url=primary.url,
                title=primary.title,
                source_name=primary.source_name,
                source_type=primary.source_type,
                published_at=primary.published_at,
            )
        ],
        news_sources=[],
        critical_views=[],
        timeline=[],
        glossary=[GlossaryTerm(term="operator-term", definition="edited")],
        questions=["operator-edited packet question"],
        format_hint="anchor",
        export_dir=str(tmp_path / "packets" / "packet_operator_edited"),
        created_at="2026-05-18T04:00:00+00:00",
    )
    upsert_notebook_packet(db_path, persisted)

    packet = _build_packet_for_cluster(
        db_path,
        cluster,
        [primary],
        "missing-series.yml",
        packet_root=tmp_path / "packets",
    )

    assert packet.id == persisted.id
    assert packet.questions == ["operator-edited packet question"]
    assert packet.glossary == [GlossaryTerm(term="operator-term", definition="edited")]


def test_downstream_packet_helper_merges_new_critical_source_into_persisted_packet(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    primary = _article("primary", source_type="official")
    critical = _article("critical", source_type="official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    upsert_article(db_path, critical)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])
    persisted = NotebookPacket(
        id="packet_operator_edited",
        story_cluster_id=cluster.id,
        primary_sources=[],
        news_sources=[],
        critical_views=[],
        timeline=[],
        glossary=[],
        questions=["operator-edited packet question"],
        format_hint="anchor",
        export_dir=str(tmp_path / "packets" / "packet_operator_edited"),
        created_at="2026-05-18T04:00:00+00:00",
    )
    upsert_notebook_packet(db_path, persisted)
    add_story_critical_source(
        db_path,
        cluster_id=cluster.id,
        article_id=critical.id,
        note="risk framing",
        created_at="2026-05-18T05:00:00+00:00",
    )

    packet = _build_packet_for_cluster(
        db_path,
        cluster,
        [primary],
        "missing-series.yml",
        packet_root=tmp_path / "packets",
    )

    assert packet.id == persisted.id
    assert packet.questions == ["operator-edited packet question"]
    assert [ref.article_id for ref in packet.critical_views] == [critical.id]
    reloaded = load_notebook_packet_for_story(db_path, cluster.id)
    assert reloaded is not None
    assert [ref.article_id for ref in reloaded.critical_views] == [critical.id]


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
    critical_records = list_story_critical_sources(db_path, cluster.id)
    assert critical_records[0].note == "updated note"
    assert critical_records[0].created_at == "2026-05-18T04:00:00+00:00"


def test_export_rebuild_prefers_refreshed_review_manifest_roots(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    script_root = tmp_path / "scripts"
    roots = {
        "visual": tmp_path / "visuals",
        "asset": tmp_path / "assets",
        "quote": tmp_path / "quotes",
        "export": tmp_path / "exports",
    }
    export_root = tmp_path / "exports"
    primary = _article("primary", source_type="official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])

    _assert_main(
        db_path,
        "script",
        "draft",
        "--story",
        cluster.id,
        "--format",
        "anchor",
        "--script-root",
        str(script_root),
    )
    script_id = next(script_root.iterdir()).name
    _run_review_pipeline(db_path, script_id, roots)

    add_exit = main(
        [
            "--db",
            str(db_path),
            "packet",
            "add-critical",
            "--story",
            cluster.id,
            "--url",
            "https://example.com/nist",
            "--title",
            "NIST Generative AI Profile",
            "--source-name",
            "NIST",
            "--source-type",
            "official",
            "--note",
            "risk framing",
        ]
    )
    assert add_exit == 0

    _assert_main(
        db_path,
        "script",
        "draft",
        "--story",
        cluster.id,
        "--format",
        "anchor",
        "--script-root",
        str(script_root),
    )
    _run_review_pipeline(db_path, script_id, roots)

    episode_dir = next(export_root.iterdir())
    exported_quote_manifest = yaml.safe_load(
        (episode_dir / "quote_manifest.yml").read_text(encoding="utf-8")
    )
    attributions = [
        quote["attribution"]
        for quote in exported_quote_manifest["quotes"]
        if isinstance(quote, dict)
    ]
    assert any("NIST" in attribution for attribution in attributions)


def _run_review_pipeline(db_path, script_id: str, roots: dict[str, object]) -> None:
    _assert_main(
        db_path,
        "visual",
        "plan",
        "--script",
        script_id,
        "--visual-root",
        str(roots["visual"]),
    )
    _assert_main(
        db_path,
        "asset",
        "suggest",
        "--script",
        script_id,
        "--asset-root",
        str(roots["asset"]),
    )
    _assert_main(
        db_path,
        "quote",
        "suggest",
        "--script",
        script_id,
        "--quote-root",
        str(roots["quote"]),
    )
    _assert_main(
        db_path,
        "export",
        "ymm4",
        "--script",
        script_id,
        "--export-root",
        str(roots["export"]),
        "--asset-root",
        str(roots["asset"]),
        "--quote-root",
        str(roots["quote"]),
    )


def _assert_main(db_path, *args: str) -> None:
    assert main(["--db", str(db_path), *args]) == 0
