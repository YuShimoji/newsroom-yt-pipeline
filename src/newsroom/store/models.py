from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

VALID_SOURCE_ROLES = {
    "vendor_official",
    "regulator_public",
    "standards_body",
    "independent_analysis",
    "technical_reference",
    "critical_view_candidate",
}


def stable_hash(value: str) -> str:
    return sha256(value.strip().lower().encode("utf-8")).hexdigest()


def validate_source_role(source_role: str | None, owner: str) -> str | None:
    if source_role is None:
        return None
    role = source_role.strip()
    if not role:
        return None
    if role not in VALID_SOURCE_ROLES:
        raise ValueError(
            f"{owner} source_role must be one of {sorted(VALID_SOURCE_ROLES)}"
        )
    return role


@dataclass(frozen=True)
class SourceFeed:
    id: str
    name: str
    kind: str
    url: str | None = None
    inoreader_stream_id: str | None = None
    source_type: str = "unknown"
    source_role: str | None = None
    source_pool_id: str | None = None
    tags: list[str] = field(default_factory=list)
    enabled: bool = True
    fetch_interval_minutes: int = 360
    last_fetched_at: str | None = None
    last_cursor: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SourceFeed":
        feed_id = str(data.get("id") or "").strip()
        name = str(data.get("name") or feed_id).strip()
        kind = str(data.get("kind") or "rss").strip()
        if not feed_id:
            raise ValueError("SourceFeed requires 'id'")
        if not name:
            raise ValueError(f"SourceFeed {feed_id!r} requires 'name'")
        if kind not in {"rss", "inoreader_stream", "manual"}:
            raise ValueError(f"Unsupported source feed kind: {kind}")

        raw_tags = data.get("tags") or []
        if not isinstance(raw_tags, list):
            raise ValueError(f"SourceFeed {feed_id!r} tags must be a list")

        return cls(
            id=feed_id,
            name=name,
            kind=kind,
            url=data.get("url"),
            inoreader_stream_id=data.get("inoreader_stream_id"),
            source_type=str(data.get("source_type") or "unknown"),
            source_role=validate_source_role(data.get("source_role"), f"SourceFeed {feed_id!r}"),
            source_pool_id=(str(data.get("source_pool_id")).strip() or None)
            if data.get("source_pool_id") is not None
            else None,
            tags=[str(tag) for tag in raw_tags],
            enabled=bool(data.get("enabled", True)),
            fetch_interval_minutes=int(data.get("fetch_interval_minutes", 360)),
            last_fetched_at=data.get("last_fetched_at"),
            last_cursor=data.get("last_cursor"),
        )


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    intent: str
    target_duration_sec: int


@dataclass(frozen=True)
class EpisodePlan:
    id: str
    story_cluster_id: str
    series_id: str | None
    title_candidates: list[str]
    thumbnail_angles: list[str]
    hook: str
    chapter_outline: list[Chapter]
    target_duration_sec: int
    viewer_utility: str
    risk_notes: list[str]
    approval_state: str
    created_at: str


@dataclass(frozen=True)
class SourceRef:
    article_id: str
    url: str
    title: str
    source_name: str
    source_type: str
    source_role: str | None = None
    source_pool_id: str | None = None
    published_at: str | None = None
    license_hint: str | None = None


@dataclass(frozen=True)
class TimelineEvent:
    occurred_at: str | None
    source_name: str
    title: str
    article_id: str
    url: str


@dataclass(frozen=True)
class GlossaryTerm:
    term: str
    definition: str | None = None


@dataclass(frozen=True)
class NotebookPacket:
    id: str
    story_cluster_id: str
    primary_sources: list[SourceRef]
    news_sources: list[SourceRef]
    critical_views: list[SourceRef]
    timeline: list[TimelineEvent]
    glossary: list[GlossaryTerm]
    questions: list[str]
    format_hint: str
    export_dir: str
    created_at: str


@dataclass(frozen=True)
class ScriptSegment:
    id: str
    chapter_id: str
    speaker: str
    text: str
    source_refs: list[str] = field(default_factory=list)
    visual_refs: list[str] = field(default_factory=list)
    claim_type: str = "interpretation"
    needs_human_review: bool = True


@dataclass(frozen=True)
class ScriptIR:
    id: str
    episode_plan_id: str
    format: str
    segments: list[ScriptSegment]
    created_at: str


@dataclass(frozen=True)
class VisualUnit:
    id: str
    segment_refs: list[str]
    unit_type: str
    duration_sec: float
    layout_template: str
    source_refs: list[str] = field(default_factory=list)
    asset_refs: list[str] = field(default_factory=list)
    density_score: float = 0.0
    approval_state: str = "auto_ok"


@dataclass(frozen=True)
class VisualIR:
    id: str
    script_id: str
    visual_units: list[VisualUnit]
    created_at: str


@dataclass(frozen=True)
class AssetCandidate:
    asset_id: str
    type: str
    source_url: str | None
    source_title: str | None
    author: str | None
    captured_at: str | None
    intended_use: str
    quote_reason: str | None = None
    display_duration_sec: float | None = None
    crop_ratio: str | None = None
    modification: str = "none"
    attribution_text: str | None = None
    risk_level: str = "medium"
    approval_state: str = "human_required"


@dataclass(frozen=True)
class AssetManifest:
    episode_id: str
    assets: list[AssetCandidate]
    created_at: str


@dataclass(frozen=True)
class QuoteEntry:
    quote_id: str
    source_ref: str
    quote_type: str
    purpose: str
    necessity: str
    quoted_scope: str
    main_subordinate_assessment: str
    distinction_method: str
    attribution: str
    risk_level: str = "medium"
    approval_state: str = "human_required"
    review_level: str = "direct_quote"
    source_role: str = "source"


@dataclass(frozen=True)
class QuoteManifest:
    episode_id: str
    quotes: list[QuoteEntry]
    created_at: str


@dataclass(frozen=True)
class StoryCluster:
    id: str
    title: str
    summary: str | None
    article_ids: list[str]
    primary_sources: list[str]
    related_series: list[str]
    entities: list[str]
    content_farm_overlap: float
    cluster_date: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class TopicScore:
    cluster_id: str
    score_total: float
    components: dict[str, float]
    scored_at: str


@dataclass(frozen=True)
class Article:
    id: str
    url: str
    canonical_url: str | None
    title: str
    source_name: str
    source_url: str | None
    author: str | None
    published_at: str | None
    fetched_at: str
    body_text: str | None = None
    summary: str | None = None
    language: str | None = None
    tags: list[str] = field(default_factory=list)
    source_type: str = "unknown"
    source_role: str | None = None
    source_pool_id: str | None = None
    license_hint: str | None = None
    hash_url: str = ""
    hash_title: str = ""
    hash_body: str | None = None
    fetch_status: str = "fetched"
    fetch_error: str | None = None

    @classmethod
    def create(
        cls,
        *,
        url: str,
        title: str,
        source_name: str,
        fetched_at: str,
        canonical_url: str | None = None,
        source_url: str | None = None,
        author: str | None = None,
        published_at: str | None = None,
        body_text: str | None = None,
        summary: str | None = None,
        language: str | None = None,
        tags: list[str] | None = None,
        source_type: str = "unknown",
        source_role: str | None = None,
        source_pool_id: str | None = None,
        license_hint: str | None = None,
        fetch_status: str = "fetched",
        fetch_error: str | None = None,
    ) -> "Article":
        clean_url = url.strip()
        clean_title = " ".join(title.split())
        if not clean_url:
            raise ValueError("Article requires url")
        if not clean_title:
            raise ValueError("Article requires title")

        canonical = canonical_url.strip() if canonical_url else clean_url
        url_hash = stable_hash(canonical)
        body_hash = stable_hash(body_text) if body_text else None

        return cls(
            id=f"article_{url_hash[:16]}",
            url=clean_url,
            canonical_url=canonical,
            title=clean_title,
            source_name=source_name,
            source_url=source_url,
            author=author,
            published_at=published_at,
            fetched_at=fetched_at,
            body_text=body_text,
            summary=summary,
            language=language,
            tags=tags or [],
            source_type=source_type,
            source_role=validate_source_role(source_role, f"Article {clean_title!r}"),
            source_pool_id=(source_pool_id.strip() or None) if source_pool_id else None,
            license_hint=license_hint,
            hash_url=url_hash,
            hash_title=stable_hash(clean_title),
            hash_body=body_hash,
            fetch_status=fetch_status,
            fetch_error=fetch_error,
        )
