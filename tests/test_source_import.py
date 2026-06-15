from __future__ import annotations

from newsroom.ingest.source_import import (
    parse_opml_sources,
    reader_source_to_feed,
    source_feed_to_config,
)


OPML_SAMPLE = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <body>
    <outline text="Tech">
      <outline text="AI">
        <outline
          text="Example AI"
          xmlUrl="https://example.com/ai.xml"
          htmlUrl="https://example.com/ai"
          iconUrl="https://example.com/icon.png"
          id="feed/ai" />
      </outline>
    </outline>
    <outline text="Business">
      <outline title="Markets" xmlUrl="https://example.com/markets.xml" />
      <outline title="Duplicate AI" xmlUrl="https://example.com/ai.xml" />
    </outline>
  </body>
</opml>
"""


def test_parse_opml_sources_keeps_categories_and_deduplicates():
    sources = parse_opml_sources(OPML_SAMPLE)

    assert [source.feed_url for source in sources] == [
        "https://example.com/ai.xml",
        "https://example.com/markets.xml",
    ]
    assert sources[0].title == "Example AI"
    assert sources[0].html_url == "https://example.com/ai"
    assert sources[0].icon_url == "https://example.com/icon.png"
    assert sources[0].reader_feed_id == "feed/ai"
    assert sources[0].categories == ("Tech", "AI")
    assert sources[1].categories == ("Business",)


def test_reader_source_to_feed_defaults_to_review_disabled():
    source = parse_opml_sources(OPML_SAMPLE)[0]

    feed = reader_source_to_feed(source)
    config = source_feed_to_config(feed)

    assert feed.kind == "rss"
    assert feed.enabled is False
    assert feed.reader == "opml"
    assert feed.reader_categories == ["Tech", "AI"]
    assert feed.tags == ["reader/tech", "reader/ai"]
    assert config["url"] == "https://example.com/ai.xml"
    assert config["reader_feed_id"] == "feed/ai"
