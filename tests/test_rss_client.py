from __future__ import annotations

from newsroom.ingest.rss_client import parse_feed
from newsroom.store.models import SourceFeed


def test_parse_rss_feed_normalizes_article():
    feed = SourceFeed(
        id="test",
        name="Test Source",
        kind="rss",
        url="https://example.com/feed.xml",
        source_type="official",
        tags=["watch/test"],
    )
    xml = """
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com/</link>
    <item>
      <title>  Example   Article  </title>
      <link>https://example.com/a</link>
      <pubDate>Sat, 16 May 2026 01:02:03 GMT</pubDate>
      <description>Summary text</description>
    </item>
  </channel>
</rss>
"""

    articles = parse_feed(xml, feed, fetched_at="2026-05-16T10:00:00+00:00")

    assert len(articles) == 1
    article = articles[0]
    assert article.title == "Example Article"
    assert article.url == "https://example.com/a"
    assert article.source_name == "Test Source"
    assert article.published_at == "2026-05-16T01:02:03+00:00"
    assert article.tags == ["watch/test"]


def test_parse_atom_feed_without_published_date():
    feed = SourceFeed(id="atom", name="Atom Source", kind="rss")
    xml = """
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Feed</title>
  <entry>
    <title>Atom Article</title>
    <link href="https://example.com/atom-a" />
  </entry>
</feed>
"""

    articles = parse_feed(xml, feed, fetched_at="2026-05-16T10:00:00+00:00")

    assert len(articles) == 1
    assert articles[0].published_at is None
    assert articles[0].url == "https://example.com/atom-a"

