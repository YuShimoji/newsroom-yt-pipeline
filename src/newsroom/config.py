from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from newsroom.store.models import SourceFeed


DEFAULT_SOURCES_CONFIG = Path("configs/sources.yml")


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {config_path}")
    return data


def load_source_feeds(path: str | Path = DEFAULT_SOURCES_CONFIG) -> list[SourceFeed]:
    data = load_yaml_file(path)
    raw_feeds = data.get("feeds", [])
    if raw_feeds is None:
        return []
    if not isinstance(raw_feeds, list):
        raise ValueError("sources.yml field 'feeds' must be a list")

    feeds: list[SourceFeed] = []
    for raw_feed in raw_feeds:
        if not isinstance(raw_feed, dict):
            raise ValueError("Each feed entry must be a mapping")
        feeds.append(SourceFeed.from_mapping(raw_feed))
    return feeds

