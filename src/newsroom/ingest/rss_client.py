from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from newsroom.store.models import Article, SourceFeed


class RssClient:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, feed: SourceFeed) -> list[Article]:
        if not feed.url:
            raise ValueError(f"RSS feed {feed.id!r} has no url")

        request = Request(
            feed.url,
            headers={"User-Agent": "newsroom-yt-pipeline/0.1 (+https://local.invalid)"},
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            xml_bytes = response.read()
        return parse_feed(xml_bytes, feed)


def parse_feed(xml_content: bytes | str, feed: SourceFeed, fetched_at: str | None = None) -> list[Article]:
    fetched = fetched_at or datetime.now(UTC).isoformat()
    root = ElementTree.fromstring(xml_content)
    root_name = _local_name(root.tag)

    if root_name == "rss":
        return _parse_rss(root, feed, fetched)
    if root_name == "feed":
        return _parse_atom(root, feed, fetched)
    raise ValueError(f"Unsupported feed root: {root.tag}")


def _parse_rss(root: ElementTree.Element, feed: SourceFeed, fetched_at: str) -> list[Article]:
    channel = _first_child(root, "channel")
    if channel is None:
        raise ValueError("RSS feed has no channel")

    source_url = _child_text(channel, "link") or feed.url
    articles: list[Article] = []
    for item in _children(channel, "item"):
        title = _child_text(item, "title")
        link = _child_text(item, "link") or _child_text(item, "guid")
        if not title or not link:
            continue
        articles.append(
            Article.create(
                url=link,
                title=title,
                canonical_url=link,
                source_name=feed.name,
                source_url=source_url,
                author=_child_text(item, "author") or _child_text(item, "creator"),
                published_at=_parse_datetime(_child_text(item, "pubDate") or _child_text(item, "date")),
                fetched_at=fetched_at,
                summary=_child_text(item, "description"),
                tags=feed.tags,
                source_type=feed.source_type,
            )
        )
    return articles


def _parse_atom(root: ElementTree.Element, feed: SourceFeed, fetched_at: str) -> list[Article]:
    source_url = _atom_link(root) or feed.url
    articles: list[Article] = []
    for entry in _children(root, "entry"):
        title = _child_text(entry, "title")
        link = _atom_link(entry) or _child_text(entry, "id")
        if not title or not link:
            continue
        articles.append(
            Article.create(
                url=link,
                title=title,
                canonical_url=link,
                source_name=feed.name,
                source_url=source_url,
                author=_atom_author(entry),
                published_at=_parse_datetime(_child_text(entry, "published") or _child_text(entry, "updated")),
                fetched_at=fetched_at,
                summary=_child_text(entry, "summary"),
                tags=feed.tags,
                source_type=feed.source_type,
            )
        )
    return articles


def _parse_datetime(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    value = raw_value.strip()
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.isoformat()
    except (TypeError, ValueError):
        pass

    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.isoformat()
    except ValueError:
        return None


def _atom_link(element: ElementTree.Element) -> str | None:
    fallback: str | None = None
    for child in element:
        if _local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        if not href:
            continue
        rel = child.attrib.get("rel", "alternate")
        if rel == "alternate":
            return href
        fallback = fallback or href
    return fallback


def _atom_author(entry: ElementTree.Element) -> str | None:
    author = _first_child(entry, "author")
    if author is None:
        return None
    return _child_text(author, "name")


def _child_text(element: ElementTree.Element, child_name: str) -> str | None:
    child = _first_child(element, child_name)
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _first_child(element: ElementTree.Element, child_name: str) -> ElementTree.Element | None:
    for child in element:
        if _local_name(child.tag) == child_name:
            return child
    return None


def _children(element: ElementTree.Element, child_name: str) -> list[ElementTree.Element]:
    return [child for child in element if _local_name(child.tag) == child_name]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

