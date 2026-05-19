from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.store.models import (
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    VisualIR,
    VisualUnit,
)


# M6.1 keeps the card vocabulary deliberately narrow. The remaining card
# types from PROJECT_SPEC §14 (version_diff / actor_map / risk_meter /
# context_stack / quote_screenshot / neutral_background) belong to later
# M6 slices.
SUPPORTED_UNIT_TYPES: frozenset[str] = frozenset(
    {"source_card", "claim_evidence_card", "timeline_spine", "takeaway_row"}
)


CHAPTER_TO_UNIT_TYPE: dict[str, str] = {
    "intro": "takeaway_row",
    "facts": "source_card",
    "context": "claim_evidence_card",
    "conflict": "claim_evidence_card",
    "impact": "takeaway_row",
    "takeaway": "takeaway_row",
}

LAYOUT_TEMPLATES: dict[str, str] = {
    "source_card": "source_card_v1",
    "claim_evidence_card": "claim_evidence_card_v1",
    "timeline_spine": "timeline_spine_v1",
    "takeaway_row": "takeaway_row_v1",
}

# §14: 8〜12 秒に 1 回意味のある視覚更新を入れる。中央値 10 秒で正規化する。
DENSITY_TARGET_SECONDS_PER_UPDATE: float = 10.0

# Only source_card surfaces external URLs / quoted content, so operator
# approval stays required. The other three cards are derived from
# internal structure (claims, timeline, takeaway sentences).
APPROVAL_BY_UNIT_TYPE: dict[str, str] = {
    "source_card": "human_required",
    "claim_evidence_card": "auto_ok",
    "timeline_spine": "auto_ok",
    "takeaway_row": "auto_ok",
}


class VisualPlanner:
    """Translate a ScriptIR into a VisualIR using four core card templates."""

    def plan(
        self,
        script: ScriptIR,
        episode_plan: EpisodePlan,
        packet: NotebookPacket,
    ) -> VisualIR:
        chapter_lookup = {chapter.id: chapter for chapter in episode_plan.chapter_outline}
        segments_by_chapter = _group_segments_by_chapter(script.segments)

        all_source_refs = [ref.article_id for ref in packet.primary_sources] + [
            ref.article_id for ref in packet.news_sources
        ]

        now = datetime.now(UTC).isoformat()
        visual_ir_id = _visual_ir_id(script.id)

        units: list[VisualUnit] = []
        for index, chapter in enumerate(episode_plan.chapter_outline):
            segments = segments_by_chapter.get(chapter.id, [])
            chapter_key = chapter.id.rsplit("__", 1)[-1]
            unit_type = CHAPTER_TO_UNIT_TYPE.get(chapter_key, "takeaway_row")
            duration_sec = float(chapter.target_duration_sec)
            source_refs = _source_refs_for_chapter(
                chapter_key=chapter_key,
                packet=packet,
                fallback=all_source_refs,
            )
            unit = VisualUnit(
                id=f"{visual_ir_id}__u{index:02d}_{chapter_key}",
                segment_refs=[segment.id for segment in segments],
                unit_type=unit_type,
                duration_sec=duration_sec,
                layout_template=LAYOUT_TEMPLATES[unit_type],
                source_refs=source_refs,
                asset_refs=[],
                density_score=_density_score(duration_sec),
                approval_state=APPROVAL_BY_UNIT_TYPE[unit_type],
            )
            units.append(unit)

        if len(packet.timeline) >= 2:
            facts_chapter = next(
                (c for c in episode_plan.chapter_outline if c.id.endswith("__facts")),
                None,
            )
            if facts_chapter is not None:
                facts_segments = segments_by_chapter.get(facts_chapter.id, [])
                timeline_unit = VisualUnit(
                    id=f"{visual_ir_id}__timeline",
                    segment_refs=[segment.id for segment in facts_segments],
                    unit_type="timeline_spine",
                    duration_sec=float(facts_chapter.target_duration_sec),
                    layout_template=LAYOUT_TEMPLATES["timeline_spine"],
                    source_refs=[event.article_id for event in packet.timeline],
                    asset_refs=[],
                    density_score=_density_score(facts_chapter.target_duration_sec),
                    approval_state=APPROVAL_BY_UNIT_TYPE["timeline_spine"],
                )
                units.append(timeline_unit)

        return VisualIR(
            id=visual_ir_id,
            script_id=script.id,
            visual_units=units,
            created_at=now,
        )


def _visual_ir_id(script_id: str) -> str:
    digest = sha256(script_id.encode("utf-8")).hexdigest()[:12]
    return f"visual_{digest}"


def _group_segments_by_chapter(segments: list[ScriptSegment]) -> dict[str, list[ScriptSegment]]:
    grouped: dict[str, list[ScriptSegment]] = {}
    for segment in segments:
        grouped.setdefault(segment.chapter_id, []).append(segment)
    return grouped


def _source_refs_for_chapter(
    chapter_key: str, packet: NotebookPacket, fallback: list[str]
) -> list[str]:
    if chapter_key == "facts":
        primary = [ref.article_id for ref in packet.primary_sources]
        return primary or fallback
    if chapter_key == "conflict":
        news = [ref.article_id for ref in packet.news_sources]
        critical = [ref.article_id for ref in packet.critical_views]
        return critical or news or fallback
    return fallback


def _density_score(duration_sec: float) -> float:
    if duration_sec <= 0:
        return 0.0
    return round(duration_sec / DENSITY_TARGET_SECONDS_PER_UPDATE, 4)
