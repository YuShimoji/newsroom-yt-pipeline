from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.store.models import (
    NotebookPacket,
    QuoteEntry,
    QuoteManifest,
    ScriptIR,
    SourceRef,
    VisualIR,
)


_PURPOSE_BY_CLAIM_TYPE: dict[str, str] = {
    "fact": "evidence",
    "interpretation": "explanation",
    "speculation": "comparison",
    "instruction": "background",
}


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
                source = source_lookup.get(source_id)
                if source is None:
                    continue
                entry = _text_quote_entry(segment.id, segment.claim_type, source)
                if entry.quote_id not in seen:
                    entries.append(entry)
                    seen.add(entry.quote_id)

        for unit in visual_ir.visual_units:
            if unit.unit_type not in {"source_card", "quote_screenshot"}:
                continue
            for source_id in unit.source_refs:
                source = source_lookup.get(source_id)
                if source is None:
                    continue
                entry = _screenshot_quote_entry(unit.id, source)
                if entry.quote_id not in seen:
                    entries.append(entry)
                    seen.add(entry.quote_id)

        return QuoteManifest(
            episode_id=episode_id,
            quotes=entries,
            created_at=datetime.now(UTC).isoformat(),
        )


def _source_lookup(packet: NotebookPacket) -> dict[str, SourceRef]:
    refs = (
        list(packet.primary_sources)
        + list(packet.news_sources)
        + list(packet.critical_views)
    )
    return {ref.article_id: ref for ref in refs}


def _text_quote_entry(
    segment_id: str,
    claim_type: str,
    source: SourceRef,
) -> QuoteEntry:
    purpose = _PURPOSE_BY_CLAIM_TYPE.get(claim_type, "explanation")
    return QuoteEntry(
        quote_id=_quote_id("text", segment_id, source.article_id),
        source_ref=source.article_id,
        quote_type="text",
        purpose=purpose,
        necessity=(
            f"Segment {segment_id} cites this source; verify direct quotation is "
            "necessary, minimal, and can be paraphrased if not."
        ),
        quoted_scope=f"script segment {segment_id}",
        main_subordinate_assessment=(
            "Newsroom analysis must remain primary; the source is supporting "
            "evidence only."
        ),
        distinction_method=(
            "Keep any quoted wording visually or verbally distinct and attach "
            "the source attribution."
        ),
        attribution=_attribution(source),
        risk_level="medium",
        approval_state="human_required",
    )


def _screenshot_quote_entry(unit_id: str, source: SourceRef) -> QuoteEntry:
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
    )


def _attribution(source: SourceRef) -> str:
    if source.published_at:
        return f"{source.source_name} ({source.published_at}) — {source.url}"
    return f"{source.source_name} — {source.url}"


def _quote_id(quote_type: str, scope_id: str, source_id: str) -> str:
    digest = sha256(f"{quote_type}|{scope_id}|{source_id}".encode("utf-8")).hexdigest()
    return f"quote_{digest[:16]}"
