# Review Artifacts

This manifest lists tracked, reviewable local artifacts introduced for repository inspection or diagnostic use. It is not a runtime export store and does not make any artifact a source-of-truth replacement for the original Markdown, database rows, or operator evidence.

Do not add runtime DBs, generated export bundles, proof screenshots, raw article bodies, OPML dumps, tokens, private traces, `.ymmp` files, or publishing outputs here.

| Artifact ID | Purpose | Identity / source of truth | Access | Validation | Review status | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| `local_docs_view` | Browser tree view for Markdown review and page-translation checks. | Manifest: `artifacts/ARTIFACTS.md`; tracked paths: `mkdocs.yml`, `.docs-view/`, `docs/index.md`, `tools/generate-doc-nav.ps1`, `scripts/operator/open_dashboard.ps1`; source of truth: original repository Markdown reached through checked-in `.docs-view/` snippet wrappers. | Repo-local launcher: `powershell -ExecutionPolicy Bypass -File scripts\operator\open_dashboard.ps1`; fallback open command from repo root: `mkdocs serve --dev-addr 127.0.0.1:8000`, then open `http://127.0.0.1:8000/`. | `python -m mkdocs build --strict`; launcher smoke with `scripts\operator\open_dashboard.ps1 -NoBrowser`. | Local review surface only; original Markdown files remain canonical. | Open through the launcher when browser review or translation aid is needed; do not edit `.docs-view/` as a replacement authority. |
| `critical_source_readback_cli` | Diagnostic readback of DB-recorded critical-view source rows for a story. | Manifest: `artifacts/ARTIFACTS.md`; tracked paths: `src/newsroom/cli/main.py`, `tests/test_critical_sources.py`; source of truth: runtime DB `story_critical_sources` rows plus article metadata. | Open command from repo root: `python -m newsroom.cli.main --db <db> packet critical-list --story <story_id> --format json`. | `python -m pytest tests\test_critical_sources.py -q` and synthetic temp-DB smoke. | Diagnostic-only; does not adopt sources, rebuild packets, clear warnings, or approve editorial/legal use. | Run against a temp or operator-approved DB when source readback is needed; use `packet add-critical` and rebuild steps only after a separate source decision. |

## Maintenance Notes

- Keep artifact paths repo-relative so the manifest remains portable across local checkouts.
- If a new tracked review artifact is added, record its purpose, tracked path, run/open command, source, validation command, and review status here.
- If a generated artifact is intentionally committed, document why it must be tracked and how to regenerate it. Otherwise keep generated output under ignored runtime directories.
