from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from newsroom.config import load_yaml_file


@dataclass(frozen=True)
class InoreaderClient:
    enabled: bool
    client_id_env: str | None = None
    client_secret_env: str | None = None
    token_store: str | None = None

    @classmethod
    def from_config_path(cls, config_path: str | Path) -> "InoreaderClient":
        data = load_yaml_file(config_path)
        raw_config = data.get("inoreader") or {}
        if not isinstance(raw_config, dict):
            raise ValueError("sources.yml field 'inoreader' must be a mapping")
        return cls(
            enabled=bool(raw_config.get("enabled", False)),
            client_id_env=raw_config.get("client_id_env"),
            client_secret_env=raw_config.get("client_secret_env"),
            token_store=raw_config.get("token_store"),
        )

    def describe_stub(self) -> str:
        return (
            "Inoreader integration is an M1 stub. "
            "Use RSS for M1; OAuth/token handling is intentionally deferred."
        )

    def fetch_stream(self, stream_id: str) -> list[object]:
        raise NotImplementedError(
            f"Inoreader stream fetch is deferred beyond M1: stream_id={stream_id}"
        )

