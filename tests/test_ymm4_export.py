from __future__ import annotations

import csv
import json

import yaml

from newsroom.adapters.ymm4_export import build_ymm4_package
from newsroom.script.script_critic import CritiqueFinding
from newsroom.store.models import (
    AssetCandidate,
    AssetManifest,
    Chapter,
    EpisodePlan,
    NotebookPacket,
    QuoteEntry,
    QuoteManifest,
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


def _script(*, source_card_intent: bool = False) -> ScriptIR:
    fact_visual_refs = ["source_card:article_a"] if source_card_intent else ["visual:facts"]
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
                visual_refs=fact_visual_refs,
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

    for filename in (
        "script.csv",
        "script_ir.json",
        "source_list.md",
        "ymm4_notes.md",
        "visual_plan.md",
        "visual_ir.json",
        "asset_manifest.yml",
        "quote_manifest.yml",
        "export_manifest.json",
    ):
        assert (output_dir / filename).exists(), f"missing {filename}"

    assert manifest["schema_version"] == 2
    assert manifest["episode_id"] == output_dir.name
    assert manifest["references"]["story_cluster_id"] == "story_20260518_test"
    assert manifest["references"]["packet_export_dir"] == "data/packets/packet_test_001"
    assert manifest["references"]["visual_ir_id"].startswith("visual_")
    assert manifest["references"]["asset_manifest_path"] == "asset_manifest.yml"
    assert manifest["references"]["quote_manifest_path"] == "quote_manifest.yml"
    assert manifest["artifacts"]["script_csv"] == "script.csv"
    assert manifest["artifacts"]["visual_plan"] == "visual_plan.md"
    assert manifest["artifacts"]["visual_ir"] == "visual_ir.json"
    assert manifest["artifacts"]["asset_manifest"] == "asset_manifest.yml"
    assert manifest["artifacts"]["quote_manifest"] == "quote_manifest.yml"


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


def test_export_does_not_duplicate_critical_view_when_critic_emits_it(tmp_path):
    findings = [
        CritiqueFinding(
            guard="critical_view",
            severity="warn",
            message="Packet has no critical_views; conflict chapter segments need manual critical input.",
        )
    ]

    _, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(critical_views_empty=True),
        findings,
        export_root=tmp_path,
    )

    critical_lines = [w for w in manifest["warnings"] if "critical_view" in w.lower()]
    assert len(critical_lines) == 1


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


def test_manifest_removes_implemented_m6_artifacts_from_deferred(tmp_path):
    _, manifest = build_ymm4_package(_plan(), _script(), _packet(), [], export_root=tmp_path)
    assert "visual_plan.md" not in manifest["deferred_artifacts"]
    assert "visual_ir.json" not in manifest["deferred_artifacts"]
    assert "asset_manifest.yml" not in manifest["deferred_artifacts"]
    assert "quote_manifest.yml" not in manifest["deferred_artifacts"]


def test_manifest_keeps_warnings_while_adding_m6_review_gate(tmp_path):
    findings = [
        CritiqueFinding(
            guard="critical_view",
            severity="warn",
            message="Packet has no critical_views; conflict chapter segments need manual critical input.",
        )
    ]

    _, manifest = build_ymm4_package(
        _plan(),
        _script(source_card_intent=True),
        _packet(critical_views_empty=True),
        findings,
        export_root=tmp_path,
    )

    joined = " | ".join(manifest["warnings"])
    assert "critical_view" in joined
    assert "human_required" in joined
    assert "segments still flagged needs_human_review" in joined


def test_manifest_omits_m6_review_gate_for_internal_visuals(tmp_path):
    _, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(critical_views_empty=False),
        [],
        export_root=tmp_path,
    )

    joined = " | ".join(manifest["warnings"])
    assert "M6 handoff contains" not in joined
    assert "human_required visual/asset/quote" not in joined
    assert "segments still flagged needs_human_review" in joined


def test_export_reuses_supplied_asset_and_quote_manifests(tmp_path):
    asset_manifest = AssetManifest(
        episode_id="plan_20260518_test",
        created_at="2026-05-18T04:00:00+00:00",
        assets=[
            AssetCandidate(
                asset_id="asset_reviewed",
                type="local_template",
                source_url=None,
                source_title=None,
                author=None,
                captured_at=None,
                intended_use="Already reviewed local card",
                risk_level="low",
                approval_state="approved",
            )
        ],
    )
    quote_manifest = QuoteManifest(
        episode_id="plan_20260518_test",
        created_at="2026-05-18T04:00:00+00:00",
        quotes=[
            QuoteEntry(
                quote_id="quote_reviewed",
                source_ref="article_a",
                quote_type="text",
                purpose="evidence",
                necessity="Already reviewed",
                quoted_scope="seg_2",
                main_subordinate_assessment="analysis remains primary",
                distinction_method="attributed",
                attribution="Microsoft Blog",
                risk_level="low",
                approval_state="approved",
            )
        ],
    )

    output_dir, manifest = build_ymm4_package(
        _plan(),
        _script(),
        _packet(),
        [],
        export_root=tmp_path,
        asset_manifest=asset_manifest,
        quote_manifest=quote_manifest,
    )

    asset_payload = yaml.safe_load(
        (output_dir / "asset_manifest.yml").read_text(encoding="utf-8")
    )
    quote_payload = yaml.safe_load(
        (output_dir / "quote_manifest.yml").read_text(encoding="utf-8")
    )
    assert asset_payload["assets"][0]["approval_state"] == "approved"
    assert quote_payload["quotes"][0]["approval_state"] == "approved"
    assert manifest["references"]["asset_manifest_episode_id"] == "plan_20260518_test"
    assert manifest["references"]["quote_manifest_episode_id"] == "plan_20260518_test"


def test_script_ir_json_round_trips_segments(tmp_path):
    output_dir, _ = build_ymm4_package(_plan(), _script(), _packet(), [], export_root=tmp_path)
    payload = json.loads((output_dir / "script_ir.json").read_text(encoding="utf-8"))
    assert payload["format"] == "yukkuri_dialogue"
    assert len(payload["segments"]) == 2
    assert payload["segments"][1]["claim_type"] == "fact"
