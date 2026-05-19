from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from newsroom.store.models import EpisodePlan, ScriptIR, VisualIR


DEFAULT_VISUAL_ROOT = Path("data/visuals")


def write_visual_bundle(
    visual_ir: VisualIR,
    script: ScriptIR,
    plan: EpisodePlan,
    visual_root: Path | str = DEFAULT_VISUAL_ROOT,
) -> Path:
    output_dir = Path(visual_root) / visual_ir.id
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "visual_plan.md").write_text(
        _render_visual_plan_md(visual_ir, script, plan),
        encoding="utf-8",
    )
    (output_dir / "visual_ir.json").write_text(
        _render_visual_ir_json(visual_ir),
        encoding="utf-8",
    )
    return output_dir


def _render_visual_plan_md(
    visual_ir: VisualIR, script: ScriptIR, plan: EpisodePlan
) -> str:
    lines: list[str] = []
    lines.append(f"# Visual Plan — {visual_ir.id}")
    lines.append("")
    lines.append(f"- script_id: `{visual_ir.script_id}`")
    lines.append(f"- episode_plan_id: `{plan.id}`")
    lines.append(f"- created_at: {visual_ir.created_at}")
    lines.append(f"- total visual units: {len(visual_ir.visual_units)}")
    lines.append("")
    lines.append("## Visual units")

    chapter_lookup = {chapter.id: chapter for chapter in plan.chapter_outline}
    for unit in visual_ir.visual_units:
        anchor_chapter = _resolve_chapter_label(unit, chapter_lookup)
        lines.append("")
        lines.append(f"### {unit.unit_type} — {anchor_chapter}")
        lines.append(f"- unit_id: `{unit.id}`")
        lines.append(f"- layout_template: `{unit.layout_template}`")
        lines.append(f"- duration_sec: {unit.duration_sec}")
        lines.append(f"- density_score: {unit.density_score}")
        lines.append(f"- approval_state: `{unit.approval_state}`")
        if unit.segment_refs:
            lines.append(f"- segment_refs: {unit.segment_refs}")
        if unit.source_refs:
            lines.append(f"- source_refs: {unit.source_refs}")
        if unit.asset_refs:
            lines.append(f"- asset_refs: {unit.asset_refs}")
        else:
            lines.append("- asset_refs: _(empty — external assets are out of M6.1 scope)_")

    lines.append("")
    lines.append("## Operator next steps")
    lines.append("- [ ] Review human_required units (typically source_card variants).")
    lines.append("- [ ] Confirm timeline_spine ordering when present.")
    lines.append("- [ ] Decide which segments need additional cards (M6.x adds version_diff / actor_map / risk_meter / context_stack).")
    lines.append("- [ ] Asset selection happens in M6.2 AssetManifest, not here.")
    lines.append("")
    return "\n".join(lines)


def _render_visual_ir_json(visual_ir: VisualIR) -> str:
    payload = {
        "id": visual_ir.id,
        "script_id": visual_ir.script_id,
        "created_at": visual_ir.created_at,
        "visual_units": [asdict(unit) for unit in visual_ir.visual_units],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _resolve_chapter_label(unit, chapter_lookup) -> str:
    for chapter_id, chapter in chapter_lookup.items():
        if any(
            segment_ref.startswith(chapter_id + "__")
            for segment_ref in unit.segment_refs
        ):
            return chapter.title
    if unit.unit_type == "timeline_spine":
        return "全章共通 timeline overlay"
    return "(no chapter anchor)"
