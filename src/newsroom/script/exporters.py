from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from newsroom.script.script_critic import CritiqueFinding
from newsroom.store.models import EpisodePlan, ScriptIR


DEFAULT_SCRIPT_ROOT = Path("data/scripts")


def write_script_bundle(
    plan: EpisodePlan,
    script: ScriptIR,
    findings: list[CritiqueFinding],
    script_root: Path | str = DEFAULT_SCRIPT_ROOT,
) -> Path:
    output_dir = Path(script_root) / script.id
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "script.md").write_text(_render_script_md(plan, script), encoding="utf-8")
    (output_dir / "script_ir.json").write_text(_render_script_json(script), encoding="utf-8")
    (output_dir / "script_review.md").write_text(_render_review_md(plan, script, findings), encoding="utf-8")
    return output_dir


def _render_script_md(plan: EpisodePlan, script: ScriptIR) -> str:
    lines: list[str] = []
    lines.append(f"# Script Draft — {script.id}")
    lines.append("")
    lines.append(f"- episode_plan: `{plan.id}`")
    lines.append(f"- format: `{script.format}`")
    lines.append(f"- target_duration_sec: {plan.target_duration_sec}")
    lines.append(f"- viewer_utility: {plan.viewer_utility}")
    lines.append("")
    lines.append("## Hook")
    lines.append("")
    lines.append(plan.hook)
    lines.append("")
    lines.append("## Title candidates")
    for candidate in plan.title_candidates:
        lines.append(f"- {candidate}")
    lines.append("")

    chapter_lookup = {chapter.id: chapter for chapter in plan.chapter_outline}
    current_chapter: str | None = None
    for segment in script.segments:
        if segment.chapter_id != current_chapter:
            chapter = chapter_lookup.get(segment.chapter_id)
            chapter_title = chapter.title if chapter else segment.chapter_id
            chapter_intent = chapter.intent if chapter else ""
            lines.append(f"## {chapter_title}")
            if chapter_intent:
                lines.append(f"_{chapter_intent}_")
            lines.append("")
            current_chapter = segment.chapter_id
        lines.append(f"**{segment.speaker}** ({segment.claim_type}): {segment.text}")
        if segment.source_refs:
            lines.append(f"  - source_refs: {segment.source_refs}")
        if segment.visual_refs:
            lines.append(f"  - visual_refs: {segment.visual_refs}")
        lines.append("")
    return "\n".join(lines)


def _render_script_json(script: ScriptIR) -> str:
    payload = {
        "id": script.id,
        "episode_plan_id": script.episode_plan_id,
        "format": script.format,
        "created_at": script.created_at,
        "segments": [asdict(segment) for segment in script.segments],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _render_review_md(
    plan: EpisodePlan,
    script: ScriptIR,
    findings: list[CritiqueFinding],
) -> str:
    lines: list[str] = []
    lines.append(f"# Script Review — {script.id}")
    lines.append("")
    lines.append(f"- episode_plan: `{plan.id}`")
    lines.append(f"- approval_state: `{plan.approval_state}`")
    lines.append("")
    lines.append("## Editorial guards")
    for finding in findings:
        marker = _severity_marker(finding.severity)
        lines.append(f"- {marker} **{finding.guard}** — {finding.message}")
    lines.append("")
    if plan.risk_notes:
        lines.append("## Risk notes from EpisodePlan")
        for note in plan.risk_notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## Operator next steps")
    lines.append("- [ ] Fill TODO segments with actual narration.")
    lines.append("- [ ] Resolve any guard marked fail or warn.")
    lines.append("- [ ] Flip approval_state to needs_review when ready.")
    lines.append("")
    return "\n".join(lines)


def _severity_marker(severity: str) -> str:
    return {"ok": "[ok]", "warn": "[warn]", "fail": "[fail]"}.get(severity, "[?]")
