from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import yaml

from newsroom.store.models import AssetManifest


DEFAULT_ASSET_ROOT = Path("data/assets")


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
        yaml.safe_dump(
            payload,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )
    return output_dir
