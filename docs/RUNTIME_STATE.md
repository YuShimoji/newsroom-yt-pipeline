# Runtime State

Last updated: 2026-06-15

## Sync Point

- Remote sync handoff on 2026-06-15: prepared the local context for `origin/main` after the boundary audit and QuoteManifest naming slice. Before this handoff update, `main` was clean at `14c1e4f`, `HEAD...origin/main` was `4 0`, and the four local commits were `baabcd6`, `d7f2bd7`, `d90452a`, and `14c1e4f`. The next terminal should `git pull --ff-only origin main`, read `docs\HANDOFF.md`, `docs\RUNTIME_STATE.md`, `docs\DEVELOPMENT_PRACTICES.md`, and `artifacts\ARTIFACTS.md`, then rerun local validation before continuing. No runtime DB/export/proof/screenshot, YMM4 GUI automation, NotebookLM live/API automation, `.ymmp`, YouTube, or raw source body was promoted.
- `autonomous_foundation_run` checkpoint on 2026-06-15: started on `main` at `e6b81ab` with `HEAD...origin/main` = `0 0`. The checkout already had local docs-view changes from the prior local documentation task (`.docs-view/`, `docs/index.md`, `mkdocs.yml`, `tools/generate-doc-nav.ps1`, and `.gitignore`); these were docs/tooling only, contained no code/runtime/generated artifact/secret/raw news data, and were adopted/tightened rather than discarded. No pull was run because the branch was already in sync and the worktree was intentionally dirty.
- Governance authority added: `docs/DEVELOPMENT_PRACTICES.md` now records the source-of-truth hierarchy, NEXT_ACTION lanes, default no-op rule, preview gates, newsroom/NLMYTGen boundary, human approval gates, evidence discipline, repository hygiene, and the local docs-view boundary. This document is development-practice authority only; it does not replace `docs/PROJECT_SPEC.md`, `docs/RUNTIME_STATE.md`, YMM4 proof procedure, or operator/editorial approval.
- Local docs view tightened for current docs: `mkdocs.yml` / `.docs-view/` now include `docs/DEVELOPMENT_PRACTICES.md`, `docs/NLMYTGEN_BOUNDARY.md`, and the 2026-06-14 project-rule alignment record. `tools/generate-doc-nav.ps1` continues to ignore `.git`, `.venv`, `.docs-view`, `.mkdocs-site`, `data`, `.claude`, and other generated or non-source directories while printing a review-only nav candidate.
- Second-stage slice selected: `critical_view_source_path`, kept to a small readback/inspect addition. Added `newsroom packet critical-list --story <story_id> [--format markdown|json]` to list DB-recorded critical-view sources for a story without printing source URLs, raw bodies, OPML, tokens, screenshots, or private traces. The readback is diagnostic and does not adopt sources, rebuild packets, clear `human_required`, or assert editorial/legal approval.
- Boundary audit after the completed `autonomous_foundation_run`: confirmed the two local commits remained split as `baabcd6 docs: add development practice docs view` and `d7f2bd7 feat: add critical source readback`; the branch was `main`, `HEAD` was `d7f2bd7`, `HEAD...origin/main` was `2 0`, and the worktree was clean before audit corrections. The docs-view source boundary is `.docs-view/` thin wrappers plus `mkdocs.yml`; generated HTML remains `.mkdocs-site/`. Reviewable local artifacts are tracked in `artifacts/ARTIFACTS.md` rather than in runtime export directories.
- Validation after the boundary-audit correction: `.venv\Scripts\python.exe -m pytest tests\test_critical_sources.py -q` -> 8 passed; `.venv\Scripts\python.exe -m pytest -q` -> 116 passed; `git diff --check` -> passed; `powershell -ExecutionPolicy Bypass -File tools\generate-doc-nav.ps1` listed `artifacts/ARTIFACTS.md` under Artifacts; `.venv\Scripts\python.exe -m mkdocs build --strict` -> passed; synthetic temp-DB smoke for `packet critical-list --format json` returned one critical view and `url_field_present: false`.
- Follow-up `quote_manifest_tightening` slice: QuoteManifest text rows for ordinary attribution now use `review_level: source_reference` while keeping `approval_state: citation_only`; source-card or quote-screenshot rows now use `review_level: screenshot_candidate`. Direct quote and data-use rows remain `human_required`. This is a schema/readback naming clarification only and does not clear legal, publication, screenshot, or data-use gates.
- Validation after the 2026-06-15 QuoteManifest naming slice: `.venv\Scripts\python.exe -m pytest tests\test_quote_manifest.py tests\test_ymm4_export.py -q` -> 16 passed; `.venv\Scripts\python.exe -m pytest -q` -> 116 passed; `git diff --check` -> passed; `.venv\Scripts\python.exe -m mkdocs build --strict` -> passed.
- Validation for this checkpoint: `.venv\Scripts\python.exe -m pytest tests\test_critical_sources.py -q` -> 8 passed; `.venv\Scripts\python.exe -m pytest -q` -> 116 passed; `git diff --check` -> passed; `powershell -ExecutionPolicy Bypass -File tools\generate-doc-nav.ps1` produced the expected candidate nav; `.venv\Scripts\python.exe -m mkdocs build --strict` -> passed after stopping the prior local MkDocs server that was holding `.mkdocs-site\mkdocs-serve-8000.err.log`; a synthetic temp-DB CLI smoke for `packet critical-list --format json` returned one `critical_view_candidate` row with no URL field.
- Boundaries preserved in this checkpoint: no YMM4 GUI automation, no NotebookLM live execution/API automation, no Inoreader OAuth, no broad crawling, no `.ymmp` generation, no YouTube upload/publishing, no runtime DB/export/proof/screenshot commit, no source adoption beyond synthetic test/readback fixtures, and no weakening of rights or approval warnings.
- Docs-only handoff inventory record on 2026-06-10: recorded the prior read-only inventory / authority check in `docs\verification\NEWSROOM-HANDOFF-INVENTORY-2026-06-10.md`. The active export folder `data\exports\episode_756343df9853` exists and inspected PASS / `No issues found`; series readback still shows Microsoft Blog as `vendor_official / microsoft_official / official`, NIST as `standards_body / standards_body / official`, no `unclassified / no_pool`, and follow-up candidates as `seed`. Handoff readiness remains `partial` until a human supplies copy-in, read-only path reference, or hold authority for NLMYTGen. No generated export artifact, runtime DB, proof, screenshot, YMM4 geometry, `.ymmp`, render, production, publishing output, NLMYTGen integration, source adoption, seed promotion, NotebookLM automation, Inoreader OAuth, or broad crawling work was committed.
- No-op restart check on 2026-06-09: `git checkout main` and `git pull --ff-only origin main` confirmed the checkout was already up to date at `1296b8e docs: backfill channel memory source roles`; `HEAD...origin/main` was `0 0`; the working tree was clean; `git status --porcelain=v1 --untracked-files=all` returned no files. Required readback stayed healthy: `newsroom series report --series copilot_watch` showed Microsoft Blog as `vendor_official / microsoft_official / official`, NIST as `standards_body / standards_body / official`, no `unclassified / no_pool`, and follow-up candidates still marked as `seed`; `newsroom export inspect --episode-dir data\exports\episode_756343df9853` returned PASS / `No issues found.`; channel-memory tests passed with 16 tests; `git diff --check` passed. No M7-D reimplementation, seed promotion, source adoption, broad crawling, NotebookLM/YMM4 automation, runtime artifact commit, or downstream subtitle/YMM4 geometry work was done.
- Current sync base HEAD before this slice: `4b83531 feat: integrate M6 artifacts into YMM4 export`.
- Current pulled HEAD before this docs-only handoff refresh: `8c3bc27 docs: refresh handoff restart point`.
- Remote status at restart: `HEAD...origin/main` was `0 0`.
- Cross-terminal handoff confirmation after M7-C on 2026-06-08: latest implementation commit before this docs-only refresh is `0322d37 feat: add channel memory append workflow`, `HEAD...origin/main` was `0 0`, the working tree was clean, channel-memory tests passed with 15 tests, full `.venv\Scripts\python.exe -m pytest -q` passed with 106 tests, active `series report --series copilot_watch` read back one active episode with follow-up candidates still marked as seeds, active `packet show --story story_20260603_503c39418f15862d` read back `packet_20260603_2de578dcd4b0` from `data\ymm4_import_proof.sqlite`, and active `export inspect --episode-dir data\exports\episode_756343df9853` was PASS with no issues found.
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
- P1 QuoteManifest tightening on 2026-06-07: citation-only source-ref rows used `review_level: citation_only` / `approval_state: citation_only` at that checkpoint, while direct quote, screenshot, and data-use intent remained `human_required`. The 2026-06-15 schema naming slice supersedes that review-level label with `review_level: source_reference` for ordinary source references. Active `quote_manifest.yml` readback at the 2026-06-07 checkpoint: 11 rows total, 10 citation-only rows, 1 screenshot human_required row, 5 C1/NIST rows retained as `source_role: critical_view`.
- Active export inspect after P1 QuoteManifest tightening: PASS with `critical_view` absent and `script_todo_skeleton` absent. The M6 handoff warning dropped from 13 to 3 total human_required visual/asset/quote items: 1 asset, 1 quote screenshot, and 1 visual unit. `speculation_vs_fact` and 6 `needs_human_review` segment warnings remain as publication/operator gates.
- Validation after P1 QuoteManifest tightening: targeted quote/export tests -> 21 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 74 passed; `git diff --check` -> passed.
- P1 remaining visual/asset/screenshot review gate on 2026-06-07: the remaining 3 `human_required` items were all source-card screenshot effects on the facts chapter. The active decision was `replace_with_local_diagram`: citation-only facts now use `claim_evidence_card`, while explicit `source_card` / `screenshot` / `quote_screenshot` intent still remains `human_required`.
- Active export inspect after the P1 visual/asset/screenshot gate: PASS with `critical_view` absent and `script_todo_skeleton` absent. VisualIR has 6 units and 0 `human_required`; AssetManifest has 6 local-template candidates and 0 `human_required`; QuoteManifest has 10 citation-only text rows, 0 screenshot rows, and retains 5 C1/NIST critical-view rows. Remaining warnings are only `speculation_vs_fact` and 6 broad `needs_human_review` segment gates.
- Validation after the P1 visual/asset/screenshot gate: targeted visual/asset/quote/export tests -> 33 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 77 passed; `git diff --check` -> passed.
- P1 broad script review gate on 2026-06-07: added `docs\script_review_gates\script_d2a46430e084.review.yml` as a tracked handoff artifact for the remaining script publication gates. The review gate classifies all 6 segments as `operator_approval_required`, keeps interpretation rows under `speculation_vs_fact` / publication-review caution, and makes no script text or review-flag changes.
- Active export inspect after the P1 broad script review gate: PASS with `critical_view`, `script_todo_skeleton`, and visual/asset/quote `human_required` absent. Remaining warnings intentionally stay: `speculation_vs_fact` and 6 broad `needs_human_review` segment gates.
- Validation after the P1 broad script review gate: targeted script/export tests -> 23 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 78 passed; `git diff --check` -> passed.
- P1 operator script review decision apply path on 2026-06-07: operator/editorial decision approved all 6 revised segments as source-bounded narration within the Microsoft official narrative and NIST risk framing. Facts and takeaway minor edits were applied to `docs\approved_materializations\script_d2a46430e084.materialization.yml`; intro/context/conflict/impact kept the approved candidate text; all 6 approved record rows now carry `human_review_required: false`.
- Active export inspect after the P1 operator script review decision apply path: PASS with no issues found. `critical_view`, `script_todo_skeleton`, visual/asset/quote `human_required`, `speculation_vs_fact`, and broad `needs_human_review` warnings are absent for `episode_756343df9853`.
- Boundary after script review clearance: this is source-bounded script review clearance only. It is not publishing approval, legal approval, YMM4 visual approval, subtitle placement proof, overlay safety proof, or final YMM4 geometry proof.
- Validation after the P1 operator script review decision apply path: targeted materialization/export/inspector tests -> 38 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 81 passed; `git diff --check` -> passed with a CRLF-to-LF normalization warning for the approved materialization YAML.
- P1 Packet persistence on 2026-06-07: added first-class runtime DB persistence for sanitized NotebookPacket records. `packet build` now upserts a packet row, `packet show` reads persisted packets by packet id or story id, and downstream helpers prefer persisted packet state while appending newly required `story_critical_sources` critical refs.
- Packet persistence boundary: persisted packets store source refs, timeline, glossary, questions, format hint, export dir, and timestamps. They do not store raw article bodies, private data, NotebookLM outputs, YMM4 geometry, subtitle placement, overlay proof, `.ymmp`, or publishing approval.
- Validation after the P1 Packet persistence slice: targeted packet/storage tests -> 13 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 85 passed; `git diff --check` -> passed. Active runtime packet readback: `packet_20260603_2de578dcd4b0`, 1 primary source, 1 C1/NIST critical view. Rebuilt active export remains PASS with no issues found.
- P2 Source expansion on 2026-06-08: added a metadata-only source pool registry at `configs\source_pools.yml` and allowed feed rows in `configs\sources.yml` to reference pools. Source roles are limited to `vendor_official`, `regulator_public`, `standards_body`, `independent_analysis`, `technical_reference`, and `critical_view_candidate`.
- Source expansion boundary: RSS feed loading applies pool defaults to `SourceFeed`, RSS ingestion carries `source_role` / `source_pool_id` to Article rows, and NotebookPacket `SourceRef` rows preserve that metadata. `critical_view_candidate` rows are not auto-adopted into packet critical views; operator/manual selection remains required.
- Validation after the P2 Source expansion slice: targeted source/storage/packet tests -> 16 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 91 passed; `git diff --check` -> passed. Active runtime packet readback remained `packet_20260603_2de578dcd4b0` with 1 primary source and 1 C1/NIST critical view. Active export remained PASS with no issues found.
- M7 channel memory seed on 2026-06-08: added `docs\channel_memory\copilot_watch.yml` and `newsroom.editorial.channel_memory` as the first narrow series/channel-memory slice. The record links the active episode/story/script/packet to compact claim summaries, source-role coverage, NIST critical-view use, open questions, and follow-up seeds without raw article bodies, private data, full narration text, runtime DB paths, screenshots, YMM4 geometry, subtitle coordinates, `.ymmp`, or overlay proof. Validation: channel-memory tests -> 5 passed; active export inspect remained PASS with no issues found.
- M7-B series report / channel memory readback on 2026-06-08: added `newsroom series report --series <series_id>` and a report renderer for `ChannelMemory`. The report is read-only and shows series title/status, episode/story/script/packet ids, source-role coverage, critical views, compact claims, open questions, and follow-up seeds, while explicitly stating that seeds are not approved stories. Validation: channel-memory CLI tests -> 7 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 98 passed; `git diff --check` -> passed; active export inspect remained PASS / no issues found.
- M7-C channel memory append workflow on 2026-06-08: added `newsroom series append-episode --series <series_id> --episode-record <path>` as a read/validate/write path for already approved episode memory. It rejects duplicate episode/story/script/packet ids, rejects forbidden raw/private/runtime/YMM4/proof fields, preserves follow-up candidates as `seed`, and does not mutate runtime DB/export/proof state.
- M7-D source-role backfill on 2026-06-08: backfilled the active legacy `docs\channel_memory\copilot_watch.yml` source-role coverage from explicit existing authority. Microsoft Blog `article_f4124bbb866ef6b0` now uses `microsoft_official` / `vendor_official`; NIST `article_bfba4cd5131daa71` now uses `standards_body` / `standards_body` in both source-role coverage and critical-view readback. No follow-up seed was promoted, no new source was adopted, and no runtime DB/export/proof artifact was committed. Validation: channel-memory tests -> 16 passed; full `.venv\Scripts\python.exe -m pytest -q` -> 107 passed; `git diff --check` -> passed; active export inspect remained PASS / no issues found.

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
- P1 broad script review gate: done for the active path after explicit operator/editorial decision. Remaining script warnings are cleared for `script_d2a46430e084` through the tracked approved materialization and review gate artifacts.
- P1 Packet persistence: done. NotebookPacket rows are persisted in the runtime DB and reused by downstream rebuild helpers.
- P2 Source expansion: done for the deliberate source-pool registry and source-role propagation. It is metadata-only and does not implement broad crawling, Inoreader OAuth, NotebookLM automation, scraping, or auto source adoption.
- M7 channel memory seed: done for the first tracked sanitized series memory record and schema validator. It records editorial continuity and next-episode seeds only; no autonomous recommendation, crawling, NotebookLM automation, dashboard, or publishing strategy is implemented.
- M7-B series report readback: done. `newsroom series report --series copilot_watch` renders tracked memory for human inspection without appending episodes, promoting sources, mutating runtime artifacts, or selecting stories.
- M7-C channel memory append workflow: done. `newsroom series append-episode --series copilot_watch --episode-record <path>` appends validated approved episode memory without generating episodes, promoting seeds, or writing runtime artifacts.
- M7-D source-role backfill: done for the active legacy `copilot_watch` memory record. The report no longer shows `unclassified / no_pool` for Microsoft Blog or NIST, and the backfill is metadata-only.
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
- Export inspect result after the P1 operator script review decision apply path: PASS with no issues found. `critical_view`, `script_todo_skeleton`, visual/asset/quote `human_required`, `speculation_vs_fact`, and broad `needs_human_review` warnings are absent after the explicit operator/editorial decision was applied.
- YMM4 GUI proof status: passed for CSV import acceptance after the operator added a `ナレーター` character in the target YMM4 environment. This does not prove subtitle placement, overlay safety, or final YMM4 geometry.

## Current P0.5 Approved Materialization State

- CLI: `newsroom script materialize --script <script_id>`.
- Apply CLI: `newsroom script apply-materialization --script <script_id> --draft <path> --require-approved`.
- Approved authority CLI: `newsroom script approve-materialization --script <script_id> --draft <path> --approved-by <operator> --output-root docs\approved_materializations`.
- Approved record apply CLI: `newsroom script apply-approved-materialization --script <script_id> --record docs\approved_materializations\<script_id>.materialization.yml`.
- Active commands used locally: filled the ignored draft from operator-approved suggestions, ran `script approve-materialization`, ran `script apply-approved-materialization`, then later reapplied the revised approved materialization authority after the operator script-review decision and rebuilt VisualIR/AssetManifest/QuoteManifest/export.
- Runtime artifact: `data\scripts\script_d2a46430e084\script_materialization.yml`, intentionally git-ignored under `data/scripts/`.
- The active draft now has 6 / 6 non-empty `operator_fill` values and 6 / 6 `approved` statuses because the operator explicitly approved adopting every `operator_fill_suggestion`.
- Approved narration authority: `docs\approved_materializations\script_d2a46430e084.materialization.yml`. It contains approved text, speaker, source refs, critical refs, visual refs, claim type, and operator-cleared human-review flags, and excludes raw article body, private data, runtime DB paths, screenshots, YMM4 geometry, subtitle coordinates, `.ymmp`, and overlay proof.
- Active ScriptIR / refreshed bundle: 0 TODO rows after applying the approved record.
- Active export: `data\exports\episode_756343df9853` rebuilt; `export inspect` passes with no issues found.
- Next state: continue to Packet persistence or explicit downstream YMM4 visual/subtitle proof if requested. Do not treat approved narration or script-review clearance as subtitle placement, overlay safety, final YMM4 geometry, full `.ymmp`, legal approval, or publishing proof.

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
- Valid next action: Packet persistence or explicit downstream YMM4 visual/subtitle proof if requested; later downstream subtitle/overlay proof stays outside newsroom scope.

## Handoff Snapshot

- Assistant status: YMM4 manual import proof preparation is implemented and P0-A CSV import acceptance is passed for the active export; P0-B critical-view source entry capability is implemented and applied to the active story with C1/NIST in local runtime artifacts; P0.5-D approved narration was recorded, applied, and rebuilt for the active export; P1 QuoteManifest tightening, the remaining visual/asset/screenshot gate, the broad script review decision apply path, Packet persistence, P2 source-pool metadata, M7 channel-memory seed, M7-B readback, M7-C append workflow, and M7-D source-role backfill are implemented for the active path.
- User action: no active newsroom-side operator review decision is pending for `episode_756343df9853`. Continue only after one explicit input is supplied: an approved second episode record YAML full path, a selected follow-up seed, or a concrete downstream failure log/artifact/proof path.
- Assistant next after restart: if an approved episode record is supplied, use `newsroom series append-episode --series copilot_watch --episode-record <path>` and validate; if a follow-up seed is selected, return to normal source/story selection without auto-adoption; if a downstream failure is supplied, keep newsroom handling limited to CSV/JSON/Markdown handoff and source/script/manifest consistency. If runtime artifacts are missing, rebuild/persist the packet, reapply the tracked approved materialization record, rerun visual/asset/quote suggest, and rebuild export before inspecting.
- What counts as progress next: active runtime preservation, next scoped backlog implementation, or handling a concrete returned downstream failure.
- What does not count as progress next: NotebookLM API automation, Inoreader OAuth, GUI/dashboard work, `.ymmp` generation, YouTube upload, NLMYTGen subprocess/path integration, or treating subtitle layout/overlay safety as newsroom-side proof.

## Not Complete Or Not Proven

- The active proof bundle has a selected C1/NIST critical view in this local runtime checkout, but the runtime DB/export artifacts are git-ignored and may need regeneration in a different checkout.
- The active approved narration has a durable tracked authority record, but DB ScriptIR and export artifacts remain git-ignored runtime state and may need reapplication/rebuild in a different checkout.
- Packet persistence is implemented in the runtime DB, but runtime DB rows are not committed and may need regeneration in another checkout.
- Source pools classify feeds and packet refs, but source candidates are not automatically adopted into story packets or critical views.
- QuoteManifest persistence is artifact-only; quote records are not stored as first-class DB rows.
- QuoteManifest rows are conservative candidates, not legal decisions. Ordinary source-reference rows use `review_level: source_reference` and `approval_state: citation_only`; direct quote, explicit screenshot/source-card, and data-use rows remain operator-review items when present.
- The active export currently has 0 visual/asset/quote `human_required` items and 0 broad script `needs_human_review` flags, but this is not publishing approval.
- Broad script review is applied in `docs\script_review_gates\script_d2a46430e084.review.yml`; it clears `speculation_vs_fact` and broad `needs_human_review` for this script slice only, not legal/publishing/YMM4 visual/subtitle/overlay approval.
- Additional visual cards from PROJECT_SPEC §14 (`version_diff`, `actor_map`, `risk_meter`, `context_stack`, `quote_screenshot`, `neutral_background`) are not implemented.
- YMM4 GUI import proof has passed for CSV import acceptance and handoff-file readability only.
- Subtitle placement and overlay safety are not proven by newsroom's YMM4 import proof.
- YMM4 GUI automation has not been performed and remains out of scope.
- NotebookLM API automation is out of scope.
- Full `.ymmp` generation is out of scope.
- YouTube upload and publishing are out of scope.
- M7 has the first tracked channel-memory seed, validator, and read-only series report. Episode append workflow, weekly strategy, source promotion, and autonomous planning are not implemented.
- Inoreader OAuth / token flow is still deferred.
- External image download and automatic external asset approval remain out of scope.

## Next Recommended Work

1. P0 support: Preserve or regenerate the active C1/NIST source application, persisted packet, approved materialization, and tightened QuoteManifest if runtime artifacts are missing.
   Purpose: keep `story_20260603_503c39418f15862d` from regressing to a permanent `critical_views` warning in local runtime state.
   Effect: keeps the active export auditable without treating ignored DB/export artifacts as tracked source.

2. M7 next: use append only when another operator-approved episode memory record exists, or run the normal source/story workflow if a follow-up seed is explicitly selected.
   Purpose: keep channel memory as approved continuity, not automatic planning.
   Effect: future series reports stay readable without turning seeds into selected stories.

3. Downstream failure intake: act only when the operator provides a concrete failure description plus the full log/artifact/proof path.
   Purpose: keep newsroom-side work tied to reproducible CSV/JSON/Markdown handoff, source, script, or manifest consistency evidence.
   Effect: prevents subtitle placement, overlay proof, full `.ymmp`, or publishing scope from drifting into newsroom without an owned artifact boundary.

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
