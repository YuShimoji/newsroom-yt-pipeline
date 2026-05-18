from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256

from newsroom.config import Series
from newsroom.store.models import Chapter, EpisodePlan, NotebookPacket, StoryCluster


CHAPTER_TEMPLATES: tuple[tuple[str, str, int], ...] = (
    ("intro", "導入と論点提示", "事象を一言で要約し、なぜ視聴者に関係するかを示す", 60),
    ("facts", "事実関係", "確定している事実と一次情報を時系列に整理する", 150),
    ("context", "背景と前史", "なぜこの事象が起きたか、過去の関連事例と比較する", 120),
    ("conflict", "対立視点・批判視点", "賛否や利害の異なる視点を最低 2 つ提示する", 120),
    ("impact", "視聴者にとっての影響", "視聴者の判断・行動・選択に何が変わるかを述べる", 90),
    ("takeaway", "まとめと次の注目点", "本回の結論と、次回以降に追うべき差分を示す", 60),
)


class EpisodePlanner:
    """Build an EpisodePlan skeleton from a packet and its cluster."""

    def plan(
        self,
        cluster: StoryCluster,
        packet: NotebookPacket,
        series: Series | None = None,
    ) -> EpisodePlan:
        now = datetime.now(UTC).isoformat()
        plan_id = _plan_id(cluster)

        viewer_utility = (
            series.strategic_question
            if series and series.strategic_question
            else "視聴者が本件をどう判断するかの材料を提示する"
        )

        risk_notes: list[str] = []
        if cluster.content_farm_overlap >= 0.5:
            risk_notes.append("competitor sources dominate; raise differentiation effort")
        if not packet.primary_sources:
            risk_notes.append("no primary source in packet; verify before fact framing")
        if not packet.critical_views:
            risk_notes.append("packet contains no critical view; add one manually")

        chapters = [
            _build_chapter(plan_id, key, title, intent, duration)
            for key, title, intent, duration in CHAPTER_TEMPLATES
        ]
        target_duration_sec = sum(chapter.target_duration_sec for chapter in chapters)

        title_candidates = _title_candidates(cluster.title)
        thumbnail_angles = _thumbnail_angles(cluster.title)
        hook = f"今回扱うのは「{cluster.title}」です。何が変わったのか、誰の利益になるのか、視聴者の判断に何が必要かを順に見ていきます。"

        return EpisodePlan(
            id=plan_id,
            story_cluster_id=cluster.id,
            series_id=series.id if series else None,
            title_candidates=title_candidates,
            thumbnail_angles=thumbnail_angles,
            hook=hook,
            chapter_outline=chapters,
            target_duration_sec=target_duration_sec,
            viewer_utility=viewer_utility,
            risk_notes=risk_notes,
            approval_state="draft",
            created_at=now,
        )


def _plan_id(cluster: StoryCluster) -> str:
    digest = sha256(cluster.id.encode("utf-8")).hexdigest()[:12]
    return f"plan_{cluster.cluster_date.replace('-', '')}_{digest}"


def _build_chapter(plan_id: str, key: str, title: str, intent: str, duration: int) -> Chapter:
    chapter_id = f"{plan_id}__{key}"
    return Chapter(id=chapter_id, title=title, intent=intent, target_duration_sec=duration)


def _title_candidates(cluster_title: str) -> list[str]:
    return [
        f"{cluster_title} で何が起きているのか",
        f"{cluster_title} を 5 つの視点で読み解く",
        f"{cluster_title} のリスクと機会",
    ]


def _thumbnail_angles(cluster_title: str) -> list[str]:
    return [
        f"{cluster_title} を象徴するキーワードを 1 つ強調",
        f"{cluster_title} の前後比較を矢印で示す",
    ]
