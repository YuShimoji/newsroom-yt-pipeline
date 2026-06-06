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
APPROVED_MATERIALIZATION_DEFAULT_ROOT = Path("docs/approved_materializations")
APPROVED_MATERIALIZATION_SUFFIX = ".materialization.yml"
APPROVED_RECORD_FORBIDDEN_KEYS = {
    "article_body",
    "body",
    "current_text",
    "operator_fill",
    "raw_article_body",
    "runtime_db_path",
    "screenshot_path",
    "source_catalog",
    "source_url",
    "url",
    "ymmp_path",
    "ymm4_geometry",
}


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


def approved_materialization_record_path(
    script_id: str,
    output_root: Path | str = APPROVED_MATERIALIZATION_DEFAULT_ROOT,
) -> Path:
    return Path(output_root) / f"{script_id}{APPROVED_MATERIALIZATION_SUFFIX}"


def write_approved_materialization_record(
    script: ScriptIR,
    draft_path: Path | str,
    *,
    story_cluster_id: str,
    episode_id: str | None,
    approved_by: str,
    approved_at: str | None = None,
    approval_note: str | None = None,
    output_root: Path | str = APPROVED_MATERIALIZATION_DEFAULT_ROOT,
    require_approved: bool = True,
) -> Path:
    payload = build_approved_materialization_record(
        script,
        draft_path,
        story_cluster_id=story_cluster_id,
        episode_id=episode_id,
        approved_by=approved_by,
        approved_at=approved_at,
        approval_note=approval_note,
        require_approved=require_approved,
    )
    output_path = approved_materialization_record_path(script.id, output_root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return output_path


def build_approved_materialization_record(
    script: ScriptIR,
    draft_path: Path | str,
    *,
    story_cluster_id: str,
    episode_id: str | None,
    approved_by: str,
    approved_at: str | None = None,
    approval_note: str | None = None,
    require_approved: bool = True,
) -> dict[str, Any]:
    approved_by_text = str(approved_by or "").strip()
    if not approved_by_text:
        raise MaterializationValidationError("approved_by is required")

    draft = _load_materialization_payload(Path(draft_path))
    replacements = _validated_replacements(script, draft, require_approved=require_approved)
    draft_by_id = _segments_by_id(draft.get("segments") or [])

    segments: list[dict[str, Any]] = []
    for index, segment in enumerate(script.segments, start=1):
        if segment.id not in replacements:
            continue
        draft_segment = draft_by_id[segment.id]
        segments.append(
            {
                "index": index,
                "segment_id": segment.id,
                "speaker": segment.speaker,
                "approved_text": replacements[segment.id],
                "source_refs": list(segment.source_refs),
                "critical_refs": list(draft_segment.get("critical_refs") or []),
                "visual_refs": list(segment.visual_refs),
                "claim_type": segment.claim_type,
                "human_review_required": segment.needs_human_review,
                "replacement_status": "approved",
            }
        )

    return {
        "schema_version": 1,
        "artifact_type": "approved_script_materialization",
        "mode": "operator_approved",
        "created_at": datetime.now(UTC).isoformat(),
        "script_id": script.id,
        "episode_plan_id": script.episode_plan_id,
        "story_cluster_id": story_cluster_id,
        "episode_id": episode_id,
        "format": script.format,
        "status": "approved",
        "approval": {
            "approved_by": approved_by_text,
            "approved_at": approved_at or datetime.now(UTC).isoformat(),
            "approval_note": approval_note,
        },
        "non_goals": [
            "does_not_include_raw_article_body",
            "does_not_include_private_data",
            "does_not_include_runtime_db_path",
            "does_not_include_screenshots",
            "does_not_include_ymm4_geometry",
        ],
        "segments": segments,
    }


def apply_approved_materialization_record(
    script: ScriptIR,
    record_path: Path | str,
) -> ScriptIR:
    record = _load_approved_materialization_record(Path(record_path))
    replacements = _validated_approved_record_replacements(script, record)
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


def _load_approved_materialization_record(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise MaterializationValidationError(
            f"Cannot read approved materialization record: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise MaterializationValidationError("Approved materialization record must be a mapping")
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

    draft_by_id = _segments_by_id(raw_segments, errors=errors, label="draft")

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


def _validated_approved_record_replacements(
    script: ScriptIR,
    record: dict[str, Any],
) -> dict[str, str]:
    errors: list[str] = []
    if record.get("script_id") != script.id:
        errors.append(f"record script_id {record.get('script_id')!r} does not match {script.id!r}")
    if record.get("artifact_type") != "approved_script_materialization":
        errors.append("record artifact_type must be approved_script_materialization")
    if record.get("status") != "approved":
        errors.append(f"record status must be approved, got {record.get('status')!r}")
    _validate_approval_block(record.get("approval"), errors)
    _reject_forbidden_approved_record_keys(record, errors)

    raw_segments = record.get("segments")
    if not isinstance(raw_segments, list):
        errors.append("record segments must be a list")
        raw_segments = []
    record_by_id = _segments_by_id(raw_segments, errors=errors, label="record")
    script_segment_ids = {segment.id for segment in script.segments}
    for segment_id in record_by_id:
        if segment_id not in script_segment_ids:
            errors.append(f"record segment {segment_id!r} is not present in ScriptIR")

    replacements: dict[str, str] = {}
    for segment in script.segments:
        if not segment.text.startswith("TODO["):
            continue
        record_segment = record_by_id.get(segment.id)
        if record_segment is None:
            errors.append(f"missing approved record segment for TODO segment {segment.id}")
            continue
        _validate_approved_segment_metadata(segment, record_segment, errors)
        approved_text = str(record_segment.get("approved_text") or "").strip()
        if not approved_text:
            errors.append(f"segment {segment.id} approved_text is empty")
        elif approved_text.startswith("TODO["):
            errors.append(f"segment {segment.id} approved_text still starts with TODO[")
        else:
            replacements[segment.id] = approved_text
        replacement_status = str(record_segment.get("replacement_status") or "")
        if replacement_status != "approved":
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


def _validate_approved_segment_metadata(
    segment: Any,
    record_segment: dict[str, Any],
    errors: list[str],
) -> None:
    if record_segment.get("speaker") != segment.speaker:
        errors.append(f"segment {segment.id} speaker does not match current ScriptIR speaker")
    record_source_refs = list(record_segment.get("source_refs") or [])
    if record_source_refs != segment.source_refs:
        errors.append(f"segment {segment.id} source_refs do not match current ScriptIR source_refs")
    record_visual_refs = list(record_segment.get("visual_refs") or [])
    if record_visual_refs != segment.visual_refs:
        errors.append(f"segment {segment.id} visual_refs do not match current ScriptIR visual_refs")
    if record_segment.get("claim_type") != segment.claim_type:
        errors.append(f"segment {segment.id} claim_type does not match current ScriptIR claim_type")
    if record_segment.get("human_review_required") != segment.needs_human_review:
        errors.append(
            f"segment {segment.id} human_review_required does not match current ScriptIR flag"
        )
    critical_refs = list(record_segment.get("critical_refs") or [])
    outside_source_refs = [ref for ref in critical_refs if ref not in segment.source_refs]
    if outside_source_refs:
        errors.append(
            f"segment {segment.id} critical_refs are not included in source_refs: {outside_source_refs}"
        )


def _validate_approval_block(raw_approval: Any, errors: list[str]) -> None:
    if not isinstance(raw_approval, dict):
        errors.append("record approval must be a mapping")
        return
    if not str(raw_approval.get("approved_by") or "").strip():
        errors.append("record approval.approved_by is required")
    if not str(raw_approval.get("approved_at") or "").strip():
        errors.append("record approval.approved_at is required")


def _reject_forbidden_approved_record_keys(value: Any, errors: list[str], path: str = "record") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            if key_text in APPROVED_RECORD_FORBIDDEN_KEYS:
                errors.append(f"{path}.{key_text} is not allowed in an approved record")
            _reject_forbidden_approved_record_keys(nested, errors, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_forbidden_approved_record_keys(nested, errors, f"{path}[{index}]")


def _segments_by_id(
    raw_segments: Any,
    *,
    errors: list[str] | None = None,
    label: str = "record",
) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for raw_segment in raw_segments:
        if not isinstance(raw_segment, dict):
            if errors is not None:
                errors.append(f"{label} segment entries must be mappings")
            continue
        segment_id = str(raw_segment.get("segment_id") or "")
        if not segment_id:
            if errors is not None:
                errors.append(f"{label} segment missing segment_id")
            continue
        if segment_id in by_id and errors is not None:
            errors.append(f"duplicate {label} segment_id {segment_id!r}")
        by_id[segment_id] = raw_segment
    return by_id


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
