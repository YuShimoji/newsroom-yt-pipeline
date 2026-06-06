from __future__ import annotations

from newsroom.layout.visual_planner import (
    APPROVAL_BY_UNIT_TYPE,
    CHAPTER_TO_UNIT_TYPE,
    DENSITY_TARGET_SECONDS_PER_UPDATE,
    VisualPlanner,
)
from newsroom.store.models import (
    Chapter,
    EpisodePlan,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    SourceRef,
    TimelineEvent,
)


def _plan_with_full_chapters() -> EpisodePlan:
    keys_and_durations = [
        ("intro", 60),
        ("facts", 150),
        ("context", 120),
        ("conflict", 120),
        ("impact", 90),
        ("takeaway", 60),
    ]
    chapters = [
        Chapter(
            id=f"plan_test__{key}",
            title=f"chapter-{key}",
            intent=f"intent-{key}",
            target_duration_sec=duration,
        )
        for key, duration in keys_and_durations
    ]
    return EpisodePlan(
        id="plan_test",
        story_cluster_id="story_test",
        series_id=None,
        title_candidates=[],
        thumbnail_angles=[],
        hook="hook",
        chapter_outline=chapters,
        target_duration_sec=600,
        viewer_utility="utility",
        risk_notes=[],
        approval_state="draft",
        created_at="2026-05-18T00:00:00+00:00",
    )


def _script_with_one_segment_per_chapter(
    plan: EpisodePlan,
    visual_refs_by_chapter: dict[str, list[str]] | None = None,
) -> ScriptIR:
    visual_refs_by_chapter = visual_refs_by_chapter or {}
    segments = [
        ScriptSegment(
            id=f"{chapter.id}__s0",
            chapter_id=chapter.id,
            speaker="ナレーター",
            text="TODO",
            source_refs=["article_a"],
            visual_refs=visual_refs_by_chapter.get(
                chapter.id.rsplit("__", 1)[-1],
                [],
            ),
            claim_type="fact" if chapter.id.endswith("__facts") else "interpretation",
            needs_human_review=True,
        )
        for chapter in plan.chapter_outline
    ]
    return ScriptIR(
        id="script_test",
        episode_plan_id=plan.id,
        format="anchor_narration",
        segments=segments,
        created_at="2026-05-18T01:00:00+00:00",
    )


def _packet(timeline_events: int = 0) -> NotebookPacket:
    primary = [
        SourceRef(
            article_id="article_a",
            url="https://example.com/a",
            title="Primary",
            source_name="Microsoft Blog",
            source_type="official",
            published_at="2026-05-18T00:00:00+00:00",
        )
    ]
    news = [
        SourceRef(
            article_id="article_b",
            url="https://example.com/b",
            title="News",
            source_name="The Verge",
            source_type="news",
            published_at="2026-05-18T01:00:00+00:00",
        )
    ]
    timeline = [
        TimelineEvent(
            occurred_at=f"2026-05-1{index}T00:00:00+00:00",
            source_name=f"Source {index}",
            title=f"Event {index}",
            article_id=f"article_{index}",
            url=f"https://example.com/{index}",
        )
        for index in range(timeline_events)
    ]
    return NotebookPacket(
        id="packet_test",
        story_cluster_id="story_test",
        primary_sources=primary,
        news_sources=news,
        critical_views=[],
        timeline=timeline,
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_test",
        created_at="2026-05-18T02:00:00+00:00",
    )


def test_planner_emits_one_unit_per_chapter_with_expected_card_types():
    plan = _plan_with_full_chapters()
    script = _script_with_one_segment_per_chapter(plan)
    packet = _packet(timeline_events=0)

    visual_ir = VisualPlanner().plan(script, plan, packet)

    assert len(visual_ir.visual_units) == 6
    for chapter in plan.chapter_outline:
        chapter_key = chapter.id.rsplit("__", 1)[-1]
        expected_type = CHAPTER_TO_UNIT_TYPE[chapter_key]
        unit = next(
            u for u in visual_ir.visual_units
            if any(ref.startswith(chapter.id + "__") for ref in u.segment_refs)
        )
        assert unit.unit_type == expected_type
        assert unit.approval_state == APPROVAL_BY_UNIT_TYPE[expected_type]


def test_planner_appends_timeline_spine_when_packet_timeline_has_two_or_more():
    plan = _plan_with_full_chapters()
    script = _script_with_one_segment_per_chapter(plan)

    visual_ir_no_timeline = VisualPlanner().plan(script, plan, _packet(timeline_events=1))
    assert all(u.unit_type != "timeline_spine" for u in visual_ir_no_timeline.visual_units)

    visual_ir_with_timeline = VisualPlanner().plan(script, plan, _packet(timeline_events=3))
    timeline_units = [u for u in visual_ir_with_timeline.visual_units if u.unit_type == "timeline_spine"]
    assert len(timeline_units) == 1
    assert timeline_units[0].approval_state == "auto_ok"


def test_density_score_matches_chapter_duration_over_target_window():
    plan = _plan_with_full_chapters()
    script = _script_with_one_segment_per_chapter(plan)
    visual_ir = VisualPlanner().plan(script, plan, _packet())

    facts_unit = next(
        u for u in visual_ir.visual_units
        if any("__facts__" in ref for ref in u.segment_refs)
    )
    expected = round(150 / DENSITY_TARGET_SECONDS_PER_UPDATE, 4)
    assert facts_unit.density_score == expected


def test_citation_only_facts_use_local_card_without_human_required_visual_review():
    plan = _plan_with_full_chapters()
    script = _script_with_one_segment_per_chapter(plan)
    visual_ir = VisualPlanner().plan(script, plan, _packet())

    facts_unit = next(
        u for u in visual_ir.visual_units
        if any("__facts__" in ref for ref in u.segment_refs)
    )
    assert facts_unit.unit_type == "claim_evidence_card"
    assert facts_unit.approval_state == "auto_ok"
    assert all(u.approval_state != "human_required" for u in visual_ir.visual_units)


def test_explicit_source_card_intent_keeps_human_approval():
    plan = _plan_with_full_chapters()
    script = _script_with_one_segment_per_chapter(
        plan,
        visual_refs_by_chapter={"facts": ["source_card:article_a"]},
    )
    visual_ir = VisualPlanner().plan(script, plan, _packet())

    facts_unit = next(
        u for u in visual_ir.visual_units
        if any("__facts__" in ref for ref in u.segment_refs)
    )
    assert facts_unit.unit_type == "source_card"
    assert facts_unit.approval_state == "human_required"
