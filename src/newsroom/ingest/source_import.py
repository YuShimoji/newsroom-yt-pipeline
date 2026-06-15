from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from urllib.parse import urlparse
from xml.etree import ElementTree

from newsroom.store.models import SourceFeed


@dataclass(frozen=True)
class ReaderSource:
    feed_url: str
    title: str | None = None
    html_url: str | None = None
    categories: tuple[str, ...] = ()
    reader: str = "opml"
    reader_feed_id: str | None = None
    icon_url: str | None = None


def load_opml_sources(path: str | Path) -> list[ReaderSource]:
    return parse_opml_sources(Path(path).read_bytes())


def parse_opml_sources(xml_bytes: bytes) -> list[ReaderSource]:
    root = ElementTree.fromstring(xml_bytes)
    tag = _local_name(root.tag).lower()
    if tag != "opml":
        raise ValueError(f"Unrecognised OPML format: root element <{root.tag}>")

    sources: list[ReaderSource] = []
    seen_urls: set[str] = set()

    def walk(node: ElementTree.Element, category_stack: tuple[str, ...]) -> None:
        for child in list(node):
            if _local_name(child.tag).lower() != "outline":
                walk(child, category_stack)
                continue

            feed_url = _attr(child, "xmlUrl")
            label = _outline_label(child)
            next_categories = category_stack

            if feed_url:
                feed_url = feed_url.strip()
                if feed_url and feed_url not in seen_urls:
                    seen_urls.add(feed_url)
                    sources.append(
                        ReaderSource(
                            feed_url=feed_url,
                            title=label,
                            html_url=_attr(child, "htmlUrl"),
                            categories=category_stack,
                            reader="opml",
                            reader_feed_id=_attr(child, "id"),
                            icon_url=_attr(child, "iconUrl") or _attr(child, "icon"),
                        )
                    )
            elif label:
                next_categories = (*category_stack, label)

            walk(child, next_categories)

    walk(root, ())
    return sources


def reader_source_to_feed(
    source: ReaderSource,
    *,
    enabled: bool = False,
    source_type: str = "unknown",
) -> SourceFeed:
    return SourceFeed(
        id=stable_feed_id(source.feed_url, source.title),
        name=source.title or _host_label(source.feed_url),
        kind="rss",
        url=source.feed_url,
        source_type=source_type,
        tags=reader_category_tags(source.categories),
        enabled=enabled,
        reader=source.reader,
        reader_feed_id=source.reader_feed_id,
        html_url=source.html_url,
        icon_url=source.icon_url,
        reader_categories=list(source.categories),
    )


def reader_sources_to_feeds(
    sources: list[ReaderSource],
    *,
    enabled: bool = False,
    source_type: str = "unknown",
) -> list[SourceFeed]:
    return [
        reader_source_to_feed(source, enabled=enabled, source_type=source_type)
        for source in sources
    ]


def stable_feed_id(feed_url: str, title: str | None = None) -> str:
    base = _slugify(title or _host_label(feed_url) or "feed")
    digest = sha256(feed_url.strip().lower().encode("utf-8")).hexdigest()[:8]
    return f"{base}_{digest}"


def reader_category_tags(categories: tuple[str, ...] | list[str]) -> list[str]:
    tags: list[str] = []
    for category in categories:
        slug = _slugify(category)
        if slug:
            tags.append(f"reader/{slug}")
    return tags


def source_feed_to_config(feed: SourceFeed) -> dict[str, object]:
    data: dict[str, object] = {
        "id": feed.id,
        "name": feed.name,
        "kind": feed.kind,
        "url": feed.url,
        "source_type": feed.source_type,
        "tags": feed.tags,
        "enabled": feed.enabled,
    }
    optional_values = {
        "source_role": feed.source_role,
        "source_pool_id": feed.source_pool_id,
        "reader": feed.reader,
        "reader_feed_id": feed.reader_feed_id,
        "html_url": feed.html_url,
        "icon_url": feed.icon_url,
        "reader_categories": feed.reader_categories,
    }
    for key, value in optional_values.items():
        if value not in (None, [], ()):
            data[key] = value
    return data


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _attr(node: ElementTree.Element, name: str) -> str | None:
    value = node.attrib.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _outline_label(node: ElementTree.Element) -> str | None:
    return _attr(node, "title") or _attr(node, "text")


def _host_label(feed_url: str) -> str:
    host = urlparse(feed_url).netloc
    return host or "feed"


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value[:48] or "feed"
