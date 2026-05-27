from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import yaml

from newsroom.store.models import (
    AssetCandidate,
    AssetManifest,
    QuoteEntry,
    QuoteManifest,
)


DEFAULT_ASSET_ROOT = Path("data/assets")
DEFAULT_QUOTE_ROOT = Path("data/quotes")


def write_asset_manifest(
    manifest: AssetManifest,
    asset_root: Path | str = DEFAULT_ASSET_ROOT,
) -> Path:
    """Write asset_manifest.yml into data/assets/<episode_id>/.

    The YAML form (not JSON) is intentional — operators are expected to
    edit approval_state by hand. Loading back into Python is done by
    higher-level callers when needed; the manifest is canonical on disk.
    """
    output_dir = Path(asset_root) / manifest.episode_id
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "episode_id": manifest.episode_id,
        "created_at": manifest.created_at,
        "assets": [asdict(asset) for asset in manifest.assets],
    }
    (output_dir / "asset_manifest.yml").write_text(
        _dump_yaml(payload),
        encoding="utf-8",
    )
    return output_dir


def write_quote_manifest(
    manifest: QuoteManifest,
    quote_root: Path | str = DEFAULT_QUOTE_ROOT,
) -> Path:
    """Write quote_manifest.yml into data/quotes/<episode_id>/.

    Quote manifests are human approval artifacts, so YAML is the canonical
    handoff format just like asset_manifest.yml.
    """
    output_dir = Path(quote_root) / manifest.episode_id
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "episode_id": manifest.episode_id,
        "created_at": manifest.created_at,
        "quotes": [asdict(quote) for quote in manifest.quotes],
    }
    (output_dir / "quote_manifest.yml").write_text(
        _dump_yaml(payload),
        encoding="utf-8",
    )
    return output_dir


def write_asset_manifest_file(output_dir: Path | str, manifest: AssetManifest) -> Path:
    """Write asset_manifest.yml directly into an existing episode bundle."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "asset_manifest.yml"
    payload = {
        "episode_id": manifest.episode_id,
        "created_at": manifest.created_at,
        "assets": [asdict(asset) for asset in manifest.assets],
    }
    target.write_text(_dump_yaml(payload), encoding="utf-8")
    return target


def write_quote_manifest_file(output_dir: Path | str, manifest: QuoteManifest) -> Path:
    """Write quote_manifest.yml directly into an existing episode bundle."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "quote_manifest.yml"
    payload = {
        "episode_id": manifest.episode_id,
        "created_at": manifest.created_at,
        "quotes": [asdict(quote) for quote in manifest.quotes],
    }
    target.write_text(_dump_yaml(payload), encoding="utf-8")
    return target


def load_asset_manifest(path: Path | str) -> AssetManifest | None:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return None
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    assets = [
        AssetCandidate(**entry)
        for entry in payload.get("assets", [])
        if isinstance(entry, dict)
    ]
    return AssetManifest(
        episode_id=str(payload["episode_id"]),
        assets=assets,
        created_at=str(payload["created_at"]),
    )


def load_quote_manifest(path: Path | str) -> QuoteManifest | None:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return None
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    quotes = [
        QuoteEntry(**entry)
        for entry in payload.get("quotes", [])
        if isinstance(entry, dict)
    ]
    return QuoteManifest(
        episode_id=str(payload["episode_id"]),
        quotes=quotes,
        created_at=str(payload["created_at"]),
    )


def _dump_yaml(payload: dict) -> str:
    return yaml.safe_dump(
        payload,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
