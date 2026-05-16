from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScriptSegment:
    id: str
    chapter_id: str
    speaker: str
    text: str
    source_refs: list[str] = field(default_factory=list)
    visual_refs: list[str] = field(default_factory=list)
    claim_type: str = "interpretation"
    needs_human_review: bool = True


@dataclass(frozen=True)
class ScriptIR:
    id: str
    episode_plan_id: str
    format: str
    segments: list[ScriptSegment] = field(default_factory=list)

