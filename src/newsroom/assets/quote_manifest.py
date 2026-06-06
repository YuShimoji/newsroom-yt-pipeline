from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.store.models import (
    NotebookPacket,
    QuoteEntry,
    QuoteManifest,
    ScriptIR,
    ScriptSegment,
    SourceRef,
    VisualIR,
)


_PURPOSE_BY_CLAIM_TYPE: dict[str, str] = {
    "fact": "evidence",
    "interpretation": "explanation",
    "speculation": "comparison",
    "instruction": "background",
    "direct_quote": "quotation",
    "quote": "quotation",
    "data": "data_use",
    "data_use": "data_use",
}

_DIRECT_QUOTE_CLAIM_TYPES = {"direct_quote", "quote"}
_DATA_USE_CLAIM_TYPES = {"data", "data_use"}


class QuoteManifestBuilder:
    """Build the M6.3 quote review manifest from script and visual intent.

    The builder does not decide legal acceptability. It creates editable
    review rows for source-backed narration and source-card screenshots so
    the operator can explicitly approve, reject, or rewrite each use.
    """

    def build(
        self,
        script: ScriptIR,
        visual_ir: VisualIR,
        packet: NotebookPacket,
        *,
        episode_id: str,
    ) -> QuoteManifest:
        source_lookup = _source_lookup(packet)
        entries: list[QuoteEntry] = []
        seen: set[str] = set()

        for segment in script.segments:
            for source_id in segment.source_refs:
                source_entry = source_lookup.get(source_id)
                if source_entry is None:
                    continue
                source, source_role = source_entry
                entry = _text_quote_entry(segment, source, source_role)
                if entry.quote_id not in seen:
                    entries.append(entry)
                    seen.add(entry.quote_id)

        for unit in visual_ir.visual_units:
            if unit.unit_type not in {"source_card", "quote_screenshot"}:
                continue
            for source_id in unit.source_refs:
                source_entry = source_lookup.get(source_id)
                if source_entry is None:
                    continue
                source, source_role = source_entry
                entry = _screenshot_quote_entry(unit.id, source, source_role)
                if entry.quote_id not in seen:
                    entries.append(entry)
                    seen.add(entry.quote_id)

        return QuoteManifest(
            episode_id=episode_id,
            quotes=entries,
            created_at=datetime.now(UTC).isoformat(),
        )


def _source_lookup(packet: NotebookPacket) -> dict[str, tuple[SourceRef, str]]:
    refs: list[tuple[SourceRef, str]] = []
    refs.extend((ref, "primary") for ref in packet.primary_sources)
    refs.extend((ref, "news") for ref in packet.news_sources)
    refs.extend((ref, "critical_view") for ref in packet.critical_views)
    return {ref.article_id: (ref, role) for ref, role in refs}


def _text_quote_entry(
    segment: ScriptSegment,
    source: SourceRef,
    source_role: str,
) -> QuoteEntry:
    review_level = _text_review_level(segment)
    quote_type = "data" if review_level == "data_use" else "text"
    approval_state = "citation_only" if review_level == "citation_only" else "human_required"
    risk_level = "low" if review_level == "citation_only" else "medium"
    claim_type = segment.claim_type.strip().lower()
    purpose = _PURPOSE_BY_CLAIM_TYPE.get(claim_type, "explanation")

    if review_level == "citation_only":
        necessity = (
            f"Segment {segment.id} cites this source for attribution or evidence; "
            "no direct quotation, screenshot, or data extraction is planned."
        )
        distinction_method = (
            "Keep attribution in the source list or narration notes; do not present "
            "source wording as a quote unless a direct-quote review row is added."
        )
    elif review_level == "data_use":
        necessity = (
            f"Segment {segment.id} uses source-backed data intent; verify the data "
            "selection, transformation, denominator, and attribution before publishing."
        )
        distinction_method = (
            "Label the data source and transformation clearly; keep analysis separate "
            "from any source table or figure reproduction."
        )
    else:
        necessity = (
            f"Segment {segment.id} carries direct quote intent; verify quoted wording "
            "is necessary, minimal, attributed, and can be paraphrased if not."
        )
        distinction_method = (
            "Keep quoted wording visually or verbally distinct and attach the source "
            "attribution."
        )

    return QuoteEntry(
        quote_id=_quote_id(quote_type, segment.id, source.article_id),
        source_ref=source.article_id,
        quote_type=quote_type,
        purpose=purpose,
        necessity=necessity,
        quoted_scope=f"script segment {segment.id}",
        main_subordinate_assessment=(
            "Newsroom analysis must remain primary; the source is supporting "
            "evidence only."
        ),
        distinction_method=distinction_method,
        attribution=_attribution(source),
        risk_level=risk_level,
        approval_state=approval_state,
        review_level=review_level,
        source_role=source_role,
    )


def _text_review_level(segment: ScriptSegment) -> str:
    claim_type = segment.claim_type.strip().lower()
    visual_refs = [ref.strip().lower() for ref in segment.visual_refs]
    if claim_type in _DATA_USE_CLAIM_TYPES or any(
        ref.startswith(("data:", "data_use:")) for ref in visual_refs
    ):
        return "data_use"
    if claim_type in _DIRECT_QUOTE_CLAIM_TYPES or any(
        ref.startswith(("quote:", "direct_quote:")) for ref in visual_refs
    ):
        return "direct_quote"
    return "citation_only"


def _screenshot_quote_entry(
    unit_id: str,
    source: SourceRef,
    source_role: str,
) -> QuoteEntry:
    return QuoteEntry(
        quote_id=_quote_id("screenshot", unit_id, source.article_id),
        source_ref=source.article_id,
        quote_type="screenshot",
        purpose="evidence",
        necessity=(
            f"Visual unit {unit_id} uses a source-card screenshot candidate; "
            "confirm the screenshot is needed instead of a local diagram."
        ),
        quoted_scope=f"visual unit {unit_id}",
        main_subordinate_assessment=(
            "The screenshot must be subordinate to original explanation and "
            "should not become the main visual value."
        ),
        distinction_method=(
            "Show as a bounded source card with visible attribution and avoid "
            "full-page reproduction."
        ),
        attribution=_attribution(source),
        risk_level="medium",
        approval_state="human_required",
        review_level="screenshot",
        source_role=source_role,
    )


def _attribution(source: SourceRef) -> str:
    if source.published_at:
        return f"{source.source_name} ({source.published_at}) — {source.url}"
    return f"{source.source_name} — {source.url}"


def _quote_id(quote_type: str, scope_id: str, source_id: str) -> str:
    digest = sha256(f"{quote_type}|{scope_id}|{source_id}".encode("utf-8")).hexdigest()
    return f"quote_{digest[:16]}"
