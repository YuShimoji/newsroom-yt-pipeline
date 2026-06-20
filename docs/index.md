# Local Documentation View

This local MkDocs view exists only to make the repository Markdown easier to inspect in a browser with a tree pane and page translation tools. The canonical documents remain in their original files and paths. This view must not be treated as a translated, summarized, or rewritten replacement for those source documents.

## Open Locally

From the repository root on Windows PowerShell, use the repo-local launcher:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\operator\open_dashboard.ps1
```

The launcher resolves the repository root dynamically, starts the MkDocs view on `http://127.0.0.1:8000/` if it is not already running, and opens the browser. If you need to keep the browser closed while checking the server, add `-NoBrowser`.

Fallback command:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install mkdocs-material
mkdocs serve --dev-addr 127.0.0.1:8000
```

Then open:

```text
http://127.0.0.1:8000/
```

Use the browser's page translation feature, such as Chrome, Edge, or a DeepL extension, as a temporary reading aid. Do not save browser-translated text back into this repository unless a separate editorial task explicitly asks for a reviewed translation.

## Review Input

Feedback on this docs view may be written in ordinary freeform language. Fixed response labels are not required. Useful comments can point to a document that looks stale, an access route that fails, a section that needs a Review Card, or a place where the original Markdown should remain the source of truth.

## Operation Cockpit Guidance

For supervisor-facing report guidance, read `docs/DEVELOPMENT_PRACTICES.md` first and use `artifacts/ARTIFACTS.md` for reviewable artifact identity and access. The current continuation state remains in `docs/RUNTIME_STATE.md`; the short restart packet remains `docs/HANDOFF.md`.

## How The Tree Is Organized

The navigation groups are practical reading buckets, not authority labels:

| Group | What it contains |
| --- | --- |
| Overview | The local-view entry page, repository README, and development-practice authority. |
| Specs | Documents that appear to describe intended scope, downstream boundaries, or operator procedure. |
| Runtime State | Restart and current-state records that appear to be active handoff context. |
| Development Notes | Review ledgers, rule-alignment packets, and inventory notes that appear to record implementation or handoff decisions. |
| Artifacts | The review-artifact manifest and README files for tracked authority or memory artifact roots. |
| Prompts | Prompt templates used by operator-side or future LLM-assisted workflows. |

When a document's role is uncertain, prefer reading the original file path and surrounding repository context before assigning stronger meaning to it. Some documents contain existing mojibake or mixed-language content; this view intentionally preserves that content instead of repairing or interpreting it.

Historical verification records may contain absolute paths, commit IDs, and machine-specific observations from the environment where they were written. Treat those as evidence snapshots; rerun the git and local validation commands in this checkout before using them as current authority.

## Regenerating A Navigation Candidate

The checked-in `mkdocs.yml` has a hand-reviewed minimal navigation. To inspect a fresh candidate after adding or moving Markdown files, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\generate-doc-nav.ps1
```

The script prints a candidate `nav` block to standard output. Review the result before copying anything into `mkdocs.yml`.

## Docs View Source Boundary

The `.docs-view/` tree is intentionally tracked because MkDocs reads from a single `docs_dir`. Files there should stay as thin snippet wrappers, such as `--8<-- "docs/RUNTIME_STATE.md"`, pointing back to the original repository Markdown. The generated site output is `.mkdocs-site/` and remains ignored.
