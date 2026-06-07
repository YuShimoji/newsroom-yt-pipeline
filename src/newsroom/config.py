from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from newsroom.store.models import SourceFeed, validate_source_role


DEFAULT_SOURCES_CONFIG = Path("configs/sources.yml")
DEFAULT_SOURCE_POOLS_CONFIG = Path("configs/source_pools.yml")
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


@dataclass(frozen=True)
class SourcePool:
    id: str
    label: str
    source_role: str
    source_type: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    manual_approval_required: bool = True
    enabled: bool = True

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "SourcePool":
        pool_id = str(data.get("id") or "").strip()
        if not pool_id:
            raise ValueError("SourcePool requires 'id'")
        label = str(data.get("label") or pool_id).strip()
        role = validate_source_role(data.get("source_role"), f"SourcePool {pool_id!r}")
        if role is None:
            raise ValueError(f"SourcePool {pool_id!r} requires 'source_role'")
        raw_tags = data.get("tags") or []
        if not isinstance(raw_tags, list):
            raise ValueError(f"SourcePool {pool_id!r} tags must be a list")
        return cls(
            id=pool_id,
            label=label,
            source_role=role,
            source_type=(str(data.get("source_type")).strip() or None)
            if data.get("source_type") is not None
            else None,
            description=(str(data.get("description")).strip() or None)
            if data.get("description") is not None
            else None,
            tags=[str(tag) for tag in raw_tags],
            manual_approval_required=bool(data.get("manual_approval_required", True)),
            enabled=bool(data.get("enabled", True)),
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


def load_source_pools(
    path: str | Path = DEFAULT_SOURCE_POOLS_CONFIG,
) -> list[SourcePool]:
    data = load_yaml_file(path)
    declared_roles = data.get("roles", [])
    if declared_roles is not None:
        if not isinstance(declared_roles, list):
            raise ValueError("source_pools.yml field 'roles' must be a list")
        for raw_role in declared_roles:
            role = raw_role.get("id") if isinstance(raw_role, dict) else raw_role
            validate_source_role(str(role), "source_pools.yml roles")

    raw_pools = data.get("pools", [])
    if raw_pools is None:
        return []
    if not isinstance(raw_pools, list):
        raise ValueError("source_pools.yml field 'pools' must be a list")

    pools: list[SourcePool] = []
    for raw_pool in raw_pools:
        if not isinstance(raw_pool, dict):
            raise ValueError("Each source pool entry must be a mapping")
        pools.append(SourcePool.from_mapping(raw_pool))
    return pools


def load_source_feeds(
    path: str | Path = DEFAULT_SOURCES_CONFIG,
    source_pools_path: str | Path | None = DEFAULT_SOURCE_POOLS_CONFIG,
) -> list[SourceFeed]:
    data = load_yaml_file(path)
    raw_feeds = data.get("feeds", [])
    if raw_feeds is None:
        return []
    if not isinstance(raw_feeds, list):
        raise ValueError("sources.yml field 'feeds' must be a list")

    pools_by_id: dict[str, SourcePool] = {}
    if source_pools_path is not None and Path(source_pools_path).exists():
        pools_by_id = {pool.id: pool for pool in load_source_pools(source_pools_path)}

    feeds: list[SourceFeed] = []
    for raw_feed in raw_feeds:
        if not isinstance(raw_feed, dict):
            raise ValueError("Each feed entry must be a mapping")
        feeds.append(SourceFeed.from_mapping(_apply_source_pool(raw_feed, pools_by_id)))
    return feeds


def _apply_source_pool(
    raw_feed: dict[str, Any], pools_by_id: dict[str, SourcePool]
) -> dict[str, Any]:
    pool_id = str(raw_feed.get("source_pool_id") or raw_feed.get("pool_id") or "").strip()
    if not pool_id:
        return raw_feed
    pool = pools_by_id.get(pool_id)
    if pool is None:
        raise ValueError(f"Unknown source_pool_id: {pool_id}")

    merged = dict(raw_feed)
    merged["source_pool_id"] = pool_id
    merged.setdefault("source_role", pool.source_role)
    if pool.source_type is not None:
        merged.setdefault("source_type", pool.source_type)
    merged["tags"] = _merge_tags(pool.tags, raw_feed.get("tags") or [])
    return merged


def _merge_tags(pool_tags: list[str], feed_tags: Any) -> list[str]:
    if not isinstance(feed_tags, list):
        raise ValueError("SourceFeed tags must be a list")
    tags: list[str] = []
    for tag in [*pool_tags, *[str(tag) for tag in feed_tags]]:
        if tag not in tags:
            tags.append(tag)
    return tags


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
