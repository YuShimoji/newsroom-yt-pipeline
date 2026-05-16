from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetRecord:
    asset_id: str
    type: str
    source_url: str | None
    intended_use: str
    approval_state: str = "human_required"
    risk_level: str = "medium"


class AssetRegistry:
    """M6 placeholder.

    Asset discovery and download are intentionally not implemented in M1.
    """

    def suggest(self) -> list[AssetRecord]:
        return []

