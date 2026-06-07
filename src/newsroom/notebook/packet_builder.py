from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from newsroom.config import Series
from newsroom.store.models import (
    Article,
    GlossaryTerm,
    NotebookPacket,
    SourceRef,
    StoryCluster,
    TimelineEvent,
)


DEFAULT_PACKET_ROOT = Path("data/packets")
DEFAULT_FORMAT_HINT = "anchor"

_QUESTION_TEMPLATES = (
    "{title} は何が新しいのか?",
    "{title} は誰の利益になり、誰の負担になるのか?",
    "{title} は今後どう変化していくのか?",
    "視聴者が {title} について知っておくべき判断材料は何か?",
    "{title} に対する反対視点や批判視点は何か?",
)


class NotebookPacketBuilder:
    """Assemble a NotebookPacket from a StoryCluster and its articles."""

    def __init__(self, series_index: dict[str, Series] | None = None) -> None:
        self.series_index = series_index or {}

    def build(
        self,
        cluster: StoryCluster,
        articles: list[Article],
        packet_root: Path | str = DEFAULT_PACKET_ROOT,
        critical_articles: list[Article] | None = None,
    ) -> NotebookPacket:
        if not articles:
            raise ValueError(f"Cluster {cluster.id!r} has no articles")

        article_index = {article.id: article for article in articles}
        ordered_ids = [aid for aid in cluster.article_ids if aid in article_index]
        if not ordered_ids:
            raise ValueError(f"Cluster {cluster.id!r} has no resolvable articles")

        primary_sources = _select_sources(
            cluster, article_index, types={"official"}
        )
        news_sources = _select_sources(
            cluster, article_index, types={"news", "commentary"}
        )
        critical_sources = _dedupe_refs(
            _select_sources(
                cluster,
                article_index,
                types={"competitor"},
                exclude_source_roles={"critical_view_candidate"},
            )
            + [_to_source_ref(article) for article in (critical_articles or [])]
        )

        timeline = _build_timeline(cluster, article_index)
        glossary = [GlossaryTerm(term=entity) for entity in cluster.entities]
        questions = _build_questions(cluster.title)
        format_hint = _resolve_format_hint(cluster, self.series_index)

        packet_id = _packet_id(cluster)
        export_dir = str(Path(packet_root) / packet_id)

        return NotebookPacket(
            id=packet_id,
            story_cluster_id=cluster.id,
            primary_sources=primary_sources,
            news_sources=news_sources,
            critical_views=critical_sources,
            timeline=timeline,
            glossary=glossary,
            questions=questions,
            format_hint=format_hint,
            export_dir=export_dir,
            created_at=datetime.now(UTC).isoformat(),
        )


def _packet_id(cluster: StoryCluster) -> str:
    seed = f"{cluster.id}|{cluster.cluster_date}"
    digest = sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"packet_{cluster.cluster_date.replace('-', '')}_{digest}"


def _select_sources(
    cluster: StoryCluster,
    article_index: dict[str, Article],
    types: set[str],
    exclude_source_roles: set[str] | None = None,
) -> list[SourceRef]:
    refs: list[SourceRef] = []
    excluded_roles = exclude_source_roles or set()
    for article_id in cluster.article_ids:
        article = article_index.get(article_id)
        if article is None or article.source_type not in types:
            continue
        if article.source_role in excluded_roles:
            continue
        refs.append(_to_source_ref(article))
    return refs


def _dedupe_refs(refs: list[SourceRef]) -> list[SourceRef]:
    seen: set[str] = set()
    deduped: list[SourceRef] = []
    for ref in refs:
        if ref.article_id in seen:
            continue
        seen.add(ref.article_id)
        deduped.append(ref)
    return deduped


def _to_source_ref(article: Article) -> SourceRef:
    return SourceRef(
        article_id=article.id,
        url=article.url,
        title=article.title,
        source_name=article.source_name,
        source_type=article.source_type,
        source_role=article.source_role,
        source_pool_id=article.source_pool_id,
        published_at=article.published_at,
        license_hint=article.license_hint,
    )


def _build_timeline(
    cluster: StoryCluster, article_index: dict[str, Article]
) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for article_id in cluster.article_ids:
        article = article_index.get(article_id)
        if article is None:
            continue
        events.append(
            TimelineEvent(
                occurred_at=article.published_at,
                source_name=article.source_name,
                title=article.title,
                article_id=article.id,
                url=article.url,
            )
        )
    events.sort(key=lambda event: (event.occurred_at or "", event.source_name))
    return events


def _build_questions(cluster_title: str) -> list[str]:
    base = cluster_title.strip() or "本件"
    return [template.format(title=base) for template in _QUESTION_TEMPLATES]


def _resolve_format_hint(
    cluster: StoryCluster, series_index: dict[str, Series]
) -> str:
    for series_tag in cluster.related_series:
        series_id = series_tag.split("/", 1)[1] if "/" in series_tag else series_tag
        series = series_index.get(series_id)
        if series is not None:
            return series.default_format
    return DEFAULT_FORMAT_HINT
