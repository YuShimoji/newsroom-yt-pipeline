# Newsroom Handoff Inventory - 2026-06-10

This docs-only record preserves the read-only handoff inventory for the active
Newsroom export package. It records what exists in this checkout, what it can
mean for a future NLMYTGen handoff, and which authority decisions are still
missing.

No NLMYTGen repository was changed. No export bundle, runtime DB, proof,
screenshot, YMM4 geometry, `.ymmp`, render, production, or publishing artifact
was copied, generated, or committed as part of this record.

## Repo State

| Item | Value |
|---|---|
| Repository | `C:\Users\PLANNER007\newsroom-yt-pipeline` |
| Branch | `main` |
| Start HEAD | `a89b8e4` |
| Latest commit at inventory time | `a89b8e4 docs: hand off channel memory restart check` |
| Upstream parity at inventory time | `HEAD...@{u}` = `0 0` |
| Working tree at inventory time | clean for tracked and untracked checks |
| Active series | `copilot_watch` |
| Active export | `data\exports\episode_756343df9853` |

Readback used for this record:

```powershell
git checkout main
git fetch --prune origin
git pull --ff-only origin main
git status --porcelain=v1 --untracked-files=all
git status --porcelain=v1 -uno
git rev-parse --short HEAD
git rev-list --left-right --count "HEAD...@{u}"
git diff --name-only
git diff --cached --name-only
.\.venv\Scripts\newsroom.exe series report --series copilot_watch
.\.venv\Scripts\newsroom.exe export inspect --episode-dir data\exports\episode_756343df9853
```

The series readback showed Microsoft Blog as
`vendor_official / microsoft_official / official` and NIST as
`standards_body / standards_body / official`. It did not show
`unclassified / no_pool`. Follow-up candidates remained `seed` and are not
approved stories.

The export inspect result was `PASS` / `No issues found`.

## Export Folder

Path:

```text
C:\Users\PLANNER007\newsroom-yt-pipeline\data\exports\episode_756343df9853
```

The folder existed at inventory time and contained these 9 files:

| File | Role in package |
|---|---|
| `asset_manifest.yml` | Asset candidates and approval state |
| `export_manifest.json` | Handoff package manifest and artifact index |
| `quote_manifest.yml` | Citation, quote, screenshot, and data-use review boundary |
| `script.csv` | YMM4 import CSV candidate |
| `script_ir.json` | Machine-readable script segments and source refs |
| `source_list.md` | Human-readable primary and critical source list |
| `visual_ir.json` | Machine-readable VisualIR |
| `visual_plan.md` | Human-readable visual plan |
| `ymm4_notes.md` | Import notes and package reading guide |

`export_manifest.json` used schema version 2 and had empty `warnings` and
`deferred_artifacts` arrays.

## Handoff File Inventory

| File | Purpose | NLMYTGen handoff relevance | Provenance, rights, or source confidence | Status |
|---|---|---|---|---|
| `export_manifest.json` | Tracks the package, referenced ids, artifact names, warnings, and deferred artifacts. | Best entry point for checking which files belong to the package. | Newsroom-generated manifest; it does not grant production or downstream integration authority. | Handoff candidate. |
| `script.csv` | Two-column YMM4 import CSV with comment rows and 6 spoken rows. | Candidate script input if NLMYTGen later receives authority to inspect or copy the export. | The CSV uses the configured narrator speaker label; local YMM4 voice/character binding remains environment-owned. No TODO skeleton rows were present. | Candidate artifact, not execution authority. |
| `script_ir.json` | Structured script segment record with source refs and review flags. | Safer than CSV for review, mapping, and source-aware downstream checks. | Newsroom-generated from the approved script path; it is not legal, publishing, or YMM4 geometry approval. | Candidate artifact. |
| `source_list.md` | Lists Microsoft Blog as primary source and NIST as critical view. | Human-readable source review material for any future handoff review. | Source roles are classified, but source-use permission and publication approval are not settled by this file. | Review material. |
| `visual_plan.md` | Human-readable plan for 6 visual units. | Useful for understanding intended cards before any NLMYTGen mapping. | Visual units are `auto_ok` within Newsroom's local-template boundary; not render proof. | Candidate review material. |
| `visual_ir.json` | Structured VisualIR with 6 visual units. | Candidate machine-readable visual input if downstream authority is granted. | Uses `takeaway_row_v1` and `claim_evidence_card_v1`; no `human_required` visual units at inventory time. | Candidate artifact. |
| `asset_manifest.yml` | Lists 6 local-template asset candidates. | Helps downstream avoid treating external media as already approved. | All assets were `local_template` and `suggested`; no external asset permission is granted here. | Candidate review material. |
| `quote_manifest.yml` | Records citation-only source use and quote/screenshot/data-use boundary. | Important boundary file for rights and quotation handling. | 10 rows were `citation_only`, 5 rows referenced NIST as `critical_view`, and no direct quote/screenshot/data extraction approval was granted. | Review material, not rights approval. |
| `ymm4_notes.md` | Summarizes import procedure, included artifacts, ids, and review gates. | Human guide for reading the export package. | It records no human-required visual/asset/quote items, but does not prove subtitle placement, overlay safety, `.ymmp`, or final geometry. | Handoff note. |

## Handoff Readiness

Readiness is `partial`, not `ready`.

The package is usable as a Newsroom-side handoff candidate because the folder
exists, all 9 expected files are present, the manifest has no warnings or
deferred artifacts, series readback is classified, and export inspection passes.

It remains partial because these decisions are not present:

- whether NLMYTGen should copy the package, review it by read-only path, or keep
  holding;
- which files would become canonical if copied;
- whether source-use, quote-use, local-template asset use, and generated-content
  boundaries are approved for production;
- whether any NLMYTGen docs should pin a read-only path;
- downstream YMM4 geometry, subtitle placement, overlay safety, `.ymmp`,
  render, production, and publishing authority.

The package is not blocked: there is no path mismatch and no active export
inspect failure. It is also not unknown: the concrete files and readback results
are known.

## Transfer Decision Material

| Option | Why it may fit | Risk or missing decision |
|---|---|---|
| Copy into NLMYTGen | Stable snapshot; less dependent on this checkout's ignored runtime folder. | No copy-in authority exists yet. A human must decide canonical files and avoid confusing candidate artifacts with production approval. |
| Read-only path reference | Lets NLMYTGen review the current export without copying files. | The path is local-machine-specific and must not be pinned in NLMYTGen docs without authority. Runtime artifact lifetime and regeneration expectations remain unresolved. |
| Hold | Avoids scope drift while preserving Newsroom evidence. | NLMYTGen-side dry-run review does not advance until a human chooses copy-in, read-only review, or another path. |

## What Can Be Offered To NLMYTGen Later

- `export_manifest.json` as the package index.
- `script.csv` and `script_ir.json` as script candidates.
- `source_list.md` as human-readable source context.
- `visual_plan.md` and `visual_ir.json` as visual planning candidates.
- `asset_manifest.yml` as a local-template asset boundary record.
- `quote_manifest.yml` as a citation-only and quote/screenshot/data-use boundary
  record.
- `ymm4_notes.md` as the package reading guide.

These are candidate handoff materials only. They do not, by themselves, approve
copy-in, read-only reference pinning, source-use rights, production, render,
publishing, or downstream YMM4 geometry work.

## What Is Not Yet Transferable As Authority

- NLMYTGen copy-in authority.
- NLMYTGen read-only path reference authority.
- Production rights approval for sources, quotes, assets, or generated content.
- Publishing approval.
- YMM4 subtitle placement, overlay safety, final geometry, or `.ymmp` proof.
- Follow-up seed promotion to approved stories.
- Source candidate adoption.
- NotebookLM API automation, Inoreader OAuth, or broad crawling.

## Human Decisions Still Required

1. Decide whether the next NLMYTGen interaction should be copy-in, read-only
   review, or continued hold.
2. If copying, decide which files become canonical and how their provenance is
   documented.
3. If using a read-only path, decide whether and where that path may be recorded
   on the NLMYTGen side.
4. Decide whether additional rights/provenance notes are needed before any
   production or render lane can treat the package as more than a candidate.

## Runtime Artifact Handling

This record intentionally does not commit `data\exports\episode_756343df9853`,
`data\ymm4_import_proof.sqlite`, proof files, screenshots, or any downstream
YMM4/render/publishing outputs. It records the read-only inventory result so a
fresh terminal can understand the handoff state without relying only on chat
history.
