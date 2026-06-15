from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from newsroom.config import load_source_feeds, load_source_pools


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


def test_load_source_pools_validates_roles(tmp_path):
    config = tmp_path / "source_pools.yml"
    config.write_text(
        """
pools:
  - id: vendor_pool
    label: Vendor Pool
    source_role: vendor_official
    source_type: official
    tags:
      - pool/vendor
""",
        encoding="utf-8",
    )

    pools = load_source_pools(config)

    assert len(pools) == 1
    assert pools[0].id == "vendor_pool"
    assert pools[0].source_role == "vendor_official"


def test_source_pool_defaults_are_applied_to_feeds(tmp_path):
    pools_config = tmp_path / "source_pools.yml"
    pools_config.write_text(
        """
pools:
  - id: standards
    label: Standards Pool
    source_role: standards_body
    source_type: official
    tags:
      - pool/standards
""",
        encoding="utf-8",
    )
    feeds_config = tmp_path / "sources.yml"
    feeds_config.write_text(
        """
feeds:
  - id: nist
    name: NIST
    kind: rss
    url: https://example.com/nist.xml
    source_pool_id: standards
    tags:
      - watch/ai-risk
""",
        encoding="utf-8",
    )

    feeds = load_source_feeds(feeds_config, source_pools_path=pools_config)

    assert feeds[0].source_pool_id == "standards"
    assert feeds[0].source_role == "standards_body"
    assert feeds[0].source_type == "official"
    assert feeds[0].tags == ["pool/standards", "watch/ai-risk"]


def test_load_source_feeds_preserves_reader_metadata(tmp_path):
    config = tmp_path / "sources.yml"
    config.write_text(
        """
feeds:
  - id: reader_feed
    name: Reader Feed
    kind: rss
    url: https://example.com/feed.xml
    reader: opml
    reader_feed_id: feed/example
    html_url: https://example.com/
    icon_url: https://example.com/icon.png
    reader_categories:
      - Tech
    tags:
      - reader/tech
""",
        encoding="utf-8",
    )

    feeds = load_source_feeds(config)

    assert feeds[0].reader == "opml"
    assert feeds[0].reader_feed_id == "feed/example"
    assert feeds[0].html_url == "https://example.com/"
    assert feeds[0].icon_url == "https://example.com/icon.png"
    assert feeds[0].reader_categories == ["Tech"]


def test_unknown_source_role_rejects(tmp_path):
    config = tmp_path / "source_pools.yml"
    config.write_text(
        """
pools:
  - id: bad
    label: Bad Pool
    source_role: broad_crawl
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="source_role"):
        load_source_pools(config)


def test_default_source_pool_registry_stores_metadata_only():
    pools = load_source_pools()
    feeds = load_source_feeds()

    assert {pool.source_role for pool in pools} >= {
        "vendor_official",
        "regulator_public",
        "standards_body",
        "independent_analysis",
        "technical_reference",
        "critical_view_candidate",
    }
    raw = yaml.safe_load(Path("configs/source_pools.yml").read_text(encoding="utf-8"))
    serialized = repr(raw)
    assert "body_text" not in serialized
    assert "raw_article" not in serialized
    assert "screenshot" not in serialized
    microsoft = next(feed for feed in feeds if feed.id == "microsoft_blog")
    assert microsoft.source_role == "vendor_official"
    competitor = next(feed for feed in feeds if feed.id == "competitor_example")
    assert competitor.source_role == "critical_view_candidate"
