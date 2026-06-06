from __future__ import annotations

from newsroom.script.episode_planner import EpisodePlanner
from newsroom.script.script_critic import ScriptCritic
from newsroom.script.script_drafter import ScriptDrafter
from newsroom.store.models import (
    Article,
    NotebookPacket,
    SourceRef,
    StoryCluster,
)


def _article(seed: str, source_type: str = "official") -> Article:
    return Article.create(
        url=f"https://example.com/{seed}",
        title=f"Copilot announcement {seed}",
        source_name=f"Source {seed}",
        source_type=source_type,
        published_at="2026-05-18T01:00:00+00:00",
        fetched_at="2026-05-18T02:00:00+00:00",
    )


def _cluster() -> StoryCluster:
    return StoryCluster(
        id="story_20260518_test",
        title="Copilot announcement",
        summary=None,
        article_ids=["a", "b"],
        primary_sources=["Source a"],
        related_series=["series/copilot"],
        entities=["microsoft", "copilot"],
        content_farm_overlap=0.0,
        cluster_date="2026-05-18",
        created_at="2026-05-18T02:00:00+00:00",
        updated_at="2026-05-18T02:00:00+00:00",
    )


def _packet(
    primary_article_id: str,
    news_article_id: str | None = None,
    critical_article_id: str | None = None,
) -> NotebookPacket:
    primary = [
        SourceRef(
            article_id=primary_article_id,
            url=f"https://example.com/{primary_article_id}",
            title=f"Copilot announcement {primary_article_id}",
            source_name=f"Source {primary_article_id}",
            source_type="official",
            published_at="2026-05-18T01:00:00+00:00",
        )
    ]
    news = []
    if news_article_id:
        news.append(
            SourceRef(
                article_id=news_article_id,
                url=f"https://example.com/{news_article_id}",
                title=f"Copilot announcement {news_article_id}",
                source_name=f"Source {news_article_id}",
                source_type="news",
                published_at="2026-05-18T03:00:00+00:00",
            )
        )
    critical = []
    if critical_article_id:
        critical.append(
            SourceRef(
                article_id=critical_article_id,
                url=f"https://example.com/{critical_article_id}",
                title=f"Critical view {critical_article_id}",
                source_name=f"Critical {critical_article_id}",
                source_type="commentary",
                published_at="2026-05-18T04:00:00+00:00",
            )
        )
    return NotebookPacket(
        id="packet_test",
        story_cluster_id="story_20260518_test",
        primary_sources=primary,
        news_sources=news,
        critical_views=critical,
        timeline=[],
        glossary=[],
        questions=[],
        format_hint="anchor",
        export_dir="data/packets/packet_test",
        created_at="2026-05-18T04:00:00+00:00",
    )


def test_drafter_produces_chapter_aware_segments():
    articles = [_article("a", source_type="official"), _article("b", source_type="news")]
    cluster = _cluster()
    cluster_with_ids = cluster.__class__(**{**cluster.__dict__, "article_ids": [a.id for a in articles]})
    packet = _packet(articles[0].id, articles[1].id)

    plan = EpisodePlanner().plan(cluster_with_ids, packet)
    script = ScriptDrafter().draft(plan, packet, "yukkuri_dialogue")

    chapter_keys = {segment.chapter_id.rsplit("__", 1)[-1] for segment in script.segments}
    assert {"intro", "facts", "context", "conflict", "impact", "takeaway"}.issubset(chapter_keys)

    facts_segment = next(seg for seg in script.segments if seg.chapter_id.endswith("__facts"))
    assert facts_segment.claim_type == "fact"
    assert facts_segment.source_refs  # facts chapter must carry source_refs

    conflict_segment = next(seg for seg in script.segments if seg.chapter_id.endswith("__conflict"))
    assert conflict_segment.source_refs == [articles[1].id]

    speakers = {segment.speaker for segment in script.segments if segment.chapter_id.endswith("__intro")}
    assert speakers.issubset({"霊夢", "魔理沙"})


def test_drafter_prefers_critical_views_for_conflict_chapter():
    articles = [
        _article("a", source_type="official"),
        _article("b", source_type="news"),
        _article("c", source_type="commentary"),
    ]
    cluster = _cluster()
    cluster_with_ids = cluster.__class__(**{**cluster.__dict__, "article_ids": [a.id for a in articles]})
    packet = _packet(articles[0].id, articles[1].id, articles[2].id)

    plan = EpisodePlanner().plan(cluster_with_ids, packet)
    script = ScriptDrafter().draft(plan, packet, "anchor_narration")

    conflict_segment = next(seg for seg in script.segments if seg.chapter_id.endswith("__conflict"))
    assert conflict_segment.source_refs == [articles[2].id]


def test_critic_flags_missing_sources_on_fact_segments():
    articles = [_article("a"), _article("b")]
    cluster = _cluster()
    cluster_with_ids = cluster.__class__(**{**cluster.__dict__, "article_ids": [a.id for a in articles]})
    packet = _packet(articles[0].id, articles[1].id)

    plan = EpisodePlanner().plan(cluster_with_ids, packet)
    script = ScriptDrafter().draft(plan, packet, "anchor_narration")

    stripped_segments = [
        seg.__class__(**{**seg.__dict__, "source_refs": []})
        if seg.claim_type == "fact"
        else seg
        for seg in script.segments
    ]
    stripped_script = script.__class__(**{**script.__dict__, "segments": stripped_segments})

    findings = ScriptCritic().critique(stripped_script, plan, packet)
    fact_finding = next(f for f in findings if f.guard == "factual_sources")
    assert fact_finding.severity == "fail"


def test_critic_warns_when_critical_view_missing():
    articles = [_article("a"), _article("b")]
    cluster = _cluster()
    cluster_with_ids = cluster.__class__(**{**cluster.__dict__, "article_ids": [a.id for a in articles]})
    packet = _packet(articles[0].id, articles[1].id)

    plan = EpisodePlanner().plan(cluster_with_ids, packet)
    script = ScriptDrafter().draft(plan, packet, "anchor_narration")
    findings = ScriptCritic().critique(script, plan, packet)

    critical = next(f for f in findings if f.guard == "critical_view")
    assert critical.severity == "warn"


def test_critic_keeps_speculation_warning_until_speculation_track_is_explicit():
    articles = [_article("a"), _article("b"), _article("c", source_type="commentary")]
    cluster = _cluster()
    cluster_with_ids = cluster.__class__(**{**cluster.__dict__, "article_ids": [a.id for a in articles]})
    packet = _packet(articles[0].id, articles[1].id, articles[2].id)

    plan = EpisodePlanner().plan(cluster_with_ids, packet)
    script = ScriptDrafter().draft(plan, packet, "anchor_narration")

    findings = ScriptCritic().critique(script, plan, packet)

    speculation = next(f for f in findings if f.guard == "speculation_vs_fact")
    assert speculation.severity == "warn"
    assert all(segment.needs_human_review for segment in script.segments)

    explicit_segments = [
        segment.__class__(**{**segment.__dict__, "claim_type": "speculation"})
        if segment.chapter_id.endswith("__impact")
        else segment
        for segment in script.segments
    ]
    explicit_script = script.__class__(**{**script.__dict__, "segments": explicit_segments})

    explicit_findings = ScriptCritic().critique(explicit_script, plan, packet)
    explicit_speculation = next(
        f for f in explicit_findings if f.guard == "speculation_vs_fact"
    )
    assert explicit_speculation.severity == "ok"
    assert all(segment.needs_human_review for segment in explicit_script.segments)
