from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from newsroom.config import load_yaml_file
from newsroom.ingest.source_import import stable_feed_id, reader_category_tags
from newsroom.store.models import Article, SourceFeed


@dataclass(frozen=True)
class InoreaderStream:
    id: str
    stream_id: str
    tags: list[str]


@dataclass(frozen=True)
class InoreaderClient:
    enabled: bool
    client_id_env: str | None = None
    client_secret_env: str | None = None
    token_store: str | None = None
    access_token_env: str = "NEWSROOM_INOREADER_ACCESS_TOKEN"
    streams: tuple[InoreaderStream, ...] = ()
    base_url: str = "https://www.inoreader.com"

    @classmethod
    def from_config_path(cls, config_path: str | Path) -> "InoreaderClient":
        data = load_yaml_file(config_path)
        raw_config = data.get("inoreader") or {}
        if not isinstance(raw_config, dict):
            raise ValueError("sources.yml field 'inoreader' must be a mapping")
        return cls(
            enabled=bool(raw_config.get("enabled", False)),
            client_id_env=raw_config.get("client_id_env"),
            client_secret_env=raw_config.get("client_secret_env"),
            token_store=raw_config.get("token_store"),
            access_token_env=str(
                raw_config.get("access_token_env") or "NEWSROOM_INOREADER_ACCESS_TOKEN"
            ),
            streams=tuple(_parse_streams(raw_config.get("streams") or [])),
        )

    def describe_stub(self) -> str:
        return (
            "Inoreader OAuth/token storage is deferred. "
            f"Read-only fetch is available when {self.access_token_env} is set."
        )

    def load_subscription_sources(self, access_token: str | None = None) -> list[SourceFeed]:
        payload = self._get_json(
            "/reader/api/0/subscription/list",
            access_token=self._require_access_token(access_token),
        )
        return parse_inoreader_subscriptions(payload)

    def fetch_stream(
        self,
        stream_id: str,
        *,
        access_token: str | None = None,
        sources: list[SourceFeed] | None = None,
        limit: int = 20,
        fetched_at: str | None = None,
    ) -> list[Article]:
        payload = self._get_json(
            f"/reader/api/0/stream/contents/{quote(stream_id, safe='')}",
            access_token=self._require_access_token(access_token),
            params={"n": str(limit)},
        )
        return parse_inoreader_stream(payload, sources=sources, fetched_at=fetched_at)

    def fetch_configured_streams(
        self,
        *,
        access_token: str | None = None,
        limit: int = 20,
        fetched_at: str | None = None,
    ) -> list[Article]:
        sources = self.load_subscription_sources(access_token=access_token)
        articles: list[Article] = []
        for stream in self.streams or (InoreaderStream("reading_list", "user/-/state/com.google/reading-list", []),):
            stream_articles = self.fetch_stream(
                stream.stream_id,
                access_token=access_token,
                sources=sources,
                limit=limit,
                fetched_at=fetched_at,
            )
            if stream.tags:
                stream_articles = [
                    _article_with_tags(article, stream.tags) for article in stream_articles
                ]
            articles.extend(stream_articles)
        return articles

    def _get_json(
        self,
        path: str,
        *,
        access_token: str,
        params: dict[str, str] | None = None,
    ) -> dict:
        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            f"{self.base_url}{path}{query}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "newsroom-yt-pipeline/0.1 (+https://local.invalid)",
            },
        )
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Inoreader response must be a JSON object")
        return data

    def _require_access_token(self, access_token: str | None) -> str:
        token = access_token or os.environ.get(self.access_token_env)
        if not token:
            raise ValueError(f"Missing Inoreader token. Set {self.access_token_env}.")
        return token


def parse_inoreader_subscriptions(payload: dict) -> list[SourceFeed]:
    subscriptions = payload.get("subscriptions", [])
    if not isinstance(subscriptions, list):
        raise ValueError("Inoreader subscription/list response must contain subscriptions[]")

    feeds: list[SourceFeed] = []
    for subscription in subscriptions:
        if not isinstance(subscription, dict):
            continue
        feed_url = _string_or_none(subscription.get("url"))
        if not feed_url:
            continue
        title = _string_or_none(subscription.get("title"))
        categories = _category_labels(subscription.get("categories"))
        feeds.append(
            SourceFeed(
                id=stable_feed_id(feed_url, title),
                name=title or feed_url,
                kind="rss",
                url=feed_url,
                tags=reader_category_tags(categories),
                reader="inoreader",
                reader_feed_id=_string_or_none(subscription.get("id")),
                html_url=_string_or_none(subscription.get("htmlUrl")),
                icon_url=_string_or_none(subscription.get("iconUrl")),
                reader_categories=list(categories),
            )
        )
    return feeds


def parse_inoreader_stream(
    payload: dict,
    *,
    sources: list[SourceFeed] | None = None,
    fetched_at: str | None = None,
) -> list[Article]:
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError("Inoreader stream/contents response must contain items[]")

    source_by_id, source_by_url = _source_indexes(sources or [])
    fetched = fetched_at or datetime.now(UTC).isoformat()
    articles: list[Article] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = _string_or_none(item.get("title"))
        if not title:
            continue
        origin = item.get("origin") if isinstance(item.get("origin"), dict) else {}
        stream_id = _string_or_none(origin.get("streamId"))
        origin_feed_url = _feed_url_from_stream_id(stream_id)
        source = source_by_id.get(stream_id or "") or source_by_url.get(origin_feed_url or "")
        url = _href_from_links(item.get("canonical")) or _href_from_links(item.get("alternate"))
        if not url:
            continue

        articles.append(
            Article.create(
                url=url,
                title=title,
                canonical_url=url,
                source_name=source.name if source else (_string_or_none(origin.get("title")) or "Inoreader"),
                source_url=source.url if source else origin_feed_url,
                published_at=_published_datetime(item),
                fetched_at=fetched,
                summary=_summary_content(item.get("summary")),
                tags=source.tags if source else [],
                source_type=source.source_type if source else "unknown",
                source_role=source.source_role if source else None,
                source_pool_id=source.source_pool_id if source else None,
            )
        )
    return articles


def _parse_streams(raw_streams: object) -> list[InoreaderStream]:
    if not isinstance(raw_streams, list):
        raise ValueError("sources.yml field 'inoreader.streams' must be a list")
    streams: list[InoreaderStream] = []
    for raw_stream in raw_streams:
        if not isinstance(raw_stream, dict):
            raise ValueError("Each inoreader.streams entry must be a mapping")
        stream_id = str(raw_stream.get("stream_id") or "").strip()
        if not stream_id:
            raise ValueError("Each inoreader.streams entry requires stream_id")
        raw_tags = raw_stream.get("tags") or []
        if not isinstance(raw_tags, list):
            raise ValueError("inoreader.streams tags must be a list")
        streams.append(
            InoreaderStream(
                id=str(raw_stream.get("id") or "stream").strip(),
                stream_id=stream_id,
                tags=[str(tag) for tag in raw_tags],
            )
        )
    return streams


def _source_indexes(sources: list[SourceFeed]) -> tuple[dict[str, SourceFeed], dict[str, SourceFeed]]:
    by_id = {source.reader_feed_id: source for source in sources if source.reader_feed_id}
    by_url = {source.url: source for source in sources if source.url}
    return by_id, by_url


def _article_with_tags(article: Article, tags: list[str]) -> Article:
    merged_tags = list(article.tags)
    for tag in tags:
        if tag not in merged_tags:
            merged_tags.append(tag)
    return Article.create(
        url=article.url,
        title=article.title,
        source_name=article.source_name,
        fetched_at=article.fetched_at,
        canonical_url=article.canonical_url,
        source_url=article.source_url,
        author=article.author,
        published_at=article.published_at,
        body_text=article.body_text,
        summary=article.summary,
        language=article.language,
        tags=merged_tags,
        source_type=article.source_type,
        source_role=article.source_role,
        source_pool_id=article.source_pool_id,
        license_hint=article.license_hint,
        fetch_status=article.fetch_status,
        fetch_error=article.fetch_error,
    )


def _category_labels(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, list):
        return ()
    labels: list[str] = []
    for category in raw:
        if not isinstance(category, dict):
            continue
        label = _string_or_none(category.get("label"))
        if label:
            labels.append(label)
    return tuple(labels)


def _href_from_links(raw: object) -> str | None:
    if not isinstance(raw, list):
        return None
    for link in raw:
        if not isinstance(link, dict):
            continue
        href = _string_or_none(link.get("href"))
        if href:
            return href
    return None


def _summary_content(raw: object) -> str | None:
    if not isinstance(raw, dict):
        return None
    return _string_or_none(raw.get("content"))


def _published_datetime(item: dict) -> str | None:
    for key, divisor in (("published", 1), ("crawlTimeMsec", 1000), ("timestampUsec", 1_000_000)):
        value = item.get(key)
        if not isinstance(value, (int, float)):
            continue
        try:
            return datetime.fromtimestamp(value / divisor, tz=UTC).isoformat()
        except (OSError, OverflowError, ValueError):
            continue
    return None


def _feed_url_from_stream_id(stream_id: str | None) -> str | None:
    if stream_id and stream_id.startswith("feed/"):
        return stream_id.removeprefix("feed/")
    return None


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
