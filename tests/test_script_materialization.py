from __future__ import annotations

import pytest
import yaml

from newsroom.adapters.export_inspector import inspect_episode_bundle
from newsroom.adapters.ymm4_export import build_ymm4_package
from newsroom.cli.main import main
from newsroom.script.materialization import (
    MaterializationValidationError,
    apply_approved_materialization_record,
    apply_materialization_draft,
    build_approved_materialization_record,
    build_materialization_payload,
    write_approved_materialization_record,
    write_materialization_draft,
)
from newsroom.store.db import (
    add_story_critical_source,
    load_script_ir,
    replace_clusters_for_date,
    upsert_article,
)
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


def test_apply_materialization_rejects_unfilled_draft(tmp_path):
    output_path = write_materialization_draft(
        _plan(),
        _script(),
        _packet(),
        script_root=tmp_path / "scripts",
    )

    with pytest.raises(MaterializationValidationError, match="operator_fill is empty"):
        apply_materialization_draft(_script(), output_path)


def test_apply_materialization_rejects_unapproved_draft(tmp_path):
    output_path = _write_draft_payload(
        tmp_path,
        fill_text="承認前の入力",
        replacement_status="operator_pending",
    )

    with pytest.raises(MaterializationValidationError, match="replacement_status must be approved"):
        apply_materialization_draft(_script(), output_path)


def test_apply_materialization_replaces_only_text_and_preserves_segment_fields(tmp_path):
    output_path = _write_draft_payload(
        tmp_path,
        fill_text="承認済みナレーション",
        replacement_status="approved",
    )

    updated = apply_materialization_draft(_script(), output_path)
    segment = updated.segments[0]

    assert segment.text == "承認済みナレーション"
    assert segment.speaker == "ナレーター"
    assert segment.source_refs == ["article_primary", "article_critical"]
    assert segment.visual_refs == ["visual:intro"]
    assert segment.needs_human_review is True
    assert segment.claim_type == "instruction"


def test_export_todo_warning_disappears_only_after_approved_replacement(tmp_path):
    output_path = _write_draft_payload(
        tmp_path,
        fill_text="承認済みナレーション",
        replacement_status="approved",
    )
    updated = apply_materialization_draft(_script(), output_path)

    export_dir, _ = build_ymm4_package(
        _plan(),
        updated,
        _packet(),
        [],
        export_root=tmp_path / "exports",
    )
    inspection = inspect_episode_bundle(export_dir)

    assert inspection.passed
    assert not any(issue.code == "script_todo_skeleton" for issue in inspection.warnings)


def test_approved_materialization_record_is_sanitized_and_portable(tmp_path):
    draft_path = _write_draft_payload(
        tmp_path,
        fill_text="承認済みナレーション",
        replacement_status="approved",
    )

    record = build_approved_materialization_record(
        _script(),
        draft_path,
        story_cluster_id=_plan().story_cluster_id,
        episode_id="episode_materialize_test",
        approved_by="operator",
        approved_at="2026-06-07T00:00:00+00:00",
        approval_note="operator-approved narration only",
    )
    dumped = yaml.safe_dump(record, allow_unicode=True, sort_keys=False)

    assert record["artifact_type"] == "approved_script_materialization"
    assert record["status"] == "approved"
    assert record["approval"]["approved_by"] == "operator"
    assert record["segments"][0]["approved_text"] == "承認済みナレーション"
    assert record["segments"][0]["source_refs"] == ["article_primary", "article_critical"]
    assert record["segments"][0]["critical_refs"] == ["article_critical"]
    assert record["segments"][0]["visual_refs"] == ["visual:intro"]
    assert "source_catalog" not in dumped
    assert "current_text" not in dumped
    assert "operator_fill" not in dumped
    assert "https://example.com" not in dumped


def test_approved_materialization_record_rejects_unfilled_or_unapproved_draft(tmp_path):
    unfilled = _write_draft_payload(
        tmp_path,
        fill_text="",
        replacement_status="approved",
    )
    with pytest.raises(MaterializationValidationError, match="operator_fill is empty"):
        write_approved_materialization_record(
            _script(),
            unfilled,
            story_cluster_id=_plan().story_cluster_id,
            episode_id=None,
            approved_by="operator",
            output_root=tmp_path / "approved",
        )

    unapproved = _write_draft_payload(
        tmp_path,
        fill_text="承認前の入力",
        replacement_status="operator_pending",
    )
    with pytest.raises(MaterializationValidationError, match="replacement_status must be approved"):
        write_approved_materialization_record(
            _script(),
            unapproved,
            story_cluster_id=_plan().story_cluster_id,
            episode_id=None,
            approved_by="operator",
            output_root=tmp_path / "approved",
        )


def test_apply_approved_materialization_record_replaces_only_text(tmp_path):
    record_path = _write_approved_record_payload(tmp_path, fill_text="承認済みナレーション")

    updated = apply_approved_materialization_record(_script(), record_path)
    segment = updated.segments[0]

    assert segment.text == "承認済みナレーション"
    assert segment.speaker == "ナレーター"
    assert segment.source_refs == ["article_primary", "article_critical"]
    assert segment.visual_refs == ["visual:intro"]
    assert segment.needs_human_review is True
    assert segment.claim_type == "instruction"


def test_approved_record_validation_rejects_raw_or_runtime_fields(tmp_path):
    record_path = _write_approved_record_payload(tmp_path, fill_text="承認済みナレーション")
    payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    payload["source_catalog"] = {"article_primary": {"body": "raw source body"}}
    record_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(MaterializationValidationError, match="source_catalog is not allowed"):
        apply_approved_materialization_record(_script(), record_path)


def test_approved_record_validation_rejects_unknown_segment(tmp_path):
    record_path = _write_approved_record_payload(tmp_path, fill_text="承認済みナレーション")
    payload = yaml.safe_load(record_path.read_text(encoding="utf-8"))
    payload["segments"].append({**payload["segments"][0], "segment_id": "unknown_segment"})
    record_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(MaterializationValidationError, match="not present in ScriptIR"):
        apply_approved_materialization_record(_script(), record_path)


def test_export_todo_warning_disappears_after_approved_record_replacement(tmp_path):
    record_path = _write_approved_record_payload(tmp_path, fill_text="承認済みナレーション")
    updated = apply_approved_materialization_record(_script(), record_path)

    export_dir, _ = build_ymm4_package(
        _plan(),
        updated,
        _packet(),
        [],
        export_root=tmp_path / "exports",
    )
    inspection = inspect_episode_bundle(export_dir)

    assert inspection.passed
    assert not any(issue.code == "script_todo_skeleton" for issue in inspection.warnings)


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


def test_script_apply_materialization_cli_rejects_unfilled_draft(tmp_path):
    db_path, script_root, script_id = _draft_cli_script(tmp_path)
    draft_path = script_root / script_id / "script_materialization.yml"

    exit_code = main(
        [
            "--db",
            str(db_path),
            "script",
            "apply-materialization",
            "--script",
            script_id,
            "--draft",
            str(draft_path),
            "--require-approved",
            "--script-root",
            str(script_root),
        ]
    )
    persisted = load_script_ir(db_path, script_id)

    assert exit_code == 1
    assert persisted is not None
    assert all(segment.text.startswith("TODO[") for segment in persisted.segments)


def test_script_apply_materialization_cli_applies_approved_draft(tmp_path):
    db_path, script_root, script_id = _draft_cli_script(tmp_path)
    draft_path = script_root / script_id / "script_materialization.yml"
    before = load_script_ir(db_path, script_id)
    assert before is not None
    source_refs_before = [segment.source_refs for segment in before.segments]
    payload = yaml.safe_load(draft_path.read_text(encoding="utf-8"))
    for index, segment in enumerate(payload["segments"], start=1):
        segment["operator_fill"] = f"承認済みナレーション {index}"
        segment["replacement_status"] = "approved"
    draft_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--db",
            str(db_path),
            "script",
            "apply-materialization",
            "--script",
            script_id,
            "--draft",
            str(draft_path),
            "--require-approved",
            "--script-root",
            str(script_root),
        ]
    )
    persisted = load_script_ir(db_path, script_id)

    assert exit_code == 0
    assert persisted is not None
    assert not any(segment.text.startswith("TODO[") for segment in persisted.segments)
    assert all(segment.speaker == "ナレーター" for segment in persisted.segments)
    assert [segment.source_refs for segment in persisted.segments] == source_refs_before
    assert any(len(segment.source_refs) > 1 for segment in persisted.segments)


def test_script_approve_materialization_cli_rejects_unfilled_draft(tmp_path):
    db_path, script_root, script_id = _draft_cli_script(tmp_path)
    draft_path = script_root / script_id / "script_materialization.yml"

    exit_code = main(
        [
            "--db",
            str(db_path),
            "script",
            "approve-materialization",
            "--script",
            script_id,
            "--draft",
            str(draft_path),
            "--approved-by",
            "operator",
            "--output-root",
            str(tmp_path / "approved"),
        ]
    )

    assert exit_code == 1
    assert not (tmp_path / "approved" / f"{script_id}.materialization.yml").exists()


def test_script_approve_and_apply_approved_materialization_cli(tmp_path):
    db_path, script_root, script_id = _draft_cli_script(tmp_path)
    draft_path = script_root / script_id / "script_materialization.yml"
    approved_root = tmp_path / "approved"
    before = load_script_ir(db_path, script_id)
    assert before is not None
    source_refs_before = [segment.source_refs for segment in before.segments]
    visual_refs_before = [segment.visual_refs for segment in before.segments]
    payload = yaml.safe_load(draft_path.read_text(encoding="utf-8"))
    for index, segment in enumerate(payload["segments"], start=1):
        segment["operator_fill"] = f"承認済みナレーション {index}"
        segment["replacement_status"] = "approved"
    draft_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    approve_exit = main(
        [
            "--db",
            str(db_path),
            "script",
            "approve-materialization",
            "--script",
            script_id,
            "--draft",
            str(draft_path),
            "--episode-id",
            "episode_materialize_cli",
            "--approved-by",
            "operator",
            "--approved-at",
            "2026-06-07T00:00:00+00:00",
            "--approval-note",
            "approved text only",
            "--output-root",
            str(approved_root),
        ]
    )
    record_path = approved_root / f"{script_id}.materialization.yml"
    record_text = record_path.read_text(encoding="utf-8")

    assert approve_exit == 0
    assert record_path.exists()
    assert "source_catalog" not in record_text
    assert "current_text" not in record_text
    assert "operator_fill" not in record_text

    apply_exit = main(
        [
            "--db",
            str(db_path),
            "script",
            "apply-approved-materialization",
            "--script",
            script_id,
            "--record",
            str(record_path),
            "--script-root",
            str(script_root),
        ]
    )
    persisted = load_script_ir(db_path, script_id)

    assert apply_exit == 0
    assert persisted is not None
    assert not any(segment.text.startswith("TODO[") for segment in persisted.segments)
    assert all(segment.speaker == "ナレーター" for segment in persisted.segments)
    assert [segment.source_refs for segment in persisted.segments] == source_refs_before
    assert [segment.visual_refs for segment in persisted.segments] == visual_refs_before
    assert all(segment.needs_human_review for segment in persisted.segments)


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


def _write_draft_payload(tmp_path, *, fill_text: str, replacement_status: str):
    payload = build_materialization_payload(_plan(), _script(), _packet())
    payload["segments"][0]["operator_fill"] = fill_text
    payload["segments"][0]["replacement_status"] = replacement_status
    output_path = tmp_path / "script_materialization.yml"
    output_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return output_path


def _write_approved_record_payload(tmp_path, *, fill_text: str):
    draft_path = _write_draft_payload(
        tmp_path,
        fill_text=fill_text,
        replacement_status="approved",
    )
    return write_approved_materialization_record(
        _script(),
        draft_path,
        story_cluster_id=_plan().story_cluster_id,
        episode_id="episode_materialize_test",
        approved_by="operator",
        approved_at="2026-06-07T00:00:00+00:00",
        output_root=tmp_path / "approved",
    )


def _draft_cli_script(tmp_path):
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
    return db_path, script_root, script_id
