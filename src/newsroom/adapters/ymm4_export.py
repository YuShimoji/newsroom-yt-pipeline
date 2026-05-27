from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from newsroom.assets.asset_registry import AssetRegistry
from newsroom.assets.exporters import (
    write_asset_manifest_file,
    write_quote_manifest_file,
)
from newsroom.assets.quote_manifest import QuoteManifestBuilder
from newsroom.layout.exporters import write_visual_files
from newsroom.layout.visual_planner import VisualPlanner
from newsroom.script.script_critic import CritiqueFinding
from newsroom.store.models import (
    AssetManifest,
    EpisodePlan,
    NotebookPacket,
    QuoteManifest,
    ScriptIR,
    VisualIR,
)


DEFAULT_EXPORT_ROOT = Path("data/exports")
MANIFEST_SCHEMA_VERSION = 2


def build_ymm4_package(
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
    findings: list[CritiqueFinding],
    *,
    export_root: Path | str = DEFAULT_EXPORT_ROOT,
    visual_ir: VisualIR | None = None,
    asset_manifest: AssetManifest | None = None,
    quote_manifest: QuoteManifest | None = None,
) -> tuple[Path, dict]:
    """Render the M6.4 YMM4 handoff bundle and return (output_dir, manifest)."""
    episode_id = export_episode_id(plan, script)
    output_dir = Path(export_root) / episode_id
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_visual_ir = visual_ir or VisualPlanner().plan(script, plan, packet)
    resolved_asset_manifest = asset_manifest or AssetRegistry().suggest(
        resolved_visual_ir,
        packet,
        episode_id=plan.id,
    )
    resolved_quote_manifest = quote_manifest or QuoteManifestBuilder().build(
        script,
        resolved_visual_ir,
        packet,
        episode_id=plan.id,
    )

    review_counts = _review_counts(
        resolved_visual_ir,
        resolved_asset_manifest,
        resolved_quote_manifest,
    )
    warnings = _collect_warnings(packet, script, findings, review_counts)
    exported_at = datetime.now(UTC).isoformat()

    chapter_lookup = {chapter.id: chapter for chapter in plan.chapter_outline}
    _write_script_csv(output_dir / "script.csv", script, chapter_lookup)
    _write_script_ir_json(output_dir / "script_ir.json", script)
    _write_source_list_md(output_dir / "source_list.md", packet)
    write_visual_files(output_dir, resolved_visual_ir, script, plan)
    write_asset_manifest_file(output_dir, resolved_asset_manifest)
    write_quote_manifest_file(output_dir, resolved_quote_manifest)
    _write_ymm4_notes_md(
        output_dir / "ymm4_notes.md",
        plan,
        script,
        packet,
        warnings,
        review_counts,
    )

    manifest = _build_manifest(
        episode_id=episode_id,
        exported_at=exported_at,
        plan=plan,
        script=script,
        packet=packet,
        visual_ir=resolved_visual_ir,
        asset_manifest=resolved_asset_manifest,
        quote_manifest=resolved_quote_manifest,
        warnings=warnings,
    )
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return output_dir, manifest


def export_episode_id(plan: EpisodePlan, script: ScriptIR) -> str:
    digest = sha256(f"{plan.id}|{script.id}".encode("utf-8")).hexdigest()[:12]
    return f"episode_{digest}"


def _collect_warnings(
    packet: NotebookPacket,
    script: ScriptIR,
    findings: list[CritiqueFinding],
    review_counts: dict[str, int],
) -> list[str]:
    warnings: list[str] = []
    guard_names = {finding.guard for finding in findings}

    # Only emit the direct critical_views warning when the critic did not
    # already raise one. Otherwise the bundle carried two nearly-identical
    # lines for the same condition.
    if not packet.critical_views and "critical_view" not in guard_names:
        warnings.append(
            "Packet has no critical_views; conflict chapter relies on operator augmentation."
        )

    fails = [f for f in findings if f.severity == "fail"]
    for failing in fails:
        warnings.append(f"Critic guard failed: {failing.guard} — {failing.message}")

    warns = [f for f in findings if f.severity == "warn"]
    for warning in warns:
        warnings.append(f"Critic guard warning: {warning.guard} — {warning.message}")

    review_count = sum(1 for seg in script.segments if seg.needs_human_review)
    if review_count:
        warnings.append(
            f"{review_count} / {len(script.segments)} segments still flagged needs_human_review."
        )

    if review_counts["total_human_required"]:
        warnings.append(
            "M6 handoff contains "
            f"{review_counts['total_human_required']} human_required "
            "visual/asset/quote review item(s); operator approval is required before publishing."
        )

    return warnings


def _review_counts(
    visual_ir: VisualIR,
    asset_manifest: AssetManifest,
    quote_manifest: QuoteManifest,
) -> dict[str, int]:
    visual_count = sum(
        1 for unit in visual_ir.visual_units if unit.approval_state == "human_required"
    )
    asset_count = sum(
        1 for asset in asset_manifest.assets if asset.approval_state == "human_required"
    )
    quote_count = sum(
        1 for quote in quote_manifest.quotes if quote.approval_state == "human_required"
    )
    return {
        "visual_human_required": visual_count,
        "asset_human_required": asset_count,
        "quote_human_required": quote_count,
        "total_human_required": visual_count + asset_count + quote_count,
    }


def _write_script_csv(path: Path, script: ScriptIR, chapter_lookup: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, quoting=csv.QUOTE_MINIMAL)
        current_chapter: str | None = None
        for segment in script.segments:
            if segment.chapter_id != current_chapter:
                chapter = chapter_lookup.get(segment.chapter_id)
                label = chapter.title if chapter else segment.chapter_id
                writer.writerow([f"# Chapter: {label}"])
                current_chapter = segment.chapter_id
            writer.writerow([segment.speaker, segment.text])


def _write_script_ir_json(path: Path, script: ScriptIR) -> None:
    payload = {
        "id": script.id,
        "episode_plan_id": script.episode_plan_id,
        "format": script.format,
        "created_at": script.created_at,
        "segments": [asdict(segment) for segment in script.segments],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_source_list_md(path: Path, packet: NotebookPacket) -> None:
    lines = ["# Source List", "", f"_For packet `{packet.id}` / cluster `{packet.story_cluster_id}`._", ""]
    lines.append("## Primary sources")
    if packet.primary_sources:
        for ref in packet.primary_sources:
            date = ref.published_at or "date unknown"
            lines.append(f"- [{ref.title}]({ref.url}) — {ref.source_name} ({date})")
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## News sources")
    if packet.news_sources:
        for ref in packet.news_sources:
            date = ref.published_at or "date unknown"
            lines.append(f"- [{ref.title}]({ref.url}) — {ref.source_name} ({date})")
    else:
        lines.append("_None._")
    lines.append("")
    lines.append("## Critical views")
    if packet.critical_views:
        for ref in packet.critical_views:
            date = ref.published_at or "date unknown"
            lines.append(f"- [{ref.title}]({ref.url}) — {ref.source_name} ({date})")
    else:
        lines.append("_None recorded; operator-added critical views must be tracked manually._")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_ymm4_notes_md(
    path: Path,
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
    warnings: list[str],
    review_counts: dict[str, int],
) -> None:
    lines: list[str] = []
    lines.append(f"# YMM4 Notes — {script.id}")
    lines.append("")
    lines.append("## Import procedure")
    lines.append("1. Open YMM4.")
    lines.append("2. ツール > 台本読み込み から `script.csv` を選択する。")
    lines.append("3. CSV は 2 列 (speaker, text) で、行頭 `#` はコメント (章境界) として読み飛ばされる。")
    lines.append("4. Speaker 名は `configs/speakers.yml` 由来。YMM4 内の char/voice mapping と一致するか確認する。")
    lines.append("")
    lines.append("## Format / speakers")
    lines.append(f"- format: `{script.format}`")
    distinct_speakers = sorted({segment.speaker for segment in script.segments})
    lines.append(f"- speakers used: {distinct_speakers}")
    lines.append("")
    lines.append("## Source references")
    lines.append(f"- story_cluster_id: `{plan.story_cluster_id}`")
    lines.append(f"- episode_plan_id: `{plan.id}`")
    lines.append(f"- script_id: `{script.id}`")
    lines.append(f"- packet_export_dir: `{packet.export_dir}`")
    lines.append("")
    lines.append("## Included artifacts")
    lines.append("- `script.csv` — YMM4 台本読み込み用 CSV")
    lines.append("- `script_ir.json` — 台本セグメントと source_ref の機械可読控え")
    lines.append("- `source_list.md` — primary / news / critical source の分類")
    lines.append("- `visual_plan.md` — 画面設計の確認用")
    lines.append("- `visual_ir.json` — VisualIR の機械可読控え")
    lines.append("- `asset_manifest.yml` — 素材候補と承認状態の確認用")
    lines.append("- `quote_manifest.yml` — 引用・スクショ・データ利用の公開前確認用")
    lines.append("- `export_manifest.json` — handoff package 全体の追跡用 manifest")
    lines.append("")
    lines.append("## Human review gates")
    lines.append(f"- visual human_required: {review_counts['visual_human_required']}")
    lines.append(f"- asset human_required: {review_counts['asset_human_required']}")
    lines.append(f"- quote human_required: {review_counts['quote_human_required']}")
    if review_counts["total_human_required"]:
        lines.append("- `human_required` が残る場合、公開前に operator が確認・承認・差し替え判断を行う。")
    else:
        lines.append("- _No human_required visual / asset / quote items recorded._")
    lines.append("")
    lines.append("## Warnings")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- _No warnings emitted._")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_manifest(
    *,
    episode_id: str,
    exported_at: str,
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
    visual_ir: VisualIR,
    asset_manifest: AssetManifest,
    quote_manifest: QuoteManifest,
    warnings: list[str],
) -> dict:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "episode_id": episode_id,
        "exported_at": exported_at,
        "format": script.format,
        "references": {
            "story_cluster_id": plan.story_cluster_id,
            "episode_plan_id": plan.id,
            "script_id": script.id,
            "packet_id": packet.id,
            "packet_export_dir": packet.export_dir,
            "visual_ir_id": visual_ir.id,
            "visual_plan_path": "visual_plan.md",
            "visual_ir_path": "visual_ir.json",
            "asset_manifest_episode_id": asset_manifest.episode_id,
            "asset_manifest_path": "asset_manifest.yml",
            "quote_manifest_episode_id": quote_manifest.episode_id,
            "quote_manifest_path": "quote_manifest.yml",
        },
        "artifacts": {
            "script_csv": "script.csv",
            "script_ir": "script_ir.json",
            "source_list": "source_list.md",
            "ymm4_notes": "ymm4_notes.md",
            "visual_plan": "visual_plan.md",
            "visual_ir": "visual_ir.json",
            "asset_manifest": "asset_manifest.yml",
            "quote_manifest": "quote_manifest.yml",
            "export_manifest": "export_manifest.json",
        },
        "warnings": warnings,
        "deferred_artifacts": [],
    }
