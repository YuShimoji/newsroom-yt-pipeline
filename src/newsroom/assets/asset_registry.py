from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.store.models import (
    AssetCandidate,
    AssetManifest,
    NotebookPacket,
    SourceRef,
    VisualIR,
    VisualUnit,
)


# Map VisualUnit.unit_type to the default candidate asset type. Stays
# narrow to match the four cards M6.1 emits.
_DEFAULT_ASSET_TYPE: dict[str, str] = {
    "source_card": "screenshot",
    "claim_evidence_card": "local_template",
    "timeline_spine": "generated_diagram",
    "takeaway_row": "local_template",
}


class AssetRegistry:
    """Suggest asset candidates for each VisualUnit in a VisualIR.

    Reads configs/quote_policy.yml indirectly: external-URL assets always
    take approval_state = human_required because the policy default is
    max_unreviewed_external_assets = 0. Internal (local_template /
    generated_diagram) candidates start as 'suggested' so the operator
    sees them in the manifest but is not blocked.
    """

    def suggest(
        self,
        visual_ir: VisualIR,
        packet: NotebookPacket,
        episode_id: str | None = None,
    ) -> AssetManifest:
        source_lookup = {
            ref.article_id: ref
            for ref in (
                list(packet.primary_sources)
                + list(packet.news_sources)
                + list(packet.critical_views)
            )
        }

        candidates: list[AssetCandidate] = []
        for unit in visual_ir.visual_units:
            for candidate in _suggest_for_unit(unit, source_lookup):
                candidates.append(candidate)

        resolved_episode_id = episode_id or _episode_id_from_visual(visual_ir)
        return AssetManifest(
            episode_id=resolved_episode_id,
            assets=candidates,
            created_at=datetime.now(UTC).isoformat(),
        )


def _episode_id_from_visual(visual_ir: VisualIR) -> str:
    digest = sha256(visual_ir.id.encode("utf-8")).hexdigest()[:12]
    return f"episode_{digest}"


def _suggest_for_unit(
    unit: VisualUnit, source_lookup: dict[str, SourceRef]
) -> list[AssetCandidate]:
    candidates: list[AssetCandidate] = []
    asset_type = _DEFAULT_ASSET_TYPE.get(unit.unit_type, "local_template")

    if asset_type == "screenshot":
        for source_ref_id in unit.source_refs:
            source_ref = source_lookup.get(source_ref_id)
            if source_ref is None:
                continue
            candidates.append(
                _screenshot_candidate(unit=unit, source_ref=source_ref)
            )
        if not candidates:
            candidates.append(_local_template_fallback(unit=unit))
    else:
        candidates.append(_internal_candidate(unit=unit, asset_type=asset_type))

    return candidates


def _screenshot_candidate(unit: VisualUnit, source_ref: SourceRef) -> AssetCandidate:
    return AssetCandidate(
        asset_id=f"asset_{unit.id}__{source_ref.article_id}",
        type="screenshot",
        source_url=source_ref.url,
        source_title=source_ref.title,
        author=None,
        captured_at=None,
        intended_use=f"Cite primary source in {unit.unit_type}",
        quote_reason="出典提示",
        display_duration_sec=unit.duration_sec,
        crop_ratio=None,
        modification="none",
        attribution_text=source_ref.source_name,
        risk_level="medium",
        approval_state="human_required",
    )


def _local_template_fallback(unit: VisualUnit) -> AssetCandidate:
    return AssetCandidate(
        asset_id=f"asset_{unit.id}__local_fallback",
        type="local_template",
        source_url=None,
        source_title=None,
        author=None,
        captured_at=None,
        intended_use=f"Local fallback for {unit.unit_type}; no source_ref available.",
        quote_reason=None,
        display_duration_sec=unit.duration_sec,
        crop_ratio=None,
        modification="none",
        attribution_text=None,
        risk_level="low",
        approval_state="suggested",
    )


def _internal_candidate(unit: VisualUnit, asset_type: str) -> AssetCandidate:
    return AssetCandidate(
        asset_id=f"asset_{unit.id}__{asset_type}",
        type=asset_type,
        source_url=None,
        source_title=None,
        author=None,
        captured_at=None,
        intended_use=_intended_use_for(unit.unit_type, asset_type),
        quote_reason=None,
        display_duration_sec=unit.duration_sec,
        crop_ratio=None,
        modification="none",
        attribution_text=None,
        risk_level="low",
        approval_state="suggested",
    )


def _intended_use_for(unit_type: str, asset_type: str) -> str:
    if asset_type == "generated_diagram":
        return f"Render an internal diagram for {unit_type} (no external source)."
    return f"Render a local template card for {unit_type} (no external source)."
