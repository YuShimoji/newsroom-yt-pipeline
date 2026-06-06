from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REQUIRED_EXPORT_FILES: tuple[str, ...] = (
    "script.csv",
    "script_ir.json",
    "source_list.md",
    "ymm4_notes.md",
    "export_manifest.json",
    "visual_plan.md",
    "visual_ir.json",
    "asset_manifest.yml",
    "quote_manifest.yml",
)


@dataclass(frozen=True)
class InspectionIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class ExportInspection:
    episode_dir: Path
    issues: list[InspectionIssue]

    @property
    def errors(self) -> list[InspectionIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[InspectionIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def passed(self) -> bool:
        return not self.errors


def inspect_episode_bundle(episode_dir: str | Path) -> ExportInspection:
    """Inspect an M6.4 export bundle before manual YMM4 import.

    This is intentionally a local file consistency check. It does not open,
    automate, or validate YMM4 itself.
    """
    root = Path(episode_dir)
    issues: list[InspectionIssue] = []

    if not root.exists() or not root.is_dir():
        return ExportInspection(
            episode_dir=root,
            issues=[
                _error(
                    "episode_dir_missing",
                    f"Episode directory does not exist: {root}",
                )
            ],
        )

    for filename in REQUIRED_EXPORT_FILES:
        if not (root / filename).exists():
            issues.append(_error("required_file_missing", f"Missing {filename}"))

    manifest = _load_json(root / "export_manifest.json", issues)
    if isinstance(manifest, dict):
        _inspect_manifest(root, manifest, issues)

    _inspect_script_csv(root / "script.csv", issues)
    asset_manifest = _load_yaml(root / "asset_manifest.yml", issues, "asset_manifest")
    quote_manifest = _load_yaml(root / "quote_manifest.yml", issues, "quote_manifest")
    visual_ir = _load_json(root / "visual_ir.json", issues, "visual_ir")

    if isinstance(asset_manifest, dict):
        _warn_human_required(asset_manifest.get("assets", []), "assets", issues)
    if isinstance(quote_manifest, dict):
        _warn_human_required(quote_manifest.get("quotes", []), "quotes", issues)
    if isinstance(visual_ir, dict):
        _warn_human_required(visual_ir.get("visual_units", []), "visual_units", issues)

    return ExportInspection(episode_dir=root, issues=issues)


def _inspect_manifest(
    episode_dir: Path, manifest: dict[str, Any], issues: list[InspectionIssue]
) -> None:
    if manifest.get("schema_version") != 2:
        issues.append(
            _error(
                "manifest_schema_version",
                f"Expected export_manifest.json schema_version 2, got {manifest.get('schema_version')!r}",
            )
        )

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(_error("manifest_artifacts", "Manifest artifacts must be a mapping"))
    else:
        for artifact_key, artifact_path in artifacts.items():
            if not isinstance(artifact_path, str):
                issues.append(
                    _error(
                        "manifest_artifact_path",
                        f"Artifact {artifact_key!r} path must be a string",
                    )
                )
                continue
            if not (episode_dir / artifact_path).exists():
                issues.append(
                    _error(
                        "manifest_artifact_missing",
                        f"Manifest artifact {artifact_key!r} points to missing file: {artifact_path}",
                    )
                )

    deferred = manifest.get("deferred_artifacts", [])
    if deferred is None:
        return
    if not isinstance(deferred, list):
        issues.append(_error("deferred_artifacts", "deferred_artifacts must be a list"))
        return
    for item in deferred:
        if not (isinstance(item, dict) and item.get("reason")):
            issues.append(
                _error(
                    "deferred_artifact_reason_missing",
                    "Deferred artifact entries must include a reason",
                )
            )

    for warning in manifest.get("warnings", []) or []:
        issues.append(_warning("manifest_warning", str(warning)))


def _inspect_script_csv(path: Path, issues: list[InspectionIssue]) -> None:
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        issues.append(_error("script_csv_read", f"script.csv is not readable: {exc}"))
        return

    todo_rows = 0
    for row_index, row in enumerate(rows, start=1):
        if len(row) == 1 and row[0].startswith("#"):
            continue
        if len(row) == 2:
            if "TODO[" in row[1]:
                todo_rows += 1
            continue
        issues.append(
            _error(
                "script_csv_shape",
                f"script.csv row {row_index} must be 2 columns or a # comment row",
            )
        )
    if todo_rows:
        issues.append(
            _warning(
                "script_todo_skeleton",
                f"script.csv contains {todo_rows} TODO skeleton row(s); "
                "YMM4 import can pass, but spoken script still requires materialization.",
            )
        )


def _load_json(
    path: Path,
    issues: list[InspectionIssue],
    label: str | None = None,
) -> Any | None:
    if not path.exists():
        return None
    name = label or path.name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        issues.append(_error(f"{name}_json_read", f"{path.name} is not valid JSON: {exc}"))
        return None


def _load_yaml(
    path: Path,
    issues: list[InspectionIssue],
    label: str,
) -> Any | None:
    if not path.exists():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as exc:
        issues.append(_error(f"{label}_yaml_read", f"{path.name} is not valid YAML: {exc}"))
        return None
    if not isinstance(payload, dict):
        issues.append(_error(f"{label}_shape", f"{path.name} must contain a mapping"))
        return None
    return payload


def _warn_human_required(
    entries: Any,
    label: str,
    issues: list[InspectionIssue],
) -> None:
    if not isinstance(entries, list):
        return
    count = sum(
        1
        for entry in entries
        if isinstance(entry, dict) and entry.get("approval_state") == "human_required"
    )
    if count:
        issues.append(
            _warning(
                "human_required",
                f"{count} {label} item(s) remain human_required",
            )
        )


def _error(code: str, message: str) -> InspectionIssue:
    return InspectionIssue(severity="error", code=code, message=message)


def _warning(code: str, message: str) -> InspectionIssue:
    return InspectionIssue(severity="warning", code=code, message=message)
