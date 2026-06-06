from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from newsroom.script.exporters import DEFAULT_SCRIPT_ROOT
from newsroom.store.models import EpisodePlan, NotebookPacket, ScriptIR


MATERIALIZATION_FILENAME = "script_materialization.yml"


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
        "source_catalog": source_catalog,
        "segments": segments,
    }


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
