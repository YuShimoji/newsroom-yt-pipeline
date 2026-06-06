from __future__ import annotations

import yaml

from newsroom.assets.exporters import write_quote_manifest
from newsroom.assets.quote_manifest import QuoteManifestBuilder
from newsroom.store.models import (
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    SourceRef,
    VisualIR,
    VisualUnit,
)


def _source_ref(article_id: str, source_type: str = "official") -> SourceRef:
    return SourceRef(
        article_id=article_id,
        url=f"https://example.com/{article_id}",
        title=f"Title {article_id}",
        source_name=f"Source {article_id}",
        source_type=source_type,
        published_at="2026-05-27T00:00:00+00:00",
    )


def _packet() -> NotebookPacket:
    return NotebookPacket(
        id="packet_test",
        story_cluster_id="story_test",
        primary_sources=[_source_ref("article_a", "official")],
        news_sources=[_source_ref("article_b", "news")],
        critical_views=[_source_ref("article_c", "commentary")],
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_test",
        created_at="2026-05-27T00:00:00+00:00",
    )


def _script() -> ScriptIR:
    return ScriptIR(
        id="script_test",
        episode_plan_id="plan_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_facts",
                chapter_id="plan_test__facts",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_a"],
                visual_refs=[],
                claim_type="fact",
                needs_human_review=True,
            ),
            ScriptSegment(
                id="seg_context",
                chapter_id="plan_test__context",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_b"],
                visual_refs=[],
                claim_type="interpretation",
                needs_human_review=True,
            ),
            ScriptSegment(
                id="seg_conflict",
                chapter_id="plan_test__conflict",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_c"],
                visual_refs=[],
                claim_type="interpretation",
                needs_human_review=True,
            ),
        ],
        created_at="2026-05-27T01:00:00+00:00",
    )


def _visual_ir() -> VisualIR:
    return VisualIR(
        id="visual_test",
        script_id="script_test",
        visual_units=[
            VisualUnit(
                id="unit_source",
                segment_refs=["seg_facts"],
                unit_type="source_card",
                duration_sec=60.0,
                layout_template="source_card_v1",
                source_refs=["article_a"],
                density_score=6.0,
                approval_state="human_required",
            ),
            VisualUnit(
                id="unit_context",
                segment_refs=["seg_context"],
                unit_type="claim_evidence_card",
                duration_sec=60.0,
                layout_template="claim_evidence_card_v1",
                source_refs=["article_b"],
                density_score=6.0,
                approval_state="auto_ok",
            ),
        ],
        created_at="2026-05-27T02:00:00+00:00",
    )


def test_quote_manifest_covers_text_and_source_card_screenshot():
    manifest = QuoteManifestBuilder().build(
        _script(),
        _visual_ir(),
        _packet(),
        episode_id="plan_test",
    )

    assert manifest.episode_id == "plan_test"
    assert len(manifest.quotes) == 4
    assert {quote.quote_type for quote in manifest.quotes} == {"text", "screenshot"}
    assert sum(quote.approval_state == "citation_only" for quote in manifest.quotes) == 3
    assert sum(quote.approval_state == "human_required" for quote in manifest.quotes) == 1

    fact_quote = next(
        quote
        for quote in manifest.quotes
        if quote.quote_type == "text" and quote.source_ref == "article_a"
    )
    assert fact_quote.purpose == "evidence"
    assert fact_quote.review_level == "citation_only"
    assert fact_quote.source_role == "primary"
    assert fact_quote.risk_level == "low"
    assert "seg_facts" in fact_quote.quoted_scope

    critical_quote = next(
        quote
        for quote in manifest.quotes
        if quote.quote_type == "text" and quote.source_ref == "article_c"
    )
    assert critical_quote.source_role == "critical_view"

    screenshot = next(quote for quote in manifest.quotes if quote.quote_type == "screenshot")
    assert screenshot.source_ref == "article_a"
    assert screenshot.review_level == "screenshot"
    assert screenshot.approval_state == "human_required"
    assert "source-card screenshot" in screenshot.necessity
    assert screenshot.risk_level == "medium"


def test_direct_quote_intent_remains_human_required():
    script = ScriptIR(
        id="script_test",
        episode_plan_id="plan_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_quote",
                chapter_id="plan_test__facts",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_a"],
                claim_type="direct_quote",
            )
        ],
        created_at="2026-05-27T01:00:00+00:00",
    )

    manifest = QuoteManifestBuilder().build(
        script,
        VisualIR(
            id="visual_test",
            script_id="script_test",
            visual_units=[],
            created_at="2026-05-27T02:00:00+00:00",
        ),
        _packet(),
        episode_id="plan_test",
    )

    quote = manifest.quotes[0]
    assert quote.quote_type == "text"
    assert quote.review_level == "direct_quote"
    assert quote.approval_state == "human_required"
    assert quote.source_ref == "article_a"


def test_data_use_intent_remains_human_required():
    script = ScriptIR(
        id="script_test",
        episode_plan_id="plan_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_data",
                chapter_id="plan_test__facts",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_b"],
                claim_type="data_use",
            )
        ],
        created_at="2026-05-27T01:00:00+00:00",
    )

    manifest = QuoteManifestBuilder().build(
        script,
        VisualIR(
            id="visual_test",
            script_id="script_test",
            visual_units=[],
            created_at="2026-05-27T02:00:00+00:00",
        ),
        _packet(),
        episode_id="plan_test",
    )

    quote = manifest.quotes[0]
    assert quote.quote_type == "data"
    assert quote.review_level == "data_use"
    assert quote.approval_state == "human_required"
    assert quote.source_ref == "article_b"
    assert quote.source_role == "news"


def test_quote_manifest_ignores_unknown_sources_and_deduplicates():
    script = ScriptIR(
        id="script_test",
        episode_plan_id="plan_test",
        format="anchor_narration",
        segments=[
            ScriptSegment(
                id="seg_dup",
                chapter_id="plan_test__facts",
                speaker="ナレーター",
                text="TODO",
                source_refs=["article_a", "article_a", "missing"],
                claim_type="fact",
            )
        ],
        created_at="2026-05-27T01:00:00+00:00",
    )

    manifest = QuoteManifestBuilder().build(
        script,
        _visual_ir(),
        _packet(),
        episode_id="plan_test",
    )

    text_quotes = [quote for quote in manifest.quotes if quote.quote_type == "text"]
    assert len(text_quotes) == 1
    assert text_quotes[0].source_ref == "article_a"
    assert text_quotes[0].review_level == "citation_only"
    assert text_quotes[0].approval_state == "citation_only"


def test_quote_manifest_round_trips_through_yaml(tmp_path):
    manifest = QuoteManifestBuilder().build(
        _script(),
        _visual_ir(),
        _packet(),
        episode_id="plan_test",
    )

    output_dir = write_quote_manifest(manifest, quote_root=tmp_path)

    yaml_path = output_dir / "quote_manifest.yml"
    assert yaml_path.exists()
    payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    assert payload["episode_id"] == "plan_test"
    assert len(payload["quotes"]) == 4
    assert payload["quotes"][0]["review_level"] == "citation_only"
    assert payload["quotes"][0]["approval_state"] == "citation_only"
    assert payload["quotes"][0]["source_role"] == "primary"
