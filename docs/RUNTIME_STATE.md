# Runtime State

Last updated: 2026-05-27

## Sync Point

- Current sync base HEAD: `1f4e563 fix: connect multi-day clusters to downstream drafts`.
- Remote status at restart: `HEAD...origin/main` was `0 0` after fast-forward.
- Working tree was clean before the local M6.3 slice.
- Development environment: `.venv` with `pip install -e .[dev]`.
- Validation before this slice: `python -m pytest -q` passed with 34 tests, and `git diff --check` passed.
- Validation after the upstream P0 slice: `python -m pytest -q` passed with 37 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster --days 120` -> score/shortlist -> packet -> script -> visual -> asset -> YMM4 export.
- Validation after this M6.3 slice: `python -m pytest -q` passed with 40 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster --from/--to` -> score -> script -> visual -> quote.
- Validation after this M6.4 slice: `python -m pytest -q` passed with 42 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster` -> score -> shortlist -> packet -> script -> visual -> asset -> quote -> YMM4 export.

## Implemented Milestones

- M1 ingest / ledger: RSS and Atom fetch, SQLite article storage, URL dedupe, daily report.
- M2 clustering / scoring: story clusters, transparent topic scoring, shortlist output.
- M2.1 multi-day window: `cluster --days N` and `cluster --from --to`, with the cluster date set to the window end.
- M3 packet: NotebookLM manual-upload packet bundle; no NotebookLM API automation.
- M4 script skeleton / critic: episode plan, TODO-shaped script skeleton, source refs, speaker assignment, editorial guard review.
- M5 YMM4 export package: `script.csv`, `script_ir.json`, `source_list.md`, `ymm4_notes.md`, and `export_manifest.json`.
- M6.1 VisualIR skeleton: done. Narrow card set covering `source_card`, `claim_evidence_card`, `timeline_spine`, and `takeaway_row`.
- M6.2 AssetManifest skeleton: done. VisualIR plus NotebookPacket produce asset candidates; external URL screenshots remain `human_required`, while `local_template` and `generated_diagram` remain `suggested`.
- M6.3 QuoteManifest skeleton: done. ScriptIR plus VisualIR plus NotebookPacket produce source-backed text quote review rows and source-card screenshot review rows; all rows start as `human_required`.
- M6.4 export integration: done. `newsroom export ymm4` now bundles `visual_plan.md`, `visual_ir.json`, `asset_manifest.yml`, and `quote_manifest.yml` alongside the existing script/source/notes/manifest handoff files.

## Current M6.4 Completed In This Slice

- Upgraded YMM4 export manifest to `schema_version: 2`.
- `newsroom export ymm4` now writes `visual_plan.md`, `visual_ir.json`, `asset_manifest.yml`, and `quote_manifest.yml` into the episode export directory.
- Export reuses an existing DB VisualIR when available; otherwise it generates VisualIR during export and persists it.
- Export reuses existing `asset_manifest.yml` / `quote_manifest.yml` from the export bundle or default artifact roots when available; otherwise it generates conservative manifests without downloading or auto-approving external assets.
- `export_manifest.json` now references visual / asset / quote artifact ids or paths and lists all bundle files in `artifacts`.
- M6 visual / asset / quote artifacts are no longer listed in `deferred_artifacts` when generated.
- `ymm4_notes.md` now explains how to read visual / asset / quote artifacts and states that any remaining `human_required` item requires operator review before publishing.

## Handoff Snapshot

- Assistant status: M6.4 export integration is implemented and tested locally.
- User action: run or inspect a YMM4 episode export bundle and verify that script, visual, asset, quote, source, notes, and manifest artifacts are all present.
- Assistant next after restart: choose either YMM4 GUI import proof or critical-view source entry as the next P0 slice.
- What counts as progress next: a clear YMM4 import proof artifact, a durable path for operator-added critical sources, QuoteManifest review tightening, or packet persistence.
- What does not count as progress next: NotebookLM API automation, Inoreader OAuth, GUI/dashboard work, `.ymmp` generation, YouTube upload, or NLMYTGen subprocess/path integration.

## Not Complete Or Not Proven

- `critical_views` has no durable source-entry path yet; current packets surface the missing view as an operator task.
- Packet persistence is artifact-only; packet records are not stored as first-class DB rows.
- QuoteManifest persistence is artifact-only; quote records are not stored as first-class DB rows.
- QuoteManifest rows are conservative candidates, not legal decisions; all start as `human_required`.
- Additional visual cards from PROJECT_SPEC §14 (`version_diff`, `actor_map`, `risk_meter`, `context_stack`, `quote_screenshot`, `neutral_background`) are not implemented.
- YMM4 GUI import proof has not been performed.
- NotebookLM API automation is out of scope.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- M7 series / channel memory and weekly strategy are not implemented.
- Inoreader OAuth / token flow is still deferred.
- External image download and automatic external asset approval remain out of scope.

## Next Recommended Work

1. P0: YMM4 GUI import proof.
   Purpose: confirm the generated `script.csv` and `ymm4_notes.md` are usable in the actual editor.
   Effect: M5/M6 can be described as YMM4-import proven rather than package-only.

2. P0: Critical-view source path.
   Purpose: let operators add or classify critical sources before script review.
   Effect: packet and script critic warnings become actionable instead of permanent manual reminders.

3. P1: QuoteManifest tightening.
   Purpose: reduce noisy quote rows by distinguishing citation-only source_refs from direct quote or screenshot intent.
   Effect: human_required review stays focused on actual publish risk instead of every sourced segment.

4. P1: Packet persistence.
   Purpose: store packet records as first-class DB rows instead of rebuilding them from cluster/articles at each downstream step.
   Effect: operator edits and critical-view additions can survive across later workflow stages.

5. P2: Source expansion.
   Purpose: add more deliberate source pools without implementing broad crawling or Inoreader OAuth.
   Effect: shortlist quality improves while RSS-first and manual approval boundaries remain intact.

6. P2: M7 series / channel memory.
   Purpose: connect daily production to series history, past claims, and next-episode planning.
   Effect: editorial continuity can be scored and reused across weekly planning.

## Restart Commands

```powershell
git checkout main
git pull --ff-only origin main
.venv\Scripts\Activate.ps1
python -m pytest -q
git diff --check
```

If `.venv` is missing:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```
