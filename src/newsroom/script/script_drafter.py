from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.config import SpeakerConfig
from newsroom.script.speakers import speaker_for_index
from newsroom.store.models import (
    Chapter,
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
)


SUPPORTED_FORMATS = {"yukkuri_dialogue", "anchor_narration"}


_CHAPTER_INTENT_TO_CLAIM: dict[str, str] = {
    "intro": "instruction",
    "facts": "fact",
    "context": "interpretation",
    "conflict": "interpretation",
    "impact": "interpretation",
    "takeaway": "instruction",
}


class ScriptDrafter:
    """Render a ScriptIR skeleton from an EpisodePlan and its NotebookPacket.

    The skeleton intentionally leaves segment.text as a TODO-shaped
    placeholder. An operator (or a later Gear-1 LLM step) is expected to
    fill the spoken text. The drafter only enforces structure: speaker
    rotation for yukkuri, claim_type per chapter intent, source_refs
    seeded from packet.primary_sources.
    """

    def __init__(self, speaker_config: SpeakerConfig | None = None) -> None:
        self.speaker_config = speaker_config

    def draft(
        self,
        plan: EpisodePlan,
        packet: NotebookPacket,
        format_name: str,
    ) -> ScriptIR:
        if format_name not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported script format: {format_name}")

        primary_refs = [ref.article_id for ref in packet.primary_sources]
        news_refs = [ref.article_id for ref in packet.news_sources]
        all_refs = primary_refs + news_refs

        now = datetime.now(UTC).isoformat()
        script_id = _script_id(plan.id, format_name)

        segments: list[ScriptSegment] = []
        index = 0
        for chapter in plan.chapter_outline:
            chapter_segments = _segments_for_chapter(
                chapter=chapter,
                format_name=format_name,
                start_index=index,
                primary_refs=primary_refs,
                news_refs=news_refs,
                all_refs=all_refs,
                speaker_config=self.speaker_config,
            )
            segments.extend(chapter_segments)
            index += len(chapter_segments)

        return ScriptIR(
            id=script_id,
            episode_plan_id=plan.id,
            format=format_name,
            segments=segments,
            created_at=now,
        )


def _script_id(plan_id: str, format_name: str) -> str:
    digest = sha256(f"{plan_id}|{format_name}".encode("utf-8")).hexdigest()[:12]
    return f"script_{digest}"


def _segments_for_chapter(
    chapter: Chapter,
    format_name: str,
    start_index: int,
    primary_refs: list[str],
    news_refs: list[str],
    all_refs: list[str],
    speaker_config: SpeakerConfig | None = None,
) -> list[ScriptSegment]:
    chapter_key = chapter.id.rsplit("__", 1)[-1]
    claim_type = _CHAPTER_INTENT_TO_CLAIM.get(chapter_key, "interpretation")

    if format_name == "yukkuri_dialogue":
        slot_count = 2
    else:
        slot_count = 1

    if chapter_key == "facts":
        source_pool = primary_refs or all_refs
    elif chapter_key == "conflict":
        source_pool = news_refs or all_refs
    else:
        source_pool = all_refs

    segments: list[ScriptSegment] = []
    for slot in range(slot_count):
        segment_id = f"{chapter.id}__s{slot}"
        speaker = speaker_for_index(format_name, start_index + slot, speaker_config)
        text = _placeholder_text(chapter, slot)
        segments.append(
            ScriptSegment(
                id=segment_id,
                chapter_id=chapter.id,
                speaker=speaker,
                text=text,
                source_refs=list(source_pool),
                visual_refs=[f"visual:{chapter.id}"],
                claim_type=claim_type,
                needs_human_review=True,
            )
        )
    return segments


def _placeholder_text(chapter: Chapter, slot: int) -> str:
    return (
        f"TODO[{chapter.id}#{slot}]: {chapter.intent}。"
        f"目安 {chapter.target_duration_sec} 秒以内で話す内容を operator が記入する。"
    )
