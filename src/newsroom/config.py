from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from newsroom.store.models import SourceFeed


DEFAULT_SOURCES_CONFIG = Path("configs/sources.yml")
DEFAULT_SERIES_CONFIG = Path("configs/series.yml")
DEFAULT_SPEAKERS_CONFIG = Path("configs/speakers.yml")


@dataclass(frozen=True)
class Series:
    id: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    default_format: str = "anchor"
    strategic_question: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "Series":
        series_id = str(data.get("id") or "").strip()
        if not series_id:
            raise ValueError("Series requires 'id'")
        title = str(data.get("title") or series_id).strip()
        description = str(data.get("description") or "").strip()
        raw_tags = data.get("tags") or []
        if not isinstance(raw_tags, list):
            raise ValueError(f"Series {series_id!r} tags must be a list")
        return cls(
            id=series_id,
            title=title,
            description=description,
            tags=[str(tag) for tag in raw_tags],
            default_format=str(data.get("default_format") or "anchor"),
            strategic_question=(data.get("strategic_question") or None),
        )


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


@dataclass(frozen=True)
class SpeakerProfile:
    id: str
    ymm4_name: str
    role: str


@dataclass(frozen=True)
class SpeakerConfig:
    by_format: dict[str, list[SpeakerProfile]]


def load_speaker_config(path: str | Path = DEFAULT_SPEAKERS_CONFIG) -> SpeakerConfig:
    data = load_yaml_file(path)
    raw_speakers = data.get("speakers")
    if not isinstance(raw_speakers, dict):
        raise ValueError("speakers.yml must define a 'speakers' mapping")

    by_format: dict[str, list[SpeakerProfile]] = {}
    for format_key, entries in raw_speakers.items():
        if not isinstance(entries, list):
            raise ValueError(f"speakers.{format_key} must be a list")
        profiles: list[SpeakerProfile] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"speakers.{format_key} entries must be mappings")
            speaker_id = str(entry.get("id") or "").strip()
            ymm4_name = str(entry.get("ymm4_name") or "").strip()
            role = str(entry.get("role") or "").strip()
            if not speaker_id or not ymm4_name:
                raise ValueError(
                    f"speakers.{format_key} entry requires 'id' and 'ymm4_name'"
                )
            profiles.append(SpeakerProfile(id=speaker_id, ymm4_name=ymm4_name, role=role))
        by_format[str(format_key)] = profiles
    return SpeakerConfig(by_format=by_format)


def load_series(path: str | Path = DEFAULT_SERIES_CONFIG) -> list[Series]:
    data = load_yaml_file(path)
    raw_series = data.get("series", [])
    if raw_series is None:
        return []
    if not isinstance(raw_series, list):
        raise ValueError("series.yml field 'series' must be a list")

    series: list[Series] = []
    for raw_entry in raw_series:
        if not isinstance(raw_entry, dict):
            raise ValueError("Each series entry must be a mapping")
        series.append(Series.from_mapping(raw_entry))
    return series

