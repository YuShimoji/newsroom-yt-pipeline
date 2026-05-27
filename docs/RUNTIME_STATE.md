# Runtime State

Last updated: 2026-05-27

## Sync Point

- Current sync base HEAD: `cffba27 chore: ignore data/assets runtime artifact directory`.
- Remote status at restart: `HEAD...origin/main` was `0 0`.
- Working tree was clean before the local P0 fix.
- Development environment: `.venv` with `pip install -e .[dev]`.
- Validation before this slice: `python -m pytest -q` passed with 34 tests, and `git diff --check` passed.
- Validation after this P0 slice: `python -m pytest -q` passed with 37 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster --days 120` -> score/shortlist -> packet -> script -> visual -> asset -> YMM4 export.

## Implemented Milestones

- M1 ingest / ledger: RSS and Atom fetch, SQLite article storage, URL dedupe, daily report.
- M2 clustering / scoring: story clusters, transparent topic scoring, shortlist output.
- M2.1 multi-day window: `cluster --days N` and `cluster --from --to`, with the cluster date set to the window end.
- M3 packet: NotebookLM manual-upload packet bundle; no NotebookLM API automation.
- M4 script skeleton / critic: episode plan, TODO-shaped script skeleton, source refs, speaker assignment, editorial guard review.
- M5 YMM4 export package: `script.csv`, `script_ir.json`, `source_list.md`, `ymm4_notes.md`, and `export_manifest.json`.
- M6.1 VisualIR skeleton: narrow card set covering `source_card`, `claim_evidence_card`, `timeline_spine`, and `takeaway_row`.
- M6.2 AssetManifest skeleton: VisualIR plus NotebookPacket produce asset candidates; external URL screenshots remain `human_required`, while `local_template` and `generated_diagram` remain `suggested`.

## Current P0 Fixed In This Slice

- Multi-day clusters now keep cluster member article IDs as the source of truth when drafting scripts.
- `_cmd_script_draft` no longer falls back to `list_articles_for_date` for cluster members.
- Downstream packet, critique, revise, visual, asset, and export paths already resolve cluster members by ID through the shared helper.
- The fix preserves single-day `--date` workflows while allowing `cluster --days N` output to continue into script drafting and later artifacts.

## Handoff Snapshot

- Assistant status: P0 multi-day downstream repair is implemented, tested, and ready to push.
- User action: pull `origin/main`, read this file, and continue from the next recommended work below.
- Assistant next after restart: begin M6.3 QuoteManifest skeleton unless the user redirects to critical-view source entry or YMM4 GUI import proof.
- What counts as progress next: a repo-local QuoteManifest model/export path with tests, or a clear proof artifact for the chosen alternate next step.
- What does not count as progress next: NotebookLM API automation, Inoreader OAuth, GUI/dashboard work, `.ymmp` generation, YouTube upload, or NLMYTGen subprocess/path integration.

## Not Complete Or Not Proven

- M6.3 QuoteManifest is not implemented.
- M6.4 export integration is not implemented.
- `critical_views` has no durable source-entry path yet; current packets surface the missing view as an operator task.
- Packet persistence is artifact-only; packet records are not stored as first-class DB rows.
- YMM4 GUI import proof has not been performed.
- NotebookLM API automation is out of scope.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- M7 series / channel memory and weekly strategy are not implemented.
- Inoreader OAuth / token flow is still deferred.
- External image download and automatic external asset approval remain out of scope.

## Next Recommended Work

1. M6.3 QuoteManifest skeleton.
   Purpose: create the publish-gate counterpart to AssetManifest for text, screenshot, image, clip, and data quotes.
   Effect: rights and reused-content review can move from loose notes into editable artifacts.

2. Critical-view source path.
   Purpose: let operators add or classify critical sources before script review.
   Effect: packet and script critic warnings become actionable instead of permanent manual reminders.

3. YMM4 GUI import proof.
   Purpose: confirm the generated `script.csv` and `ymm4_notes.md` are usable in the actual editor.
   Effect: M5 can be described as YMM4-import proven rather than package-only.

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
