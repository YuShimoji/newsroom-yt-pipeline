from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VisualUnit:
    id: str
    segment_refs: list[str]
    unit_type: str
    duration_sec: float
    layout_template: str
    source_refs: list[str] = field(default_factory=list)
    asset_refs: list[str] = field(default_factory=list)
    density_score: float = 0.0
    approval_state: str = "human_required"


@dataclass(frozen=True)
class VisualIR:
    id: str
    script_id: str
    visual_units: list[VisualUnit] = field(default_factory=list)

