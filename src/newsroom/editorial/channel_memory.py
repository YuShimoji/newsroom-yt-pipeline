from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from newsroom.store.models import validate_source_role


FORBIDDEN_MEMORY_KEYS = {
    "article_body",
    "approved_text",
    "body_text",
    "private_data",
    "raw_article_body",
    "runtime_db_path",
    "screenshot_path",
    "subtitle_coordinates",
    "ymmp",
    "ymm4_geometry",
}


class ChannelMemoryValidationError(ValueError):
    """Raised when a tracked channel memory record is not safe to use."""


@dataclass(frozen=True)
class MemorySourceRole:
    source_role: str | None
    source_pool_id: str | None
    source_type: str
    source_count: int
    article_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MemoryCriticalView:
    article_id: str
    source_name: str
    source_type: str
    source_role: str | None = None
    source_pool_id: str | None = None
    title: str | None = None
    purpose: str | None = None


@dataclass(frozen=True)
class MemoryClaim:
    claim_id: str
    summary: str
    source_refs: list[str] = field(default_factory=list)
    critical_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FollowupCandidate:
    candidate_id: str
    title: str
    rationale: str
    source_roles_needed: list[str] = field(default_factory=list)
    status: str = "seed"


@dataclass(frozen=True)
class EpisodeMemory:
    episode_id: str
    story_id: str
    script_id: str
    packet_id: str
    topic: str
    status: str
    source_roles_used: list[MemorySourceRole] = field(default_factory=list)
    critical_views_used: list[MemoryCriticalView] = field(default_factory=list)
    claims_made: list[MemoryClaim] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    followup_candidates: list[FollowupCandidate] = field(default_factory=list)


@dataclass(frozen=True)
class ChannelMemory:
    series_id: str
    title: str
    status: str
    episodes: list[EpisodeMemory] = field(default_factory=list)


def load_channel_memory(path: str | Path) -> ChannelMemory:
    memory_path = Path(path)
    with memory_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("channel memory root must be a mapping")
    validate_channel_memory_payload(payload)
    return _memory_from_payload(payload)


def validate_channel_memory_payload(payload: dict[str, Any]) -> None:
    _reject_forbidden_keys(payload)
    _require(payload, "artifact_type", "channel_memory")
    _require(payload, "schema_version", 1)
    for key in ("series_id", "title", "status"):
        _require_string(payload, key)

    episodes = payload.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        raise ChannelMemoryValidationError("channel memory requires at least one episode")
    for episode in episodes:
        _validate_episode(episode)


def _validate_episode(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("episode entries must be mappings")
    for key in ("episode_id", "story_id", "script_id", "packet_id", "topic", "status"):
        _require_string(payload, key)

    for role in payload.get("source_roles_used", []):
        _validate_source_role_row(role)
    for critical in payload.get("critical_views_used", []):
        _validate_critical_view(critical)
    for claim in payload.get("claims_made", []):
        _validate_claim(claim)
    for question in payload.get("open_questions", []):
        if not isinstance(question, str) or not question.strip():
            raise ChannelMemoryValidationError("open_questions entries must be strings")
    for candidate in payload.get("followup_candidates", []):
        _validate_followup(candidate)


def _validate_source_role_row(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("source_roles_used entries must be mappings")
    source_role = payload.get("source_role")
    validate_source_role(source_role, "ChannelMemory source_roles_used")
    _require_string(payload, "source_type")
    if not isinstance(payload.get("source_count"), int) or payload["source_count"] < 0:
        raise ChannelMemoryValidationError("source_count must be a non-negative integer")
    article_ids = payload.get("article_ids", [])
    if not isinstance(article_ids, list) or not all(isinstance(item, str) for item in article_ids):
        raise ChannelMemoryValidationError("article_ids must be a list of strings")


def _validate_critical_view(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("critical_views_used entries must be mappings")
    for key in ("article_id", "source_name", "source_type"):
        _require_string(payload, key)
    validate_source_role(payload.get("source_role"), "ChannelMemory critical_views_used")


def _validate_claim(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("claims_made entries must be mappings")
    for key in ("claim_id", "summary"):
        _require_string(payload, key)
    for key in ("source_refs", "critical_refs"):
        refs = payload.get(key, [])
        if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
            raise ChannelMemoryValidationError(f"{key} must be a list of strings")


def _validate_followup(payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("followup_candidates entries must be mappings")
    for key in ("candidate_id", "title", "rationale", "status"):
        _require_string(payload, key)
    roles = payload.get("source_roles_needed", [])
    if not isinstance(roles, list):
        raise ChannelMemoryValidationError("source_roles_needed must be a list")
    for role in roles:
        validate_source_role(role, "ChannelMemory source_roles_needed")


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key) in FORBIDDEN_MEMORY_KEYS:
                raise ChannelMemoryValidationError(
                    f"channel memory must not contain {key!r}"
                )
            _reject_forbidden_keys(child)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden_keys(item)


def _require(payload: dict[str, Any], key: str, expected: Any) -> None:
    if payload.get(key) != expected:
        raise ChannelMemoryValidationError(f"{key} must be {expected!r}")


def _require_string(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), str) or not payload[key].strip():
        raise ChannelMemoryValidationError(f"{key} must be a non-empty string")


def _memory_from_payload(payload: dict[str, Any]) -> ChannelMemory:
    return ChannelMemory(
        series_id=payload["series_id"],
        title=payload["title"],
        status=payload["status"],
        episodes=[_episode_from_payload(row) for row in payload["episodes"]],
    )


def _episode_from_payload(payload: dict[str, Any]) -> EpisodeMemory:
    return EpisodeMemory(
        episode_id=payload["episode_id"],
        story_id=payload["story_id"],
        script_id=payload["script_id"],
        packet_id=payload["packet_id"],
        topic=payload["topic"],
        status=payload["status"],
        source_roles_used=[
            MemorySourceRole(
                source_role=row.get("source_role"),
                source_pool_id=row.get("source_pool_id"),
                source_type=row["source_type"],
                source_count=row["source_count"],
                article_ids=list(row.get("article_ids", [])),
            )
            for row in payload.get("source_roles_used", [])
        ],
        critical_views_used=[
            MemoryCriticalView(
                article_id=row["article_id"],
                source_name=row["source_name"],
                source_type=row["source_type"],
                source_role=row.get("source_role"),
                source_pool_id=row.get("source_pool_id"),
                title=row.get("title"),
                purpose=row.get("purpose"),
            )
            for row in payload.get("critical_views_used", [])
        ],
        claims_made=[
            MemoryClaim(
                claim_id=row["claim_id"],
                summary=row["summary"],
                source_refs=list(row.get("source_refs", [])),
                critical_refs=list(row.get("critical_refs", [])),
            )
            for row in payload.get("claims_made", [])
        ],
        open_questions=list(payload.get("open_questions", [])),
        followup_candidates=[
            FollowupCandidate(
                candidate_id=row["candidate_id"],
                title=row["title"],
                rationale=row["rationale"],
                source_roles_needed=list(row.get("source_roles_needed", [])),
                status=row["status"],
            )
            for row in payload.get("followup_candidates", [])
        ],
    )
