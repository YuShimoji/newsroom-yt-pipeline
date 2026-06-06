from __future__ import annotations

import json

from newsroom.adapters.export_inspector import inspect_episode_bundle
from newsroom.adapters.ymm4_export import build_ymm4_package
from newsroom.cli.main import main
from newsroom.store.models import (
    Chapter,
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    SourceRef,
)


def _plan() -> EpisodePlan:
    return EpisodePlan(
        id="plan_inspect_test",
        story_cluster_id="story_inspect_test",
        series_id=None,
        title_candidates=["A"],
        thumbnail_angles=["angle"],
        hook="hook",
        chapter_outline=[
            Chapter(id="plan_inspect_test__intro", title="導入", intent="導入", target_duration_sec=30),
            Chapter(id="plan_inspect_test__facts", title="事実", intent="事実", target_duration_sec=60),
        ],
        target_duration_sec=90,
        viewer_utility="判断材料",
        risk_notes=[],
        approval_state="draft",
        created_at="2026-05-28T00:00:00+09:00",
    )


def _script(*, source_card_intent: bool = False) -> ScriptIR:
    fact_visual_refs = ["source_card:article_a"] if source_card_intent else ["visual:facts"]
    return ScriptIR(
        id="script_inspect_test",
        episode_plan_id="plan_inspect_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_intro",
                chapter_id="plan_inspect_test__intro",
                speaker="ナレーター",
                text="カンマ, と改行\nを含む日本語セリフ",
                source_refs=[],
                visual_refs=[],
                claim_type="instruction",
                needs_human_review=True,
            ),
            ScriptSegment(
                id="seg_fact",
                chapter_id="plan_inspect_test__facts",
                speaker="ナレーター",
                text="事実関係",
                source_refs=["article_a"],
                visual_refs=fact_visual_refs,
                claim_type="fact",
                needs_human_review=True,
            ),
        ],
        created_at="2026-05-28T00:01:00+09:00",
    )


def _packet() -> NotebookPacket:
    return NotebookPacket(
        id="packet_inspect_test",
        story_cluster_id="story_inspect_test",
        primary_sources=[
            SourceRef(
                article_id="article_a",
                url="https://example.com/a",
                title="Primary source",
                source_name="Microsoft Blog",
                source_type="official",
                published_at="2026-05-28T00:00:00+09:00",
            )
        ],
        news_sources=[],
        critical_views=[],
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_inspect_test",
        created_at="2026-05-28T00:02:00+09:00",
    )


def _valid_bundle(tmp_path, *, source_card_intent: bool = False):
    output_dir, _ = build_ymm4_package(
        _plan(),
        _script(source_card_intent=source_card_intent),
        _packet(),
        [],
        export_root=tmp_path,
    )
    return output_dir


def test_inspect_valid_bundle_passes_with_human_required_warnings(tmp_path):
    output_dir = _valid_bundle(tmp_path, source_card_intent=True)

    inspection = inspect_episode_bundle(output_dir)

    assert inspection.passed
    assert not inspection.errors
    assert any(issue.code == "human_required" for issue in inspection.warnings)


def test_inspect_internal_visuals_do_not_emit_human_required_warning(tmp_path):
    output_dir = _valid_bundle(tmp_path)

    inspection = inspect_episode_bundle(output_dir)

    assert inspection.passed
    assert all(issue.code != "human_required" for issue in inspection.warnings)


def test_export_inspect_cli_returns_zero_for_valid_bundle(tmp_path, capsys):
    output_dir = _valid_bundle(tmp_path)

    exit_code = main(["export", "inspect", "--episode-dir", str(output_dir)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Export bundle inspect: PASS" in captured.out


def test_inspect_missing_required_file_fails(tmp_path):
    output_dir = _valid_bundle(tmp_path)
    (output_dir / "visual_plan.md").unlink()

    inspection = inspect_episode_bundle(output_dir)

    assert not inspection.passed
    assert any(issue.code == "required_file_missing" for issue in inspection.errors)


def test_inspect_manifest_artifact_mismatch_fails(tmp_path):
    output_dir = _valid_bundle(tmp_path)
    manifest_path = output_dir / "export_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"]["visual_plan"] = "missing_visual_plan.md"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    inspection = inspect_episode_bundle(output_dir)

    assert not inspection.passed
    assert any(issue.code == "manifest_artifact_missing" for issue in inspection.errors)


def test_inspect_invalid_script_csv_shape_fails(tmp_path):
    output_dir = _valid_bundle(tmp_path)
    (output_dir / "script.csv").write_text(
        "ナレーター,本文,extra\n",
        encoding="utf-8",
    )

    inspection = inspect_episode_bundle(output_dir)

    assert not inspection.passed
    assert any(issue.code == "script_csv_shape" for issue in inspection.errors)


def test_inspect_script_csv_todo_skeleton_is_warning(tmp_path):
    output_dir = _valid_bundle(tmp_path)
    (output_dir / "script.csv").write_text(
        "ナレーター,TODO[plan#0]: operator が記入する。\n",
        encoding="utf-8",
    )

    inspection = inspect_episode_bundle(output_dir)

    assert inspection.passed
    assert any(issue.code == "script_todo_skeleton" for issue in inspection.warnings)
    assert all(issue.code != "script_todo_skeleton" for issue in inspection.errors)


def test_inspect_human_required_is_warning_not_error(tmp_path):
    output_dir = _valid_bundle(tmp_path, source_card_intent=True)

    inspection = inspect_episode_bundle(output_dir)

    assert inspection.passed
    assert any(issue.code == "human_required" for issue in inspection.warnings)
    assert all(issue.code != "human_required" for issue in inspection.errors)
