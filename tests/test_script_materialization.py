from __future__ import annotations

import yaml

from newsroom.adapters.export_inspector import inspect_episode_bundle
from newsroom.adapters.ymm4_export import build_ymm4_package
from newsroom.cli.main import main
from newsroom.script.materialization import (
    build_materialization_payload,
    write_materialization_draft,
)
from newsroom.store.db import add_story_critical_source, replace_clusters_for_date, upsert_article
from newsroom.store.models import (
    Article,
    Chapter,
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    SourceRef,
    StoryCluster,
)


def _source_ref(seed: str, source_type: str) -> SourceRef:
    return SourceRef(
        article_id=f"article_{seed}",
        url=f"https://example.com/{seed}",
        title=f"Source {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        published_at="2026-06-01T00:00:00+00:00",
    )


def _plan() -> EpisodePlan:
    return EpisodePlan(
        id="plan_materialize_test",
        story_cluster_id="story_materialize_test",
        series_id=None,
        title_candidates=["AI systems"],
        thumbnail_angles=["system view"],
        hook="hook",
        chapter_outline=[
            Chapter(
                id="plan_materialize_test__intro",
                title="導入",
                intent="論点を提示する",
                target_duration_sec=60,
            )
        ],
        target_duration_sec=60,
        viewer_utility="判断材料",
        risk_notes=[],
        approval_state="draft",
        created_at="2026-06-01T00:00:00+00:00",
    )


def _script() -> ScriptIR:
    return ScriptIR(
        id="script_materialize_test",
        episode_plan_id="plan_materialize_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_intro",
                chapter_id="plan_materialize_test__intro",
                speaker="ナレーター",
                text="TODO[plan_materialize_test__intro#0]: operator が記入する。",
                source_refs=["article_primary", "article_critical"],
                visual_refs=["visual:intro"],
                claim_type="instruction",
                needs_human_review=True,
            )
        ],
        created_at="2026-06-01T00:01:00+00:00",
    )


def _packet() -> NotebookPacket:
    return NotebookPacket(
        id="packet_materialize_test",
        story_cluster_id="story_materialize_test",
        primary_sources=[_source_ref("primary", "official")],
        news_sources=[],
        critical_views=[_source_ref("critical", "official")],
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_materialize_test",
        created_at="2026-06-01T00:02:00+00:00",
    )


def test_materialization_payload_preserves_operator_edit_fields():
    payload = build_materialization_payload(_plan(), _script(), _packet())

    segment = payload["segments"][0]
    assert payload["mode"] == "operator_draft"
    assert "does_not_modify_script_csv" in payload["non_goals"]
    assert segment["speaker"] == "ナレーター"
    assert segment["current_text"].startswith("TODO[")
    assert segment["source_refs"] == ["article_primary", "article_critical"]
    assert segment["critical_refs"] == ["article_critical"]
    assert segment["operator_fill"] == ""
    assert segment["human_review_required"] is True
    assert payload["source_catalog"]["article_critical"]["role"] == "critical"


def test_materialization_draft_does_not_clear_export_todo_warning(tmp_path):
    export_dir, _ = build_ymm4_package(
        _plan(),
        _script(),
        _packet(),
        [],
        export_root=tmp_path / "exports",
    )

    output_path = write_materialization_draft(
        _plan(),
        _script(),
        _packet(),
        script_root=tmp_path / "scripts",
    )
    inspection = inspect_episode_bundle(export_dir)

    assert output_path.exists()
    assert inspection.passed
    assert any(issue.code == "script_todo_skeleton" for issue in inspection.warnings)


def test_script_materialize_cli_writes_draft_packet(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    script_root = tmp_path / "scripts"
    primary = _article("primary", "official")
    critical = _article("critical", "official")
    cluster = _cluster(primary)
    upsert_article(db_path, primary)
    upsert_article(db_path, critical)
    replace_clusters_for_date(db_path, cluster.cluster_date, [cluster])
    add_story_critical_source(db_path, cluster_id=cluster.id, article_id=critical.id)

    assert (
        main(
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
        == 0
    )
    script_id = next(script_root.iterdir()).name

    assert (
        main(
            [
                "--db",
                str(db_path),
                "script",
                "materialize",
                "--script",
                script_id,
                "--script-root",
                str(script_root),
            ]
        )
        == 0
    )

    payload = yaml.safe_load(
        (script_root / script_id / "script_materialization.yml").read_text(encoding="utf-8")
    )
    assert payload["status"] == "operator_fill_required"
    assert len(payload["segments"]) == 6
    assert any(segment["critical_refs"] for segment in payload["segments"])
    assert all(segment["replacement_status"] == "operator_pending" for segment in payload["segments"])


def _article(seed: str, source_type: str) -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Source article {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        published_at="2026-06-01T00:00:00+00:00",
        fetched_at="2026-06-01T01:00:00+00:00",
    )


def _cluster(article: Article) -> StoryCluster:
    return StoryCluster(
        id="story_materialize_cli",
        title="AI systems",
        summary=None,
        article_ids=[article.id],
        primary_sources=[article.source_name],
        related_series=[],
        entities=["AI"],
        content_farm_overlap=0.0,
        cluster_date="2026-06-01",
        created_at="2026-06-01T01:00:00+00:00",
        updated_at="2026-06-01T01:00:00+00:00",
    )
