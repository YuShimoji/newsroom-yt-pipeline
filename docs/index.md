# Local Documentation View

This local MkDocs view exists only to make the repository Markdown easier to inspect in a browser with a tree pane and page translation tools. The canonical documents remain in their original files and paths. This view must not be treated as a translated, summarized, or rewritten replacement for those source documents.

## Open Locally

From the repository root on Windows PowerShell:

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

## How The Tree Is Organized

The navigation groups are practical reading buckets, not authority labels:

| Group | What it contains |
| --- | --- |
| Overview | The local-view entry page, repository README, and development-practice authority. |
| Specs | Documents that appear to describe intended scope, downstream boundaries, or operator procedure. |
| Runtime State | Restart and current-state records that appear to be active handoff context. |
| Development Notes | Review ledgers, rule-alignment packets, and inventory notes that appear to record implementation or handoff decisions. |
| Artifacts | README files for tracked authority or memory artifact roots. |
| Prompts | Prompt templates used by operator-side or future LLM-assisted workflows. |

When a document's role is uncertain, prefer reading the original file path and surrounding repository context before assigning stronger meaning to it. Some documents contain existing mojibake or mixed-language content; this view intentionally preserves that content instead of repairing or interpreting it.

Historical verification records may contain absolute paths, commit IDs, and machine-specific observations from the environment where they were written. Treat those as evidence snapshots; rerun the git and local validation commands in this checkout before using them as current authority.

## Regenerating A Navigation Candidate

The checked-in `mkdocs.yml` has a hand-reviewed minimal navigation. To inspect a fresh candidate after adding or moving Markdown files, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\generate-doc-nav.ps1
```

The script prints a candidate `nav` block to standard output. Review the result before copying anything into `mkdocs.yml`.
