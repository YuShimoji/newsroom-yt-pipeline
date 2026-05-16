from __future__ import annotations

from newsroom.config import load_source_feeds


def test_load_source_feeds(tmp_path):
    config = tmp_path / "sources.yml"
    config.write_text(
        """
feeds:
  - id: example
    name: Example Feed
    kind: rss
    url: https://example.com/feed.xml
    source_type: official
    tags:
      - watch/test
    enabled: true
""",
        encoding="utf-8",
    )

    feeds = load_source_feeds(config)

    assert len(feeds) == 1
    assert feeds[0].id == "example"
    assert feeds[0].kind == "rss"
    assert feeds[0].tags == ["watch/test"]

