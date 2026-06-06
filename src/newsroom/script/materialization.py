from __future__ import annotations

from dataclasses import asdict
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from newsroom.script.exporters import DEFAULT_SCRIPT_ROOT
from newsroom.store.models import EpisodePlan, NotebookPacket, ScriptIR


MATERIALIZATION_FILENAME = "script_materialization.yml"


class MaterializationValidationError(ValueError):
    pass


def write_materialization_draft(
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
    script_root: Path | str = DEFAULT_SCRIPT_ROOT,
) -> Path:
    output_dir = Path(script_root) / script.id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / MATERIALIZATION_FILENAME
    output_path.write_text(
        _render_materialization_yaml(plan, script, packet),
        encoding="utf-8",
    )
    return output_path


def _render_materialization_yaml(
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
) -> str:
    payload = build_materialization_payload(plan, script, packet)
    return yaml.safe_dump(
        payload,
        allow_unicode=True,
        sort_keys=False,
    )


def build_materialization_payload(
    plan: EpisodePlan,
    script: ScriptIR,
    packet: NotebookPacket,
) -> dict[str, Any]:
    source_catalog = _source_catalog(packet)
    critical_source_ids = {ref.article_id for ref in packet.critical_views}
    chapter_lookup = {chapter.id: chapter for chapter in plan.chapter_outline}

    segments: list[dict[str, Any]] = []
    for index, segment in enumerate(script.segments, start=1):
        chapter = chapter_lookup.get(segment.chapter_id)
        source_refs = list(segment.source_refs)
        critical_refs = [ref for ref in source_refs if ref in critical_source_ids]
        segments.append(
            {
                "index": index,
                "segment_id": segment.id,
                "chapter_id": segment.chapter_id,
                "chapter_title": chapter.title if chapter else None,
                "chapter_intent": chapter.intent if chapter else None,
                "target_duration_sec": chapter.target_duration_sec if chapter else None,
                "speaker": segment.speaker,
                "claim_type": segment.claim_type,
                "current_text": segment.text,
                "source_refs": source_refs,
                "critical_refs": critical_refs,
                "suggested_angle": _suggested_angle(chapter, critical_refs),
                "operator_fill": "",
                "human_review_required": segment.needs_human_review,
                "replacement_status": "operator_pending",
            }
        )

    return {
        "schema_version": 1,
        "artifact_type": "script_materialization_draft",
        "mode": "operator_draft",
        "created_at": datetime.now(UTC).isoformat(),
        "script_id": script.id,
        "episode_plan_id": plan.id,
        "story_cluster_id": plan.story_cluster_id,
        "format": script.format,
        "status": "operator_fill_required",
        "non_goals": [
            "does_not_generate_final_narration",
            "does_not_modify_script_ir",
            "does_not_modify_script_csv",
            "does_not_clear_export_inspect_todo_warning",
        ],
        "replacement_policy": (
            "Fill operator_fill for each segment, then use a separate "
            "operator-approved replacement step before rebuilding script.csv."
        ),
        "approval_policy": {
            "required_replacement_status": "approved",
            "operator_fill_required": True,
        },
        "source_catalog": source_catalog,
        "segments": segments,
    }


def apply_materialization_draft(
    script: ScriptIR,
    draft_path: Path | str,
    *,
    require_approved: bool = True,
) -> ScriptIR:
    draft = _load_materialization_payload(Path(draft_path))
    replacements = _validated_replacements(script, draft, require_approved=require_approved)
    updated_segments = [
        replace(segment, text=replacements[segment.id])
        if segment.id in replacements
        else segment
        for segment in script.segments
    ]
    return replace(script, segments=updated_segments)


def _load_materialization_payload(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise MaterializationValidationError(f"Cannot read materialization draft: {exc}") from exc
    if not isinstance(payload, dict):
        raise MaterializationValidationError("Materialization draft must be a mapping")
    return payload


def _validated_replacements(
    script: ScriptIR,
    draft: dict[str, Any],
    *,
    require_approved: bool,
) -> dict[str, str]:
    errors: list[str] = []
    if draft.get("script_id") != script.id:
        errors.append(f"draft script_id {draft.get('script_id')!r} does not match {script.id!r}")
    if draft.get("artifact_type") != "script_materialization_draft":
        errors.append("draft artifact_type must be script_materialization_draft")
    raw_segments = draft.get("segments")
    if not isinstance(raw_segments, list):
        errors.append("draft segments must be a list")
        raw_segments = []

    draft_by_id: dict[str, dict[str, Any]] = {}
    for raw_segment in raw_segments:
        if not isinstance(raw_segment, dict):
            errors.append("draft segment entries must be mappings")
            continue
        segment_id = str(raw_segment.get("segment_id") or "")
        if not segment_id:
            errors.append("draft segment missing segment_id")
            continue
        if segment_id in draft_by_id:
            errors.append(f"duplicate draft segment_id {segment_id!r}")
        draft_by_id[segment_id] = raw_segment

    replacements: dict[str, str] = {}
    for segment in script.segments:
        if not segment.text.startswith("TODO["):
            continue
        draft_segment = draft_by_id.get(segment.id)
        if draft_segment is None:
            errors.append(f"missing draft segment for TODO segment {segment.id}")
            continue
        _validate_segment_metadata(segment, draft_segment, errors)
        operator_fill = str(draft_segment.get("operator_fill") or "").strip()
        if not operator_fill:
            errors.append(f"segment {segment.id} operator_fill is empty")
        elif operator_fill.startswith("TODO["):
            errors.append(f"segment {segment.id} operator_fill still starts with TODO[")
        else:
            replacements[segment.id] = operator_fill
        replacement_status = str(draft_segment.get("replacement_status") or "")
        if require_approved and replacement_status != "approved":
            errors.append(
                f"segment {segment.id} replacement_status must be approved, got {replacement_status!r}"
            )

    if errors:
        raise MaterializationValidationError("; ".join(errors))
    return replacements


def _validate_segment_metadata(
    segment: Any,
    draft_segment: dict[str, Any],
    errors: list[str],
) -> None:
    if draft_segment.get("current_text") != segment.text:
        errors.append(f"segment {segment.id} current_text does not match current ScriptIR text")
    if draft_segment.get("speaker") != segment.speaker:
        errors.append(f"segment {segment.id} speaker does not match current ScriptIR speaker")
    draft_source_refs = list(draft_segment.get("source_refs") or [])
    if draft_source_refs != segment.source_refs:
        errors.append(f"segment {segment.id} source_refs do not match current ScriptIR source_refs")
    critical_refs = list(draft_segment.get("critical_refs") or [])
    outside_source_refs = [ref for ref in critical_refs if ref not in segment.source_refs]
    if outside_source_refs:
        errors.append(
            f"segment {segment.id} critical_refs are not included in source_refs: {outside_source_refs}"
        )


def _source_catalog(packet: NotebookPacket) -> dict[str, dict[str, Any]]:
    catalog: dict[str, dict[str, Any]] = {}
    for role, refs in (
        ("primary", packet.primary_sources),
        ("news", packet.news_sources),
        ("critical", packet.critical_views),
    ):
        for ref in refs:
            catalog[ref.article_id] = {"role": role, **asdict(ref)}
    return catalog


def _suggested_angle(chapter: Any | None, critical_refs: list[str]) -> str:
    if chapter is None:
        base = "Write operator-approved narration for this segment from the listed source_refs."
    else:
        base = (
            f"Write operator-approved narration for '{chapter.title}' from the listed "
            f"source_refs, following intent: {chapter.intent}."
        )
    if critical_refs:
        return f"{base} Include the critical_refs as a review lens, not as unsupported final claims."
    return f"{base} Avoid direct quotes unless quote review explicitly approves them."
