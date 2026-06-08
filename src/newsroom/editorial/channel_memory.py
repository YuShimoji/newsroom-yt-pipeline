from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from newsroom.store.models import validate_source_role


DEFAULT_CHANNEL_MEMORY_ROOT = Path("docs/channel_memory")

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

EPISODE_RECORD_OPTIONAL_KEYS = {
    "claims_made",
    "critical_views_used",
    "followup_candidates",
    "open_questions",
    "source_roles_used",
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


def render_channel_memory_report(memory: ChannelMemory) -> str:
    lines = [
        f"Series: {memory.title} ({memory.series_id})",
        f"Status: {memory.status}",
        f"Episodes: {len(memory.episodes)}",
        "",
        "Important: follow-up seeds are not approved stories.",
        "They require normal editorial selection and source approval before use.",
    ]
    for episode in memory.episodes:
        lines.extend(
            [
                "",
                f"## Episode {episode.episode_id}",
                f"- Status: {episode.status}",
                f"- Story: {episode.story_id}",
                f"- Script: {episode.script_id}",
                f"- Packet: {episode.packet_id}",
                f"- Topic: {episode.topic}",
                "",
                "Source-role coverage:",
            ]
        )
        if episode.source_roles_used:
            for role in episode.source_roles_used:
                role_label = role.source_role or "unclassified"
                pool_label = role.source_pool_id or "no_pool"
                article_ids = ", ".join(role.article_ids) if role.article_ids else "none"
                lines.append(
                    f"- {role_label} / {pool_label} / {role.source_type}: "
                    f"{role.source_count} source(s) [{article_ids}]"
                )
        else:
            lines.append("- none recorded")

        lines.append("")
        lines.append("Critical views:")
        if episode.critical_views_used:
            for critical in episode.critical_views_used:
                title = f" - {critical.title}" if critical.title else ""
                purpose = f" ({critical.purpose})" if critical.purpose else ""
                role_label = critical.source_role or "unclassified"
                lines.append(
                    f"- {critical.source_name}: {critical.article_id} "
                    f"[{critical.source_type}, {role_label}]{title}{purpose}"
                )
        else:
            lines.append("- none recorded")

        lines.append("")
        lines.append("Compact claims:")
        if episode.claims_made:
            for claim in episode.claims_made:
                source_refs = ", ".join(claim.source_refs) or "none"
                critical_refs = ", ".join(claim.critical_refs) or "none"
                lines.append(
                    f"- {claim.claim_id}: {claim.summary} "
                    f"(sources: {source_refs}; critical: {critical_refs})"
                )
        else:
            lines.append("- none recorded")

        lines.append("")
        lines.append("Open questions:")
        if episode.open_questions:
            lines.extend(f"- {question}" for question in episode.open_questions)
        else:
            lines.append("- none recorded")

        lines.append("")
        lines.append("Follow-up seeds:")
        if episode.followup_candidates:
            for candidate in episode.followup_candidates:
                roles = ", ".join(candidate.source_roles_needed) or "none"
                lines.append(
                    f"- [{candidate.status}] {candidate.candidate_id}: "
                    f"{candidate.title} (needed roles: {roles})"
                )
                lines.append(f"  Rationale: {candidate.rationale}")
        else:
            lines.append("- none recorded")

    return "\n".join(lines)


def load_channel_memory(path: str | Path) -> ChannelMemory:
    memory_path = Path(path)
    payload = _load_yaml_mapping(memory_path, "channel memory root")
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError("channel memory root must be a mapping")
    validate_channel_memory_payload(payload)
    return _memory_from_payload(payload)


def append_episode_record(
    memory_path: str | Path,
    episode_record_path: str | Path,
) -> ChannelMemory:
    memory_file = Path(memory_path)
    memory_payload = _load_yaml_mapping(memory_file, "channel memory root")
    validate_channel_memory_payload(memory_payload)

    episode_payload = load_episode_record_payload(episode_record_path)
    _reject_duplicate_episode_ids(memory_payload["episodes"], episode_payload)

    memory_payload["episodes"].append(episode_payload)
    validate_channel_memory_payload(memory_payload)
    with memory_file.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(
            memory_payload,
            handle,
            allow_unicode=True,
            sort_keys=False,
        )
    return _memory_from_payload(memory_payload)


def load_episode_record_payload(path: str | Path) -> dict[str, Any]:
    payload = _load_yaml_mapping(Path(path), "episode record")
    if payload.get("artifact_type") is not None:
        _require(payload, "artifact_type", "channel_memory_episode")
        _require(payload, "schema_version", 1)
        payload = {
            key: value
            for key, value in payload.items()
            if key not in {"artifact_type", "schema_version"}
        }
    _validate_episode_record_payload(payload)
    return payload


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
    _reject_duplicate_episode_ids(episodes)


def _validate_episode_record_payload(payload: dict[str, Any]) -> None:
    _reject_forbidden_keys(payload)
    allowed_keys = {
        "episode_id",
        "story_id",
        "script_id",
        "packet_id",
        "topic",
        "status",
        *EPISODE_RECORD_OPTIONAL_KEYS,
    }
    unknown_keys = sorted(str(key) for key in payload.keys() if key not in allowed_keys)
    if unknown_keys:
        raise ChannelMemoryValidationError(
            f"episode record contains unsupported keys: {', '.join(unknown_keys)}"
        )
    _validate_episode(payload)


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
    if payload["status"] != "seed":
        raise ChannelMemoryValidationError("followup_candidates status must be 'seed'")
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


def _load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ChannelMemoryValidationError(f"{label} must be a mapping")
    return payload


def _reject_duplicate_episode_ids(
    existing_episodes: list[dict[str, Any]],
    new_episode: dict[str, Any] | None = None,
) -> None:
    episodes = [*existing_episodes]
    if new_episode is not None:
        episodes.append(new_episode)
    for key in ("episode_id", "story_id", "script_id", "packet_id"):
        seen: set[str] = set()
        for episode in episodes:
            value = episode.get(key)
            if not isinstance(value, str):
                continue
            if value in seen:
                raise ChannelMemoryValidationError(f"duplicate {key}: {value}")
            seen.add(value)


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
