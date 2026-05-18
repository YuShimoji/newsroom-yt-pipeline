from __future__ import annotations

import csv
import json

from newsroom.adapters.ymm4_export import build_ymm4_package
from newsroom.script.script_critic import CritiqueFinding
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
        id="plan_20260518_test",
        story_cluster_id="story_20260518_test",
        series_id="copilot",
        title_candidates=["A"],
        thumbnail_angles=["angle"],
        hook="hook",
        chapter_outline=[
            Chapter(id="plan_20260518_test__intro", title="導入", intent="導入", target_duration_sec=60),
            Chapter(id="plan_20260518_test__facts", title="事実", intent="事実", target_duration_sec=120),
        ],
        target_duration_sec=180,
        viewer_utility="判断材料",
        risk_notes=[],
        approval_state="draft",
        created_at="2026-05-18T00:00:00+00:00",
    )


def _script() -> ScriptIR:
    return ScriptIR(
        id="script_test_001",
        episode_plan_id="plan_20260518_test",
        format="yukkuri_dialogue",
        segments=[
            ScriptSegment(
                id="seg_1",
                chapter_id="plan_20260518_test__intro",
                speaker="霊夢",
                text='これは "テスト" 用の発言, カンマと改行\nを含みます。',
                source_refs=[],
                visual_refs=[],
                claim_type="instruction",
                needs_human_review=True,
            ),
            ScriptSegment(
                id="seg_2",
                chapter_id="plan_20260518_test__facts",
                speaker="魔理沙",
                text="TODO[facts]: 事実関係",
                source_refs=["article_a"],
                visual_refs=["visual:facts"],
                claim_type="fact",
                needs_human_review=True,
            ),
        ],
        created_at="2026-05-18T01:00:00+00:00",
    )


def _packet(critical_views_empty: bool = True) -> NotebookPacket:
    primary = [
        SourceRef(
            article_id="article_a",
            url="https://example.com/a",
            title="Primary source",
            source_name="Microsoft Blog",
            source_type="official",
            published_at="2026-05-18T00:00:00+00:00",
        )
    ]
    critical: list[SourceRef] = []
    if not critical_views_empty:
        critical.append(
            SourceRef(
                article_id="article_c",
                url="https://example.com/c",
                title="Critical view",
                source_name="Critic Outlet",
                source_type="commentary",
                published_at="2026-05-18T02:00:00+00:00",
            )
        )
    return NotebookPacket(
        id="packet_test_001",
        story_cluster_id="story_20260518_test",
        primary_sources=primary,
        news_sources=[],
        critical_views=critical,
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="yukkuri",
        export_dir="data/packets/packet_test_001",
        created_at="2026-05-18T03:00:00+00:00",
    )


def test_export_emits_full_artifact_bundle(tmp_path):
    findings: list[CritiqueFinding] = [
        CritiqueFinding(guard="factual_sources", severity="ok", message="all sourced"),
        CritiqueFinding(guard="viewer_utility", severity="ok", message="set"),
    ]

    output_dir, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(),
        findings,
        export_root=tmp_path,
    )

    for filename in ("script.csv", "script_ir.json", "source_list.md", "ymm4_notes.md", "export_manifest.json"):
        assert (output_dir / filename).exists(), f"missing {filename}"

    assert manifest["episode_id"] == output_dir.name
    assert manifest["references"]["story_cluster_id"] == "story_20260518_test"
    assert manifest["references"]["packet_export_dir"] == "data/packets/packet_test_001"
    assert manifest["artifacts"]["script_csv"] == "script.csv"


def test_script_csv_quotes_commas_and_newlines(tmp_path):
    output_dir, _ = build_ymm4_package(
        _plan(),
        _script(),
        _packet(),
        [],
        export_root=tmp_path,
    )

    with (output_dir / "script.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    speaker_rows = [row for row in rows if not row[0].startswith("#")]
    assert speaker_rows[0][0] == "霊夢"
    assert "," in speaker_rows[0][1]
    assert "\n" in speaker_rows[0][1]
    assert speaker_rows[1][0] == "魔理沙"

    comment_rows = [row for row in rows if row[0].startswith("#")]
    assert any("導入" in row[0] for row in comment_rows)
    assert any("事実" in row[0] for row in comment_rows)


def test_export_warns_when_critical_views_missing(tmp_path):
    _, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(critical_views_empty=True),
        [],
        export_root=tmp_path,
    )

    joined = " | ".join(manifest["warnings"])
    assert "critical_views" in joined


def test_export_omits_critical_warning_when_packet_has_critical_views(tmp_path):
    _, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(critical_views_empty=False),
        [],
        export_root=tmp_path,
    )

    joined = " | ".join(manifest["warnings"])
    assert "critical_views" not in joined


def test_manifest_lists_deferred_milestone_artifacts(tmp_path):
    _, manifest = build_ymm4_package(_plan(), _script(), _packet(), [], export_root=tmp_path)
    assert "visual_plan.md" in manifest["deferred_artifacts"]
    assert "asset_manifest.yml" in manifest["deferred_artifacts"]


def test_script_ir_json_round_trips_segments(tmp_path):
    output_dir, _ = build_ymm4_package(_plan(), _script(), _packet(), [], export_root=tmp_path)
    payload = json.loads((output_dir / "script_ir.json").read_text(encoding="utf-8"))
    assert payload["format"] == "yukkuri_dialogue"
    assert len(payload["segments"]) == 2
    assert payload["segments"][1]["claim_type"] == "fact"
