from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from newsroom.script.script_critic import CritiqueFinding
from newsroom.store.models import (
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
)


DEFAULT_EXPORT_ROOT = Path("data/exports")
MANIFEST_SCHEMA_VERSION = 1


def build_ymm4_package(
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
    findings: list[CritiqueFinding],
    *,
    export_root: Path | str = DEFAULT_EXPORT_ROOT,
) -> tuple[Path, dict]:
    """Render the M5 artifact bundle and return (output_dir, manifest)."""
    episode_id = _episode_id(plan, script)
    output_dir = Path(export_root) / episode_id
    output_dir.mkdir(parents=True, exist_ok=True)

    warnings = _collect_warnings(packet, script, findings)
    exported_at = datetime.now(UTC).isoformat()

    chapter_lookup = {chapter.id: chapter for chapter in plan.chapter_outline}
    _write_script_csv(output_dir / "script.csv", script, chapter_lookup)
    _write_script_ir_json(output_dir / "script_ir.json", script)
    _write_source_list_md(output_dir / "source_list.md", packet)
    _write_ymm4_notes_md(output_dir / "ymm4_notes.md", plan, script, packet, warnings)

    manifest = _build_manifest(
        episode_id=episode_id,
        exported_at=exported_at,
        plan=plan,
        script=script,
        packet=packet,
        warnings=warnings,
    )
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return output_dir, manifest


def _episode_id(plan: EpisodePlan, script: ScriptIR) -> str:
    digest = sha256(f"{plan.id}|{script.id}".encode("utf-8")).hexdigest()[:12]
    return f"episode_{digest}"


def _collect_warnings(
    packet: NotebookPacket,
    script: ScriptIR,
    findings: list[CritiqueFinding],
) -> list[str]:
    warnings: list[str] = []

    if not packet.critical_views:
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

    return warnings


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
    lines.append("## Warnings")
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- _No warnings emitted._")
    lines.append("")
    lines.append("## Deferred (not in this milestone)")
    lines.append("- `visual_plan.md`, `visual_ir.json` — M6 VisualIR")
    lines.append("- `asset_manifest.yml`, `quote_manifest.yml` — M6 Asset / Quote manifests")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_manifest(
    *,
    episode_id: str,
    exported_at: str,
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
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
        },
        "artifacts": {
            "script_csv": "script.csv",
            "script_ir": "script_ir.json",
            "source_list": "source_list.md",
            "ymm4_notes": "ymm4_notes.md",
        },
        "warnings": warnings,
        "deferred_artifacts": [
            "visual_plan.md",
            "visual_ir.json",
            "asset_manifest.yml",
            "quote_manifest.yml",
        ],
    }
