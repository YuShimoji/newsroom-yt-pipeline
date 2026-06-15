# Review Artifacts

This manifest lists tracked, reviewable local artifacts introduced for repository inspection or diagnostic use. It is not a runtime export store and does not make any artifact a source-of-truth replacement for the original Markdown, database rows, or operator evidence.

Do not add runtime DBs, generated export bundles, proof screenshots, raw article bodies, OPML dumps, tokens, private traces, `.ymmp` files, or publishing outputs here.

| Artifact ID | Purpose | Tracked paths | Open or run | Generated from | Validation | Review status |
| --- | --- | --- | --- | --- | --- | --- |
| `local_docs_view` | Browser tree view for Markdown review and page-translation checks. | `mkdocs.yml`, `.docs-view/`, `docs/index.md`, `tools/generate-doc-nav.ps1` | `mkdocs serve --dev-addr 127.0.0.1:8000`, then open `http://127.0.0.1:8000/` | Existing repository Markdown via checked-in `.docs-view/` snippet wrappers. | `python -m mkdocs build --strict` | Local review surface only; original Markdown files remain canonical. |
| `critical_source_readback_cli` | Diagnostic readback of DB-recorded critical-view source rows for a story. | `src/newsroom/cli/main.py`, `tests/test_critical_sources.py` | `python -m newsroom.cli.main --db <db> packet critical-list --story <story_id> --format json` | Runtime DB `story_critical_sources` rows plus article metadata. | `python -m pytest tests\test_critical_sources.py -q` and synthetic temp-DB smoke. | Diagnostic-only; does not adopt sources, rebuild packets, or approve editorial/legal use. |

## Maintenance Notes

- Keep artifact paths repo-relative so the manifest remains portable across local checkouts.
- If a new tracked review artifact is added, record its purpose, tracked path, run/open command, source, validation command, and review status here.
- If a generated artifact is intentionally committed, document why it must be tracked and how to regenerate it. Otherwise keep generated output under ignored runtime directories.
