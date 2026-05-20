from __future__ import annotations

import yaml

from newsroom.assets.asset_registry import AssetRegistry
from newsroom.assets.exporters import write_asset_manifest
from newsroom.store.models import (
    NotebookPacket,
    SourceRef,
    VisualIR,
    VisualUnit,
)


def _source_ref(article_id: str, source_name: str = "Microsoft Blog") -> SourceRef:
    return SourceRef(
        article_id=article_id,
        url=f"https://example.com/{article_id}",
        title=f"Title {article_id}",
        source_name=source_name,
        source_type="official",
        published_at="2026-05-18T00:00:00+00:00",
    )


def _visual_unit(unit_id: str, unit_type: str, source_refs: list[str]) -> VisualUnit:
    return VisualUnit(
        id=unit_id,
        segment_refs=[f"{unit_id}__s0"],
        unit_type=unit_type,
        duration_sec=60.0,
        layout_template=f"{unit_type}_v1",
        source_refs=source_refs,
        asset_refs=[],
        density_score=6.0,
        approval_state="auto_ok",
    )


def _visual_ir(units: list[VisualUnit]) -> VisualIR:
    return VisualIR(
        id="visual_test_001",
        script_id="script_test_001",
        visual_units=units,
        created_at="2026-05-20T00:00:00+00:00",
    )


def _packet(primary_ids: list[str]) -> NotebookPacket:
    return NotebookPacket(
        id="packet_test",
        story_cluster_id="story_test",
        primary_sources=[_source_ref(article_id=aid) for aid in primary_ids],
        news_sources=[],
        critical_views=[],
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_test",
        created_at="2026-05-20T00:00:00+00:00",
    )


def test_source_card_emits_screenshot_with_human_required():
    visual_ir = _visual_ir([_visual_unit("u_facts", "source_card", ["article_a"])])
    packet = _packet(["article_a"])

    manifest = AssetRegistry().suggest(visual_ir, packet)

    assert len(manifest.assets) == 1
    asset = manifest.assets[0]
    assert asset.type == "screenshot"
    assert asset.source_url == "https://example.com/article_a"
    assert asset.approval_state == "human_required"
    assert asset.risk_level == "medium"
    assert asset.attribution_text == "Microsoft Blog"


def test_claim_evidence_card_emits_local_template_suggested():
    visual_ir = _visual_ir([_visual_unit("u_context", "claim_evidence_card", [])])
    packet = _packet([])

    manifest = AssetRegistry().suggest(visual_ir, packet)
    assert len(manifest.assets) == 1
    asset = manifest.assets[0]
    assert asset.type == "local_template"
    assert asset.source_url is None
    assert asset.approval_state == "suggested"
    assert asset.risk_level == "low"


def test_timeline_spine_emits_generated_diagram():
    visual_ir = _visual_ir([_visual_unit("u_timeline", "timeline_spine", [])])
    packet = _packet([])

    manifest = AssetRegistry().suggest(visual_ir, packet)
    asset = manifest.assets[0]
    assert asset.type == "generated_diagram"
    assert asset.approval_state == "suggested"


def test_source_card_without_matching_source_falls_back_to_local_template():
    visual_ir = _visual_ir([_visual_unit("u_facts", "source_card", ["article_missing"])])
    packet = _packet([])  # no matching source

    manifest = AssetRegistry().suggest(visual_ir, packet)
    asset = manifest.assets[0]
    assert asset.type == "local_template"
    assert asset.approval_state == "suggested"


def test_manifest_round_trips_through_yaml(tmp_path):
    visual_ir = _visual_ir(
        [
            _visual_unit("u_facts", "source_card", ["article_a"]),
            _visual_unit("u_context", "claim_evidence_card", []),
        ]
    )
    packet = _packet(["article_a"])

    manifest = AssetRegistry().suggest(visual_ir, packet, episode_id="plan_test_001")
    output_dir = write_asset_manifest(manifest, asset_root=tmp_path)

    yaml_path = output_dir / "asset_manifest.yml"
    assert yaml_path.exists()

    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert payload["episode_id"] == "plan_test_001"
    assert len(payload["assets"]) == 2
    screenshot_entry = next(a for a in payload["assets"] if a["type"] == "screenshot")
    assert screenshot_entry["approval_state"] == "human_required"
