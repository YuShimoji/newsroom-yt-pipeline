from __future__ import annotations

from newsroom.store.db import (
    load_episode_plan,
    load_notebook_packet,
    load_script_ir,
    upsert_episode_plan,
    upsert_notebook_packet,
    upsert_script_ir,
)
from newsroom.store.models import (
    Chapter,
    EpisodePlan,
    GlossaryTerm,
    NotebookPacket,
    ScriptIR,
    ScriptSegment,
    SourceRef,
    TimelineEvent,
)


def test_episode_plan_round_trips_through_sqlite(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    plan = EpisodePlan(
        id="plan_20260518_test",
        story_cluster_id="story_20260518_test",
        series_id="copilot",
        title_candidates=["A", "B"],
        thumbnail_angles=["before/after"],
        hook="hook text",
        chapter_outline=[
            Chapter(id="plan_20260518_test__intro", title="導入", intent="導入", target_duration_sec=60),
            Chapter(id="plan_20260518_test__facts", title="事実", intent="事実関係", target_duration_sec=150),
        ],
        target_duration_sec=210,
        viewer_utility="判断材料",
        risk_notes=["no critical view"],
        approval_state="draft",
        created_at="2026-05-18T00:00:00+00:00",
    )

    upsert_episode_plan(db_path, plan)
    loaded = load_episode_plan(db_path, plan.id)

    assert loaded is not None
    assert loaded == plan


def test_script_ir_round_trips_through_sqlite(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    plan = EpisodePlan(
        id="plan_20260518_test",
        story_cluster_id="story_20260518_test",
        series_id=None,
        title_candidates=[],
        thumbnail_angles=[],
        hook="hook",
        chapter_outline=[],
        target_duration_sec=600,
        viewer_utility="utility",
        risk_notes=[],
        approval_state="draft",
        created_at="2026-05-18T00:00:00+00:00",
    )
    upsert_episode_plan(db_path, plan)

    script = ScriptIR(
        id="script_test_001",
        episode_plan_id=plan.id,
        format="yukkuri_dialogue",
        segments=[
            ScriptSegment(
                id="seg_1",
                chapter_id="plan_20260518_test__intro",
                speaker="霊夢",
                text="TODO[intro]: 導入",
                source_refs=["article_a"],
                visual_refs=["visual:intro"],
                claim_type="instruction",
                needs_human_review=True,
            ),
            ScriptSegment(
                id="seg_2",
                chapter_id="plan_20260518_test__facts",
                speaker="魔理沙",
                text="TODO[facts]: 事実",
                source_refs=["article_a", "article_b"],
                visual_refs=["visual:facts"],
                claim_type="fact",
                needs_human_review=True,
            ),
        ],
        created_at="2026-05-18T01:00:00+00:00",
    )

    upsert_script_ir(db_path, script)
    loaded = load_script_ir(db_path, script.id)

    assert loaded is not None
    assert loaded == script


def test_notebook_packet_round_trips_through_sqlite(tmp_path):
    db_path = tmp_path / "newsroom.sqlite"
    packet = NotebookPacket(
        id="packet_20260518_test",
        story_cluster_id="story_20260518_test",
        primary_sources=[
            SourceRef(
                article_id="article_primary",
                url="https://example.com/primary",
                title="Primary source",
                source_name="Microsoft Blog",
                source_type="official",
                published_at="2026-05-18T00:00:00+00:00",
                license_hint="public",
            )
        ],
        news_sources=[
            SourceRef(
                article_id="article_news",
                url="https://example.com/news",
                title="News source",
                source_name="News Outlet",
                source_type="news",
                published_at="2026-05-18T01:00:00+00:00",
            )
        ],
        critical_views=[
            SourceRef(
                article_id="article_critical",
                url="https://example.com/critical",
                title="Critical source",
                source_name="NIST",
                source_type="official",
                published_at="2026-05-18T02:00:00+00:00",
            )
        ],
        timeline=[
            TimelineEvent(
                occurred_at="2026-05-18T00:00:00+00:00",
                source_name="Microsoft Blog",
                title="Primary source",
                article_id="article_primary",
                url="https://example.com/primary",
            )
        ],
        glossary=[GlossaryTerm(term="agent", definition="operator-edited definition")],
        questions=["operator-edited question"],
        format_hint="anchor",
        export_dir="data/packets/packet_20260518_test",
        created_at="2026-05-18T03:00:00+00:00",
    )

    upsert_notebook_packet(db_path, packet)
    loaded = load_notebook_packet(db_path, packet.id)

    assert loaded is not None
    assert loaded == packet
