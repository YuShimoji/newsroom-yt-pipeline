# Runtime State

Last updated: 2026-06-07

## Sync Point

- Current sync base HEAD before this slice: `4b83531 feat: integrate M6 artifacts into YMM4 export`.
- Current pulled HEAD before this docs-only handoff refresh: `8c3bc27 docs: refresh handoff restart point`.
- Remote status at restart: `HEAD...origin/main` was `0 0`.
- M6.4 export integration is pushed to `origin/main` and was in sync before this slice.
- YMM4 import proof preparation and handoff confirmation are pushed to `origin/main`; pull latest `origin/main` and read `docs/HANDOFF.md` as the short restart packet.
- Working tree was clean before the local YMM4 import proof preparation slice.
- Development environment: `.venv` with `pip install -e .[dev]`.
- Validation before this slice: `python -m pytest -q` passed with 34 tests, and `git diff --check` passed.
- Validation after the upstream P0 slice: `python -m pytest -q` passed with 37 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster --days 120` -> score/shortlist -> packet -> script -> visual -> asset -> YMM4 export.
- Validation after this M6.3 slice: `python -m pytest -q` passed with 40 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster --from/--to` -> score -> script -> visual -> quote.
- Validation after this M6.4 slice: `python -m pytest -q` passed with 42 tests, `git diff --check` passed, and a temp-DB smoke reached `cluster` -> score -> shortlist -> packet -> script -> visual -> asset -> quote -> YMM4 export.
- Validation after this YMM4 proof prep slice: `python -m pytest -q` passed with 48 tests, `git diff --check` passed, and `newsroom export inspect` was exercised against a temp episode export bundle.
- Handoff confirmation on 2026-06-01: `HEAD...origin/main` was `0 0` before that doc refresh, working tree was clean, and no implementation changes were pending.
- Handoff refresh on 2026-06-03: fast-forwarded from `4b83531` to `8c3bc27`, `HEAD...origin/main` was `0 0`, `.venv\Scripts\python.exe -m pytest -q` passed with 48 tests, `git diff --check` passed, and `newsroom export inspect --help` was available.
- YMM4 GUI proof handoff on 2026-06-03: fast-forwarded to `20cfd7a`, fetched real RSS into `data\ymm4_import_proof.sqlite`, generated `data\exports\episode_756343df9853`, wrote a git-ignored proof draft at `data\proofs\ymm4_import\episode_756343df9853\proof.yml`, and confirmed `newsroom export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with review warnings. YMM4 GUI import itself is still operator-pending.
- Meta-review / P0-B slice on 2026-06-04: pulled `origin/main` to `36c1988`, confirmed `HEAD...origin/main` was `0 0`, reran `newsroom export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with review warnings, implemented DB-backed critical-view source entry, ran `.venv\Scripts\python.exe -m pytest -q` -> 53 passed, and `git diff --check` -> passed.
- Active C1/NIST source application on 2026-06-05: started clean from `13246b5`, `HEAD...origin/main` was `0 0`, recorded C1/NIST with `newsroom packet add-critical`, rebuilt packet/script/visual/asset/quote/export for `story_20260603_503c39418f15862d` / `episode_756343df9853`, fixed export rebuilds to prefer refreshed asset/quote roots over stale export-bundle copies, and confirmed `newsroom export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with no `critical_view` warning. Remaining warnings are `speculation_vs_fact`, 6 segments `needs_human_review`, 1 asset `human_required`, 11 quotes `human_required`, and 1 visual unit `human_required`. Validation: `.venv\Scripts\python.exe -m pytest -q` -> 54 passed; `git diff --check` -> passed.
- YMM4 GUI proof attempt on 2026-06-05: opened YukkuriMovieMaker v4.43.1.0 and loaded `data\exports\episode_756343df9853\script.csv` into `台本編集 / script.csv`, but the proof stopped because YMM4 reported `キャラクターが見つかりませんでした。キャラクターを指定してください。` for exported speaker `ナレーター`. The visible YMM4 selector showed `ゆっくり霊夢`, so the local YMM4 character setup did not match `configs/speakers.yml`. The ignored proof YAML was updated locally to `import_result: failed` / `decision.status: needs_fix`; this is not a passed import proof.
- Final sync validation on this PLANNER007 checkout: `.venv\Scripts\python.exe -m pytest -q` -> 54 passed and `git diff --check` -> passed. `export inspect` on the local git-ignored `data\exports\episode_756343df9853` still returned PASS but showed the older `critical_view` warning, so regenerate the active C1/NIST runtime artifacts if the next terminal needs the no-`critical_view` export state.
- P0-A restart context reflection on 2026-06-05: reread the restart docs and subtitle boundary gate after the GUI attempt, kept the GUI proof status as `needs_fix`, and reflected that newsroom-side proof covers CSV import acceptance and handoff-file readability only. Git-ignored runtime exports and proof YAMLs remain checkout-sensitive and must not be committed.
- P0-A request validity check on 2026-06-06: pulled `origin/main` at `2b459a2`, confirmed `HEAD...origin/main` was `0 0`, reread the P0-A prompt, proof YAML, and authority docs, and reran `export inspect` -> PASS with no `critical_view` warning. The request is valid only as an external YMM4 character-registry fix plus proof rerun. Repo-side `configs\speakers.yml` and `script.csv` already agree on `ナレーター`; no code change or speaker remap to `ゆっくり霊夢` is justified. A safe file-backed YMM4 character registry was not identified under `C:\Users\thank\AppData\Local\YukkuriMovieMaker\v4`, which contained only `temp` content in this run.
- P0-A YMM4 GUI proof pass on 2026-06-07: operator created a YMM4 character named `ナレーター`, reran import for `data\exports\episode_756343df9853\script.csv`, and reported that YMM4 recognized the CSV and imported it normally. The local proof YAML was updated to `import_result: pass` / `decision.status: passed`. `TODO[...]` tokens were pronounced because they are literal TODO skeleton script text, not an import failure. This proves CSV import acceptance and handoff-file readability only; subtitle placement, overlay safety, and final YMM4 geometry remain outside newsroom-side proof.
- Post-proof TODO skeleton gate on 2026-06-07: re-read the active export and found all 6 spoken `script.csv` / `script_ir.json` rows still contain literal `TODO[...]` skeleton text. `export inspect` now reports this as `script_todo_skeleton` warning while still passing the bundle. This makes P0.5 Script materialization the next active artifact path before P1 QuoteManifest tightening.
- Validation after the TODO skeleton inspector slice: `.venv\Scripts\python.exe -m pytest -q` -> 55 passed, `git diff --check` -> passed, and `.venv\Scripts\python.exe -m newsroom.cli.main export inspect --episode-dir data\exports\episode_756343df9853` -> PASS with `script_todo_skeleton`, `speculation_vs_fact`, `needs_human_review`, and `human_required` warnings; `critical_view` warning remains absent.
- P0.5 materialization draft path on 2026-06-07: added `newsroom script materialize --script <script_id>` to write `script_materialization.yml` under `data/scripts/<script_id>/`. The draft preserves segment ids, speaker, current TODO text, source refs, critical refs, suggested operator angles, empty `operator_fill`, and human-review flags. It does not modify the DB script row, `script_ir.json`, `script.csv`, or export bundles, so `script_todo_skeleton` remains until operator-approved replacement is applied.
- Validation after the P0.5 materialization draft slice: `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py tests\test_export_inspector.py -q` -> 10 passed, `.venv\Scripts\python.exe -m pytest -q` -> 58 passed, `git diff --check` -> passed, active materialization draft generation succeeded for `script_d2a46430e084`, and active `export inspect` remained PASS with `script_todo_skeleton` present and `critical_view` absent.
- P0.5-B operator-approved replacement intake on 2026-06-07: added `newsroom script apply-materialization --script <script_id> --draft <path> --require-approved`. The command validates filled `operator_fill`, `replacement_status: approved`, current-text freshness, speaker match, source refs, and critical refs before updating the DB ScriptIR and refreshed script bundle. It does not rebuild export bundles automatically. The active draft was rejected because all 6 `operator_fill` values are empty and all 6 rows are still `operator_pending`, so no active replacement was executed.
- Validation after the P0.5-B replacement intake slice: `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py tests\test_export_inspector.py -q` -> 16 passed, `.venv\Scripts\python.exe -m pytest -q` -> 64 passed, `git diff --check` -> passed, active apply rejected the unfilled/unapproved runtime draft as expected, and active `export inspect` remained PASS with `script_todo_skeleton` present and `critical_view` absent.
- P0.5-C approved materialization authority on 2026-06-07: added `docs\approved_materializations\` as the tracked sanitized authority root, `newsroom script approve-materialization` to create a portable approved record from a filled/approved draft, and `newsroom script apply-approved-materialization` to apply that record while preserving speaker, source refs, critical refs, visual refs, claim type, and human-review flags. Active `script_materialization.yml` is still unfilled/unapproved, so no active approved record or active replacement was created.
- Validation after the P0.5-C approved authority slice: `.venv\Scripts\python.exe -m pytest tests\test_script_materialization.py -q` -> 17 passed, `.venv\Scripts\python.exe -m pytest -q` -> 72 passed, `git diff --check` -> passed, active `approve-materialization` rejected the unfilled/unapproved runtime draft as expected, and active `export inspect` remained PASS with `script_todo_skeleton` present and `critical_view` absent.
- P0.5-D approved materialization apply on 2026-06-07: operator explicitly approved adopting all 6 `operator_fill_suggestion` values from the runtime draft as narration. The ignored draft was filled locally, `docs\approved_materializations\script_d2a46430e084.materialization.yml` was generated as the tracked sanitized authority, the record was applied to DB ScriptIR and the refreshed script bundle, and `data\exports\episode_756343df9853` was rebuilt.
- Active export inspect after P0.5-D: PASS with `script_todo_skeleton` absent and `critical_view` absent. Remaining warnings are publication/operator gates: `speculation_vs_fact`, 6 segments `needs_human_review`, 1 asset `human_required`, 11 quotes `human_required`, and 1 visual unit `human_required`.
- Validation after the P0.5-D approved materialization apply: `.venv\Scripts\python.exe -m pytest -q` -> 72 passed, `git diff --check` -> passed, and active export `script_ir.json` has 0 TODO rows.
- P1 QuoteManifest tightening on 2026-06-07: citation-only source-ref rows now use `review_level: citation_only` / `approval_state: citation_only`, while direct quote, screenshot, and data-use intent remain `human_required`. Active `quote_manifest.yml` readback: 11 rows total, 10 citation-only rows, 1 screenshot human_required row, 5 C1/NIST rows retained as `source_role: critical_view`.
- Active export inspect after P1 QuoteManifest tightening: PASS with `critical_view` absent and `script_todo_skeleton` absent. The M6 handoff warning dropped from 13 to 3 total human_required visual/asset/quote items: 1 asset, 1 quote screenshot, and 1 visual unit. `speculation_vs_fact` and 6 `needs_human_review` segment warnings remain as publication/operator gates.
- Validation after P1 QuoteManifest tightening: targeted quote/export tests -> 21 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 74 passed; `git diff --check` -> passed.
- P1 remaining visual/asset/screenshot review gate on 2026-06-07: the remaining 3 `human_required` items were all source-card screenshot effects on the facts chapter. The active decision was `replace_with_local_diagram`: citation-only facts now use `claim_evidence_card`, while explicit `source_card` / `screenshot` / `quote_screenshot` intent still remains `human_required`.
- Active export inspect after the P1 visual/asset/screenshot gate: PASS with `critical_view` absent and `script_todo_skeleton` absent. VisualIR has 6 units and 0 `human_required`; AssetManifest has 6 local-template candidates and 0 `human_required`; QuoteManifest has 10 citation-only text rows, 0 screenshot rows, and retains 5 C1/NIST critical-view rows. Remaining warnings are only `speculation_vs_fact` and 6 broad `needs_human_review` segment gates.
- Validation after the P1 visual/asset/screenshot gate: targeted visual/asset/quote/export tests -> 33 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 77 passed; `git diff --check` -> passed.
- P1 broad script review gate on 2026-06-07: added `docs\script_review_gates\script_d2a46430e084.review.yml` as a tracked handoff artifact for the remaining script publication gates. The review gate classifies all 6 segments as `operator_approval_required`, keeps interpretation rows under `speculation_vs_fact` / publication-review caution, and makes no script text or review-flag changes.
- Active export inspect after the P1 broad script review gate: PASS with `critical_view`, `script_todo_skeleton`, and visual/asset/quote `human_required` absent. Remaining warnings intentionally stay: `speculation_vs_fact` and 6 broad `needs_human_review` segment gates.
- Validation after the P1 broad script review gate: targeted script/export tests -> 23 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 78 passed; `git diff --check` -> passed.

## Implemented Milestones

- M1 ingest / ledger: RSS and Atom fetch, SQLite article storage, URL dedupe, daily report.
- M2 clustering / scoring: story clusters, transparent topic scoring, shortlist output.
- M2.1 multi-day window: `cluster --days N` and `cluster --from --to`, with the cluster date set to the window end.
- M3 packet: NotebookLM manual-upload packet bundle; no NotebookLM API automation.
- M4 script skeleton / critic: episode plan, TODO-shaped script skeleton, source refs, speaker assignment, editorial guard review.
- P0.5 script materialization draft: operator-editable `script_materialization.yml` generation from an existing ScriptIR and rebuilt packet.
- P0.5-B script materialization apply: reject-first operator-approved replacement intake that preserves ScriptIR metadata and updates only text when validation passes.
- P0.5-C approved materialization authority: tracked sanitized approved-materialization records under `docs\approved_materializations\`, plus CLI validation and apply path.
- P0.5-D active script materialization: active approved record generated and applied for `script_d2a46430e084`; active export rebuilt with no literal TODO spoken rows.
- M5 YMM4 export package: `script.csv`, `script_ir.json`, `source_list.md`, `ymm4_notes.md`, and `export_manifest.json`.
- M6.1 VisualIR skeleton: done. Narrow card set covering `source_card`, `claim_evidence_card`, `timeline_spine`, and `takeaway_row`.
- M6.2 AssetManifest skeleton: done. VisualIR plus NotebookPacket produce asset candidates; external URL screenshots remain `human_required`, while `local_template` and `generated_diagram` remain `suggested`.
- M6.3 QuoteManifest skeleton: done. ScriptIR plus VisualIR plus NotebookPacket produce citation-only source-ref rows, direct quote/data-use review rows when explicitly intended, and source-card screenshot review rows.
- P1 QuoteManifest tightening: done for the active path. Citation-only rows no longer count as `human_required`; screenshot/direct quote/data-use intent remains operator-reviewed.
- P1 visual/asset/screenshot gate: done for the active path. Citation-only facts default to local `claim_evidence_card`; explicit source-card/screenshot intent still remains operator-reviewed.
- P1 broad script review gate: handoff-only done for the active path. Remaining script warnings are classified, not cleared.
- M6.4 export integration: done. `newsroom export ymm4` now bundles `visual_plan.md`, `visual_ir.json`, `asset_manifest.yml`, and `quote_manifest.yml` alongside the existing script/source/notes/manifest handoff files.

## M6.4 Completed In Previous Slice

- Upgraded YMM4 export manifest to `schema_version: 2`.
- `newsroom export ymm4` now writes `visual_plan.md`, `visual_ir.json`, `asset_manifest.yml`, and `quote_manifest.yml` into the episode export directory.
- Export reuses an existing DB VisualIR when available; otherwise it generates VisualIR during export and persists it.
- Export reuses existing `asset_manifest.yml` / `quote_manifest.yml` from the default artifact roots first, then falls back to export-bundle copies when no refreshed root manifest exists; otherwise it generates conservative manifests without downloading or auto-approving external assets.
- `export_manifest.json` now references visual / asset / quote artifact ids or paths and lists all bundle files in `artifacts`.
- M6 visual / asset / quote artifacts are no longer listed in `deferred_artifacts` when generated.
- `ymm4_notes.md` now explains how to read visual / asset / quote artifacts and states that any remaining `human_required` item requires operator review before publishing.

## Current YMM4 Proof Prep Completed In This Slice

- Added `docs/YMM4_IMPORT_PROOF.md` as the operator hand-run procedure for YMM4 CSV import proof.
- Added `docs/templates/ymm4_import_proof_template.yml` as the proof record template.
- Added `newsroom export inspect --episode-dir <path>` as a pre-import self-check for M6.4 episode bundles.
- The inspect command checks required bundle files, `export_manifest.json` schema v2, manifest artifact path consistency, `script.csv` CSV shape, readable asset / quote YAML, TODO skeleton rows, and `human_required` warning counts.
- YMM4 GUI import itself is still operator-pending. No YMM4 GUI automation was performed.

## Current YMM4 GUI Proof Handoff Completed In This Slice

- Pulled latest `origin/main` to `20cfd7a docs: add restart handoff packet`.
- Generated a local proof target from real RSS input using the standard CLI flow: fetch -> cluster `--days 120` -> score -> shortlist -> packet -> script -> visual -> asset -> quote -> YMM4 export.
- Selected Microsoft Blog story `story_20260603_503c39418f15862d` and generated script `script_d2a46430e084`.
- Exported episode bundle `data\exports\episode_756343df9853` containing `script.csv`, `script_ir.json`, `source_list.md`, `ymm4_notes.md`, `visual_plan.md`, `visual_ir.json`, `asset_manifest.yml`, `quote_manifest.yml`, and `export_manifest.json`.
- Ran `newsroom export inspect --episode-dir data\exports\episode_756343df9853`; result was PASS.
- Inspector warnings remain as publication review gates: `speculation_vs_fact`, `critical_view`, 6 segments flagged `needs_human_review`, 1 human-required visual unit, 1 human-required asset, and 7 human-required quotes.
- Created proof draft `data\proofs\ymm4_import\episode_756343df9853\proof.yml` with GUI-dependent checks left `untested`.
- Added `data/proofs/` to `.gitignore` so operator proof artifacts stay local unless explicitly promoted to docs.

## Current Meta-Review And Critical-View Source Entry Slice

- Ran a meta-review gate before implementation. Decision: narrow. P0-A YMM4 GUI import proof remains `request authority`; P0-B critical-view source entry was machine-closeable and scoped to a minimal CLI plus DB relation.
- Added `story_critical_sources` as a SQLite relation from story cluster to article. It supports classifying an existing article as critical or recording a manual runtime source row without committing raw source data to the repo.
- Added `newsroom packet add-critical --story <story_id> --article <article_id>` for existing article classification.
- Added `newsroom packet add-critical --story <story_id> --url <url> --title <title> --source-name <name>` for a manual runtime source. Runtime DB rows are local artifacts, not tracked repo content.
- Packet rebuilds now include critical sources in `NotebookPacket.critical_views`, `sources.json`, `packet.md`, and operator notes.
- Script drafting now prefers critical-view source refs for conflict chapters. Visual, asset, quote, and YMM4 export commands rebuild packets through the same helper, so the critical view remains available downstream.
- Superseded by 2026-06-05 active-source application: the active proof bundle was editorially rebuilt with C1/NIST after this generic capability slice.

## Current Active Critical Source Application

- Selected source: C1 / NIST, `Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile`.
- Runtime source row: `article_bfba4cd5131daa71` in `data\ymm4_import_proof.sqlite`. This is git-ignored runtime state and is not committed.
- Rebuilt packet: `packet_20260603_2de578dcd4b0`; `sources.json` and `packet.md` include NIST under `critical_views`.
- Rebuilt script: `script_d2a46430e084` was reused deterministically; `script_review.md` reports `[ok] critical_view`.
- Rebuilt VisualIR: `visual_eca67c6bd375`; conflict visual unit references `article_bfba4cd5131daa71`.
- Rebuilt review manifests: `data\assets\plan_20260603_faca8ebcbc45` and `data\quotes\plan_20260603_faca8ebcbc45`; quote rows include NIST.
- Rebuilt export bundle: `data\exports\episode_756343df9853`; `source_list.md`, `script_ir.json`, `visual_ir.json`, and `quote_manifest.yml` include the NIST critical source.
- Export inspect result after the P1 broad script review gate: PASS. `critical_view`, `script_todo_skeleton`, and visual/asset/quote `human_required` warnings are gone. Remaining warnings are `speculation_vs_fact` and 6 broad `needs_human_review` segment gates; these are publication/operator review gates, not machine failures and were intentionally not cleared without operator authority.
- YMM4 GUI proof status: passed for CSV import acceptance after the operator added a `ナレーター` character in the target YMM4 environment. This does not prove subtitle placement, overlay safety, or final YMM4 geometry.

## Current P0.5 Approved Materialization State

- CLI: `newsroom script materialize --script <script_id>`.
- Apply CLI: `newsroom script apply-materialization --script <script_id> --draft <path> --require-approved`.
- Approved authority CLI: `newsroom script approve-materialization --script <script_id> --draft <path> --approved-by <operator> --output-root docs\approved_materializations`.
- Approved record apply CLI: `newsroom script apply-approved-materialization --script <script_id> --record docs\approved_materializations\<script_id>.materialization.yml`.
- Active commands used locally: filled the ignored draft from operator-approved suggestions, ran `script approve-materialization`, ran `script apply-approved-materialization`, then rebuilt `export ymm4 --script script_d2a46430e084`.
- Runtime artifact: `data\scripts\script_d2a46430e084\script_materialization.yml`, intentionally git-ignored under `data/scripts/`.
- The active draft now has 6 / 6 non-empty `operator_fill` values and 6 / 6 `approved` statuses because the operator explicitly approved adopting every `operator_fill_suggestion`.
- Approved narration authority: `docs\approved_materializations\script_d2a46430e084.materialization.yml`. It contains approved text, speaker, source refs, critical refs, visual refs, claim type, and human-review flags, and excludes raw article body, private data, runtime DB paths, screenshots, YMM4 geometry, subtitle coordinates, `.ymmp`, and overlay proof.
- Active ScriptIR / refreshed bundle: 0 TODO rows after applying the approved record.
- Active export: `data\exports\episode_756343df9853` rebuilt; `export inspect` passes with `script_todo_skeleton` absent and `critical_view` absent.
- Next state: continue with remaining publication/operator review gates. Do not treat approved narration as subtitle placement, overlay safety, final YMM4 geometry, full `.ymmp`, or publishing proof.

## Current YMM4 GUI Proof Attempt

- Target episode remained `episode_756343df9853`; target CSV was `data\exports\episode_756343df9853\script.csv`.
- The CSV emits speaker `ナレーター` on the spoken rows and the repo speaker config expects `anchor_narration` to map to `ナレーター`.
- YukkuriMovieMaker v4.43.1.0 opened the CSV in `台本編集 / script.csv`, but showed `キャラクターが見つかりませんでした。キャラクターを指定してください。`
- The local YMM4 character selector showed `ゆっくり霊夢`, so the immediate blocker is YMM4 character setup, not CSV encoding.
- Before the speaker fix, the mismatch blocked acceptance and prevented the remaining checks from being observed.
- The operator then created a YMM4 character named `ナレーター`, reran import, and reported that YMM4 recognized and imported the CSV normally.
- The local ignored proof record is `data\proofs\ymm4_import\episode_756343df9853\proof.yml`; it is now set to `import_result: pass` / `decision.status: passed`.
- `TODO[...]` tokens were pronounced because the active CSV contains TODO skeleton script text. That is a script-content state, not an import failure.
- Subtitle placement, overlay safety, final YMM4 geometry, template positioning, and `.ymmp` patch details were not inspected and remain outside newsroom-side acceptance.

## Current P0-A Restart Context Reflection

- Active export: `data\exports\episode_756343df9853`.
- Active script CSV: `data\exports\episode_756343df9853\script.csv`.
- Proof record path: `data\proofs\ymm4_import\episode_756343df9853\proof.yml`, intentionally git-ignored under `data/proofs/`.
- Machine inspect after active C1/NIST rebuild: PASS with `critical_view` absent. Because runtime exports are git-ignored, another checkout can still show older warning state until the active C1/NIST artifacts are regenerated.
- Proof status: passed for CSV import acceptance and handoff-file readability. `data\proofs\ymm4_import\episode_756343df9853\proof.yml` is local evidence and is git-ignored.
- Boundary: newsroom YMM4 GUI proof is CSV import acceptance and handoff-file readability only. Subtitle placement, YMM4 item geometry, template positioning, subtitle band decisions, `.ymmp` patch details, and overlay proof remain downstream NLMYTGen/YMM4-side authority.
- Runtime artifact rule: do not commit `data\ymm4_import_proof.sqlite`, `data\exports\episode_756343df9853`, `data\proofs\...`, or screenshots.
- Valid next action: remaining publication/operator gates or Packet persistence; later downstream subtitle/overlay proof stays outside newsroom scope.

## Handoff Snapshot

- Assistant status: YMM4 manual import proof preparation is implemented and P0-A CSV import acceptance is passed for the active export; P0-B critical-view source entry capability is implemented and applied to the active story with C1/NIST in local runtime artifacts; P0.5-D approved narration was recorded, applied, and rebuilt for the active export; P1 QuoteManifest tightening, the remaining visual/asset/screenshot gate, and the broad script review handoff are implemented for the active path.
- User action: review `docs\script_review_gates\script_d2a46430e084.review.yml` plus the approved materialization text, then return explicit approval or concrete text/claim-type changes. If downstream YMM4 subtitle/overlay work exposes a concrete failure, pass that result separately.
- Assistant next after restart: apply explicit returned script-review decisions or continue to Packet persistence. If runtime artifacts are missing, reapply the tracked approved materialization record, rerun visual/asset/quote suggest, and rebuild export before inspecting.
- What counts as progress next: operator-approved clearing/applying of script review decisions, adding Packet persistence, or handling a concrete returned downstream failure.
- What does not count as progress next: NotebookLM API automation, Inoreader OAuth, GUI/dashboard work, `.ymmp` generation, YouTube upload, NLMYTGen subprocess/path integration, or treating subtitle layout/overlay safety as newsroom-side proof.

## Not Complete Or Not Proven

- The active proof bundle has a selected C1/NIST critical view in this local runtime checkout, but the runtime DB/export artifacts are git-ignored and may need regeneration in a different checkout.
- The active approved narration has a durable tracked authority record, but DB ScriptIR and export artifacts remain git-ignored runtime state and may need reapplication/rebuild in a different checkout.
- Packet persistence is artifact-only; packet records are not stored as first-class DB rows.
- QuoteManifest persistence is artifact-only; quote records are not stored as first-class DB rows.
- QuoteManifest rows are conservative candidates, not legal decisions. Citation-only rows are no longer `human_required`; direct quote, explicit screenshot/source-card, and data-use rows remain operator-review items when present.
- The active export currently has 0 visual/asset/quote `human_required` items, but this is not publishing approval and does not clear broad script `needs_human_review`.
- Broad script review is classified in `docs\script_review_gates\script_d2a46430e084.review.yml`, but the active ScriptIR still has 6 `needs_human_review` flags and the export still carries `speculation_vs_fact`.
- Additional visual cards from PROJECT_SPEC §14 (`version_diff`, `actor_map`, `risk_meter`, `context_stack`, `quote_screenshot`, `neutral_background`) are not implemented.
- YMM4 GUI import proof has passed for CSV import acceptance and handoff-file readability only.
- Subtitle placement and overlay safety are not proven by newsroom's YMM4 import proof.
- YMM4 GUI automation has not been performed and remains out of scope.
- NotebookLM API automation is out of scope.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- M7 series / channel memory and weekly strategy are not implemented.
- Inoreader OAuth / token flow is still deferred.
- External image download and automatic external asset approval remain out of scope.

## Next Recommended Work

1. P1: Operator script review decision apply path.
   Purpose: consume explicit operator decisions from `docs\script_review_gates\script_d2a46430e084.review.yml`, then either clear review flags, adjust text/claim types, or keep warnings.
   Effect: makes broad script review decisions reproducible without treating the assistant as editorial approval authority.

2. P0 support: Preserve or regenerate the active C1/NIST source application, approved materialization, and tightened QuoteManifest if runtime artifacts are missing.
   Purpose: keep `story_20260603_503c39418f15862d` from regressing to a permanent `critical_views` warning in local runtime state.
   Effect: keeps the active export auditable without treating ignored DB/export artifacts as tracked source.

3. P1: Packet persistence.
   Purpose: store packet records as first-class DB rows instead of rebuilding them from cluster/articles at each downstream step.
   Effect: operator edits and critical-view additions can survive across later workflow stages.

4. P2: Source expansion.
   Purpose: add more deliberate source pools without implementing broad crawling or Inoreader OAuth.
   Effect: shortlist quality improves while RSS-first and manual approval boundaries remain intact.

5. P2: M7 series / channel memory.
   Purpose: connect daily production to series history, past claims, and next-episode planning.
   Effect: editorial continuity can be scored and reused across weekly planning.

## Restart Commands

```powershell
git checkout main
git pull --ff-only origin main
.venv\Scripts\Activate.ps1
Get-Content -Raw -Encoding UTF8 docs\HANDOFF.md
python -m pytest -q
git diff --check
if (Test-Path data\exports\episode_756343df9853) {
  newsroom export inspect --episode-dir data\exports\episode_756343df9853
} else {
  Get-Content -Raw -Encoding UTF8 docs\HANDOFF.md
}
```

If `.venv` is missing:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```
