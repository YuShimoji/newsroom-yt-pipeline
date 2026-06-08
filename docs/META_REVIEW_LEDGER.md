# Meta-Review Ledger

Last updated: 2026-06-08

This ledger preserves supervision decisions that should survive restarts. Keep it short; do not turn it into a runtime-state duplicate.

## 2026-06-04 Gate

- current_task: resume `newsroom-yt-pipeline` after sync and re-audit P0 blocker/artifact boundaries before normal implementation.
- decision: narrow.
- reason: YMM4 GUI import proof is a real operator authority boundary, but it should not block Codex-owned work on the critical-view source-entry path.
- active_artifact: `data\exports\episode_756343df9853` remains the active YMM4 proof target. It passed machine inspection but is not YMM4 GUI-proven.
- true_blockers: YMM4 GUI import, screen check, and proof YAML completion require operator authority.
- stale_or_false_blockers: `export inspect` review warnings are not machine failure; more proof/docs/readback is not production progress unless an active artifact moves.
- evidence_boundary: `newsroom export inspect` is diagnostic; `data\proofs\ymm4_import\<episode_id>\proof.yml` is operator evidence; `docs/HANDOFF.md` and `docs/RUNTIME_STATE.md` are authority docs; runtime DB/export/proof files are not tracked production source.
- next_allowed_work: use the new `newsroom packet add-critical` path only with a real chosen source, then rebuild downstream artifacts and inspect the resulting export.
- prohibited_work: NLMYTGen subprocess/path integration, NotebookLM API automation, Inoreader OAuth, GUI/dashboard, full `.ymmp`, YouTube upload/publishing, destructive cleanup, raw article body or private data in repo.

## 2026-06-05 Active Critical Source Gate

- current_task: apply the user-selected C1/NIST critical source to `story_20260603_503c39418f15862d`, rebuild downstream artifacts, and inspect the active export.
- decision: continue.
- reason: the source choice was operator/editorial authority, and the remaining work was Codex-owned mechanical registration, rebuild, inspection, and a narrow export rebuild fix.
- active_artifact: `data\exports\episode_756343df9853` remains the active YMM4 proof target. It now includes the NIST critical source and passes machine inspection, but it is still not YMM4 GUI-proven.
- true_blockers: YMM4 GUI import, screen check, and proof YAML completion still require operator authority.
- stale_or_false_blockers: the prior `critical_view` warning is superseded by C1/NIST runtime registration and rebuild; stale export-bundle asset/quote manifests were a machine-closeable implementation bug, not a human blocker.
- evidence_boundary: runtime DB rows and export bundles are evidence/runtime artifacts; docs are restart authority; the new regression test is production code proof for the export rebuild behavior.
- next_allowed_work: operator YMM4 import proof, or targeted fixes if the returned proof/inspect output shows a concrete failure.
- prohibited_work: do not reselect additional critical sources, expand to NotebookLM/Inoreader/GUI/full `.ymmp`/YouTube, or move responsibilities into NLMYTGen shared implementation.

## 2026-06-05 Subtitle Placement Boundary Gate

- current_task: re-audit newsroom / NLMYTGen responsibility boundaries before any subtitle placement or overlay-proof work.
- decision: retire from newsroom active work; keep as downstream authority.
- reason: newsroom may express subtitle-safe intent and no-occlusion requirements, but final YMM4 subtitle placement is a downstream conversion/editor authority.
- newsroom_owns: script text, speaker mapping, source planning, VisualIR/AssetManifest/QuoteManifest planning, `script.csv`, `ymm4_notes.md`, and subtitle-safe / no-occlusion intent.
- nlmytgen_owns: subtitle placement authority, YMM4 item geometry, template positioning, subtitle band decisions, `.ymmp` patch details, and overlay proof.
- ymm4_gui_proof_boundary: newsroom YMM4 GUI proof means CSV import acceptance and handoff-file readability only; it does not prove subtitle layout, subtitle position, overlay safety, or final YMM4 geometry.
- next_allowed_work: update schema notes or handoff docs if a future artifact needs to carry no-occlusion intent as data.
- prohibited_work: do not add subtitle coordinates, YMM4 item geometry, template placement rules, overlay proof, NLMYTGen subprocess/path dependency, shared implementation, GUI/dashboard, full `.ymmp`, or publishing automation to newsroom.

## 2026-06-05 P0-A Restart Context Reflection Gate

- current_task: reflect the latest P0-A restart context into project docs and push without promoting runtime artifacts.
- decision: docs-only.
- reason: machine inspection, boundary readback, and the returned YMM4 GUI attempt changed the restart context, but no code path changed and runtime proof artifacts remain local.
- active_artifact: `data\exports\episode_756343df9853` remains the active YMM4 proof target. A refreshed C1/NIST bundle passes machine inspection with no `critical_view` warning, but ignored runtime exports are checkout-sensitive.
- true_blockers: the first YMM4 GUI attempt failed in YukkuriMovieMaker v4.43.1.0 because exported speaker `ナレーター` was not present in the local YMM4 character setup. Speaker mapping must be aligned and the GUI proof rerun before `decision.status: passed`.
- stale_or_false_blockers: `speculation_vs_fact`, `needs_human_review`, and `human_required` are publication/operator gates, not `export inspect` failure.
- evidence_boundary: tracked docs record restart state; `data\proofs\ymm4_import\episode_756343df9853\proof.yml` is local operator evidence and remains git-ignored.
- next_allowed_work: align YMM4 character setup or regenerate the export with a compatible speaker name, then rerun the GUI proof; assistant handles a targeted fix if proof/inspect returns a concrete machine failure.
- prohibited_work: do not commit runtime DB/export/proof/screenshots, reselect C2+ sources, add subtitle geometry, move overlay proof into newsroom, or expand into GUI/dashboard/full `.ymmp`/publishing automation.

## 2026-06-06 P0-A Validity Check

- current_task: assess the pasted P0-A rerun request and advance the project without overstepping newsroom authority.
- decision: valid but external-environment gated.
- reason: repo/export state is coherent, `configs\speakers.yml` and `script.csv` both use `ナレーター`, and `export inspect` passes with `critical_view` absent. The remaining blocker is the local YMM4 character registry, not encoding, stale export state, or newsroom code.
- active_artifact: `data\exports\episode_756343df9853` remains the active proof target; `data\proofs\ymm4_import\episode_756343df9853\proof.yml` remains local evidence and is not tracked.
- true_blockers: YMM4 must contain a character named `ナレーター`, or there must be an explicit editorial decision to export a speaker name already present in the target YMM4 environment.
- stale_or_false_blockers: the local YMM4 selector showing `ゆっくり霊夢` is not a reason to silently remap newsroom speaker config to `ゆっくり霊夢`.
- evidence_boundary: filesystem inspection found `C:\Users\thank\AppData\Local\YukkuriMovieMaker\v4` but only `temp` content; no safe editable character-registry file was identified in this run.
- next_allowed_work: operator creates/renames a YMM4 character to `ナレーター` through YMM4 UI, then reruns import and updates proof YAML; assistant can update docs after returned proof or implement a targeted export/config option only if explicitly chosen.
- prohibited_work: do not mark proof passed, do not edit unknown YMM4 config files by guesswork, do not change newsroom speaker mapping to `ゆっくり霊夢` just to match one local environment, and do not expand proof scope into subtitle layout or overlay safety.

## 2026-06-07 P0-A Import Acceptance Pass

- current_task: record the returned YMM4 GUI import proof after the target environment gained a `ナレーター` character.
- decision: pass within scope.
- reason: operator created a YMM4 character named `ナレーター`, reran import for `data\exports\episode_756343df9853\script.csv`, and reported that YMM4 recognized the CSV and imported it normally.
- active_artifact: `data\exports\episode_756343df9853` remains the active proof target; `data\proofs\ymm4_import\episode_756343df9853\proof.yml` is updated locally to `import_result: pass` / `decision.status: passed` and remains git-ignored.
- true_blockers: none for newsroom-side CSV import acceptance on this active export.
- stale_or_false_blockers: `TODO[...]` text being pronounced is not an import failure; it is literal TODO skeleton script content.
- evidence_boundary: this pass proves CSV import acceptance and handoff-file readability only. It does not prove subtitle placement, overlay safety, final YMM4 geometry, template positioning, or `.ymmp` patch behavior.
- next_allowed_work: continue publication/operator review gates, P1 QuoteManifest tightening, Packet persistence, or targeted fixes tied to concrete returned failures.
- prohibited_work: do not relabel this as final YMM4 composition proof, and do not commit runtime proof/screenshots.

## 2026-06-07 Post-Proof TODO Skeleton Gate

- current_task: decide whether to continue into P0.5 script materialization or P1 QuoteManifest tightening after P0-A passed.
- decision: supersede P1 until P0.5 is handled.
- reason: the active `script.csv` imports correctly, but all 6 spoken rows still contain literal `TODO[...]` skeleton text. QuoteManifest tightening would operate on placeholder narration and would not move the active publishable artifact.
- active_artifact: `data\exports\episode_756343df9853` remains the active export; `script.csv` and `script_ir.json` are importable but not production-listenable until TODO skeleton text is replaced.
- true_blockers: script materialization requires an operator/editorial fill or a future source-bounded drafting path. Do not auto-invent final narration from sparse source metadata.
- stale_or_false_blockers: the TODO text being pronounced is not a YMM4 import failure and should not invalidate the P0-A proof.
- evidence_boundary: `newsroom export inspect` now reports `script_todo_skeleton` as a warning, not an error. This keeps import acceptance and script-content readiness separate.
- next_allowed_work: P0.5 Script materialization / TODO skeleton replacement, with `source_refs`, speaker mapping, CSV shape, and C1/NIST critical-view coverage preserved.
- prohibited_work: do not proceed to QuoteManifest tightening as the active path while the active spoken script is still 100% TODO skeleton; do not expand into subtitle placement, overlay proof, full `.ymmp`, GUI automation, or publishing.

## 2026-06-07 P0.5 Materialization Draft Path Gate

- current_task: add an operator-editable draft path for the active TODO skeleton script without inventing final narration.
- decision: continue with draft-only materialization.
- reason: the machine-safe step is to expose every TODO segment, source ref, critical ref, speaker, and review flag in an editable artifact. Replacing spoken script text still requires operator-approved content.
- active_artifact: `data\scripts\script_d2a46430e084\script_materialization.yml` is the active ignored draft artifact for filling narration; `data\exports\episode_756343df9853\script.csv` still contains TODO skeleton text.
- true_blockers: operator must fill/approve narration before any replacement step can update `script_ir.json` / `script.csv` and clear `script_todo_skeleton`.
- stale_or_false_blockers: the presence of a materialization draft does not make the active export production-reviewable and must not remove the TODO warning.
- evidence_boundary: `newsroom script materialize --script <script_id>` writes a runtime draft packet under `data/scripts/`; it does not modify DB script rows, export bundles, YMM4 geometry, or downstream proof artifacts.
- next_allowed_work: operator-approved replacement intake for a filled `script_materialization.yml`, followed by script/export rebuild and `export inspect`.
- prohibited_work: do not auto-generate final narration, clear TODO warnings from draft existence alone, or proceed to QuoteManifest tightening as the active path before the spoken script text is materialized.

## 2026-06-07 P0.5-B Replacement Intake Gate

- current_task: add a narrow operator-approved replacement intake for filled materialization drafts.
- decision: implement reject-first apply path; do not run active replacement.
- reason: the active draft has 6 empty `operator_fill` values and 6 `replacement_status: operator_pending` rows. Applying it would silently replace TODO text without operator-approved narration.
- active_artifact: `data\scripts\script_d2a46430e084\script_materialization.yml` remains the active ignored draft; `data\exports\episode_756343df9853\script.csv` and DB ScriptIR still have 6 TODO rows.
- true_blockers: operator must fill all relevant `operator_fill` values and mark replacements approved before the active script can be updated.
- stale_or_false_blockers: a rejected apply attempt is not a system failure; it is the intended safety gate for unfilled/unapproved runtime input.
- evidence_boundary: `newsroom script apply-materialization` can update the DB ScriptIR and refreshed script bundle only after validation passes. It does not rebuild export bundles automatically and does not modify YMM4 proof artifacts.
- next_allowed_work: after operator fills and approves the draft, run the apply command, rebuild the active export, and confirm `script_todo_skeleton` is absent.
- prohibited_work: do not bypass approval, synthesize narration, commit runtime draft/export/proof artifacts, or move to QuoteManifest tightening while the active export still speaks TODO text.

## 2026-06-07 Approved Narration Authority Gate

- current_task: decide where operator-approved narration becomes durable authority after P0.5-B.
- decision: runtime-only replacement proof for this active lane; defer durable approved narration authority to Script/Packet persistence.
- reason: `script_materialization.yml`, DB rows, and export bundles are runtime artifacts and are not committed. Committing ad hoc approved narration now would create a new tracked content authority before script persistence, review status, and copyright/source boundaries are designed.
- active_artifact: `data\scripts\script_d2a46430e084\script_materialization.yml` remains local input. It is not a production authority and is currently unfilled/unapproved.
- true_blockers: a durable authority path must define where approved text lives, how review state is represented, how source refs are retained, and how another checkout reproduces the approved ScriptIR without committing runtime DB/export/proof artifacts.
- stale_or_false_blockers: local runtime application, if later performed, proves the apply path and can update the active export locally, but it does not by itself make the approved narration portable across checkouts.
- next_allowed_work: after operator-approved text exists, either run a local replacement/export proof explicitly marked runtime-only, or implement P1 Script/Packet persistence before treating approved narration as durable project authority.
- prohibited_work: do not commit raw runtime drafts or exports as the canonical script, and do not treat ignored DB state as portable production authority.

## 2026-06-07 P0.5-C Approved Materialization Authority Gate

- current_task: design the smallest portable authority for operator-approved narration without generating narration.
- decision: implement a tracked sanitized approved-materialization record under `docs\approved_materializations\`.
- reason: runtime-only `script_materialization.yml`, DB rows, and export bundles are checkout-sensitive. A small tracked record can carry operator-approved text and metadata without raw article bodies, private data, screenshots, runtime DB paths, or YMM4 geometry.
- active_artifact: the active runtime draft `data\scripts\script_d2a46430e084\script_materialization.yml` is still unfilled/unapproved, so no active approved record or ScriptIR replacement was created.
- true_blockers: operator-approved text is still required before `script_todo_skeleton` can be cleared.
- stale_or_false_blockers: the absence of an approved record for the active script is not a code failure; it is a content authority gate.
- evidence_boundary: approved records are text authority only. They do not prove subtitle placement, overlay safety, final YMM4 geometry, full `.ymmp`, or publishing readiness.
- next_allowed_work: operator fills/approves the draft, generate `docs\approved_materializations\script_d2a46430e084.materialization.yml`, apply it, rebuild the active export, and inspect for `script_todo_skeleton` absence.
- prohibited_work: do not write approved records from unapproved draft rows, do not include raw source data, do not synthesize narration, and do not move QuoteManifest tightening into the active path before the spoken script is materialized.

## 2026-06-07 P0.5-D Approved Materialization Apply Gate

- current_task: apply operator-approved narration to the active ScriptIR and export.
- decision: continue and complete within the approved materialization boundary.
- reason: the operator explicitly approved adopting all 6 `operator_fill_suggestion` values as final narration for this slice, so the assistant could mechanically fill the ignored runtime draft, generate the tracked sanitized record, apply it, rebuild export, and inspect.
- active_artifact: `docs\approved_materializations\script_d2a46430e084.materialization.yml` is now the tracked approved narration authority for `script_d2a46430e084`; `data\exports\episode_756343df9853` is rebuilt in local runtime state.
- true_blockers: none for clearing the active script TODO skeleton. Publication/operator review gates remain: `speculation_vs_fact`, `needs_human_review`, and `human_required` asset/quote/visual items.
- stale_or_false_blockers: `script_todo_skeleton` is no longer active after the approved record apply and export rebuild.
- evidence_boundary: approved materialization is text authority only. Runtime DB/export/proof artifacts remain local evidence and are not committed.
- next_allowed_work: P1 QuoteManifest tightening or another concrete publication/operator gate on the materialized script. Superseded by the P1 QuoteManifest Tightening Gate below for quote-related rows.
- prohibited_work: do not treat this as subtitle placement, overlay safety, final YMM4 geometry, full `.ymmp`, or publishing proof; do not commit runtime DB/export/proof/screenshots.

## 2026-06-07 P1 QuoteManifest Tightening Gate

- current_task: reduce quote-related `human_required` noise without clearing unrelated publication gates.
- decision: implement narrow intent classification.
- reason: active script narration is materialized, and the QuoteManifest builder was treating citation-only `source_refs` as if every segment planned direct quotation. Citation-only evidence rows can be separated from direct quote, screenshot, and data-use intent without adding raw source text.
- active_artifact: `data\exports\episode_756343df9853\quote_manifest.yml` in local runtime state; generated from code and not committed.
- true_blockers: direct quote, screenshot, and data-use rows still require operator review when present.
- stale_or_false_blockers: citation-only text rows are not direct quotes and should not remain `human_required`.
- evidence_boundary: QuoteManifest classification is a review triage aid, not legal approval, source quote authority, subtitle placement proof, YMM4 geometry proof, or publishing readiness.
- next_allowed_work: review remaining screenshot/asset/visual `human_required` items, address broad script review gates with operator authority, or continue to Packet persistence.
- prohibited_work: do not suppress `speculation_vs_fact` or broad `needs_human_review`, do not add raw article body/private/copyright-unclear text, and do not expand into `.ymmp`, overlay proof, YMM4 geometry, or publishing.

## 2026-06-07 P1 Visual/Asset/Screenshot Review Gate

- current_task: classify the remaining visual, asset, and screenshot `human_required` items without clearing unrelated publication warnings.
- decision: implement `replace_with_local_diagram` for the active citation-only facts visual, while preserving explicit source-card/screenshot intent as `human_required`.
- reason: the remaining 3 items were one chain from the facts chapter's default `source_card`: a human-required visual unit, an external screenshot asset, and a screenshot QuoteManifest row. The approved narration cites Microsoft as evidence but does not require direct screenshot/source-card display.
- active_artifact: `data\exports\episode_756343df9853` in local runtime state; regenerated VisualIR/AssetManifest/QuoteManifest/export now have 0 visual/asset/quote `human_required` items.
- true_blockers: broad script `needs_human_review` and `speculation_vs_fact` remain operator/editorial gates.
- stale_or_false_blockers: citation-only source refs are not screenshot intent and should not require external screenshot approval by default.
- next_allowed_work: broad script review gate, Packet persistence, or targeted follow-up if an explicit source-card/screenshot use is requested.
- prohibited_work: do not auto-approve external screenshots, do not suppress `speculation_vs_fact` or broad `needs_human_review`, do not add raw/private/copyright-unclear source material, and do not move subtitle/YMM4 geometry/overlay/publishing into newsroom.

## 2026-06-07 P1 Broad Script Review Gate

- current_task: classify remaining `speculation_vs_fact` and broad `needs_human_review` warnings after visual/asset/quote gates were cleared.
- decision: handoff-only; do not clear warnings or change script text without operator/editorial approval.
- reason: active narration is operator-approved text, but publication review flags require a separate editorial decision. The `speculation_vs_fact` warning is heuristic-only and points to interpretation rows that need source-boundedness review, not an automatic script failure.
- active_artifact: `docs\script_review_gates\script_d2a46430e084.review.yml` tracks segment-level review classification; `docs\approved_materializations\script_d2a46430e084.materialization.yml` remains the approved narration authority.
- true_blockers: operator must approve the six segment review flags, request text changes, or approve an explicit claim-type/speculation treatment before warnings can be cleared.
- stale_or_false_blockers: visual/asset/quote `human_required`, `critical_view`, and `script_todo_skeleton` are no longer active blockers in the current export.
- next_allowed_work: operator script review decision apply path, Packet persistence, or targeted follow-up from a concrete downstream failure.
- prohibited_work: do not bulk-clear `needs_human_review`, do not suppress `speculation_vs_fact`, do not alter approved narration authority without explicit operator approval, and do not add raw/private/copyright-unclear source text or downstream YMM4 geometry/publishing scope.

## 2026-06-07 P1 Operator Script Review Decision Apply Gate

- current_task: apply the returned operator/editorial review decision for the six active script segments.
- decision: apply explicit operator authority and clear the broad script review warnings for this script slice.
- reason: the operator approved the revised narration as source-bounded within the Microsoft official narrative and NIST risk framing, with exact minor edits for facts and takeaway. This is an explicit editorial decision, not assistant auto-approval.
- active_artifact: `docs\approved_materializations\script_d2a46430e084.materialization.yml` is the tracked script text and review-flag authority; `docs\script_review_gates\script_d2a46430e084.review.yml` records the review clearance.
- true_blockers: none for the active newsroom export inspect; `episode_756343df9853` now inspects PASS with no issues found.
- stale_or_false_blockers: prior `speculation_vs_fact` and 6 broad `needs_human_review` warnings are superseded by the returned operator decision for this script slice.
- evidence_boundary: this clearance is not publishing approval, legal approval, YMM4 visual approval, subtitle placement proof, overlay safety proof, or final YMM4 geometry proof.
- next_allowed_work: Packet persistence, preserving/regenerating active runtime artifacts if needed, or targeted follow-up from a concrete downstream failure.
- prohibited_work: do not treat this as permission to change source refs, claim types, subtitle/YMM4 geometry, overlay proof, full `.ymmp`, publishing, or unrelated story/source choices.

## 2026-06-07 P1 Packet Persistence Gate

- current_task: persist NotebookPacket records as first-class runtime DB rows and make downstream rebuilds reuse them.
- decision: implement DB-backed packet persistence with conservative merge behavior.
- reason: packet artifacts under `data\packets` are checkout-local, while downstream script/visual/asset/quote/export steps need a stable packet source that can retain operator packet edits and still pick up required critical-view additions.
- active_artifact: runtime DB table `notebook_packets`; CLI readback via `newsroom packet show`.
- true_blockers: none for the active export path; runtime DB rows are local evidence and may need regeneration in another checkout.
- stale_or_false_blockers: packet persistence is not NotebookLM API automation and does not require committing packet artifacts or raw source bodies.
- evidence_boundary: persisted packets store source refs and operator packet fields only. They do not store raw article bodies, private data, NotebookLM outputs, YMM4 geometry, subtitle placement, overlay proof, `.ymmp`, or publishing approval.
- next_allowed_work: preserve/regenerate active runtime state, source expansion, M7 series/channel memory, or targeted follow-up from a concrete downstream failure.
- prohibited_work: do not expand persistence into raw source storage, NotebookLM automation, YMM4/subtitle geometry, overlay proof, full `.ymmp`, or publishing.

## 2026-06-08 P2 Source Expansion Gate

- current_task: add deliberate source pools while preserving RSS-first and manual-approval boundaries.
- decision: continue with a metadata-only source-pool registry and role propagation.
- reason: source quality can improve by classifying vendor, regulator, standards, independent-analysis, technical-reference, and critical-view candidate sources without adding broad crawling, OAuth, NotebookLM automation, scraping, or auto-adoption.
- active_artifact: `configs\source_pools.yml` plus `configs\sources.yml` feed metadata; active runtime packet/export remain local evidence and still inspect PASS with no issues found before the P2 implementation.
- true_blockers: operator/editorial authority is still required to adopt story sources or promote `critical_view_candidate` sources into active packet critical views.
- stale_or_false_blockers: adding a source pool is not the same as selecting or approving a source, and source-role metadata does not require moving source selection into NLMYTGen.
- next_allowed_work: add/tune source pool metadata deliberately, use manual critical-source selection for chosen candidates, or continue to M7 series/channel memory.
- prohibited_work: do not implement broad crawling, Inoreader OAuth/token flow, NotebookLM API automation, raw article body tracking, automatic critical-view adoption, NLMYTGen subprocess/path dependency, YMM4 geometry, overlay proof, full `.ymmp`, or publishing.

## 2026-06-08 M7 Channel Memory Seed Gate

- current_task: add the first narrow series/channel-memory slice using P2 source-role metadata and P1 packet persistence context.
- decision: continue with tracked sanitized YAML and a schema validator; do not add DB persistence or recommendation automation yet.
- reason: editorial continuity needs a durable record of episode ids, compact recurring claims, source-role coverage, critical-view use, open questions, and follow-up seeds, but it should not select topics or sources automatically.
- active_artifact: `docs\channel_memory\copilot_watch.yml` records `episode_756343df9853` / `story_20260603_503c39418f15862d` / `script_d2a46430e084` / `packet_20260603_2de578dcd4b0`; active runtime export remains PASS with no issues found.
- true_blockers: operator/editorial authority is required before any follow-up seed becomes an actual selected story or before any source candidate is promoted.
- stale_or_false_blockers: a channel-memory seed is not a runtime export dependency and does not require a DB migration, dashboard, or autonomous planning engine.
- next_allowed_work: add a report or append workflow after another episode exists, or manually promote one follow-up seed into a normal RSS-first source/story workflow.
- prohibited_work: do not implement broad crawling, social trend scraping, Inoreader OAuth/token flow, NotebookLM API automation, raw article body tracking, full narration copying, automatic topic/source adoption, NLMYTGen integration, YMM4 geometry, overlay proof, full `.ymmp`, dashboarding, or publishing strategy.

## 2026-06-08 M7-B Series Report Readback Gate

- current_task: make tracked channel memory readable through a minimal CLI report.
- decision: continue with read-only `series report`; do not implement append workflow, recommendations, or source promotion.
- reason: the memory record is now durable, but operators need a safe readback that summarizes continuity without treating follow-up seeds as selected stories.
- active_artifact: `docs\channel_memory\copilot_watch.yml`; runtime active export `data\exports\episode_756343df9853` remains PASS with no issues found.
- true_blockers: operator/editorial authority remains required before any follow-up seed becomes a story or any candidate source is adopted.
- stale_or_false_blockers: default DB missing the active packet is a checkout-local runtime issue and does not block reading tracked channel memory; use `data\ymm4_import_proof.sqlite` when active packet readback is needed.
- next_allowed_work: refine report formatting or add an append workflow only after a second episode or a returned manual story-selection decision exists.
- prohibited_work: do not add autonomous recommendation, broad crawling, social trend scraping, Inoreader OAuth, NotebookLM API automation, raw article body tracking, source candidate auto-promotion, dashboarding, NLMYTGen integration, YMM4 geometry, overlay proof, full `.ymmp`, or publishing strategy.

## 2026-06-08 M7-C Channel Memory Append Workflow Gate

- current_task: add an operator-safe append workflow for approved episode memory.
- decision: narrow.
- reason: the useful machine-closeable step is validating and appending an already approved episode record to tracked channel memory, not generating a second episode or promoting a follow-up seed.
- active_artifact: `docs\channel_memory\copilot_watch.yml` remains the tracked memory record; active runtime export `data\exports\episode_756343df9853` remains runtime evidence and is not rewritten by append.
- true_blockers: operator/editorial authority is required before an episode record can be considered approved input and before any follow-up seed becomes a story.
- stale_or_false_blockers: append workflow support does not require a DB migration, dashboard, runtime packet archive, source candidate promotion, or NotebookLM/YMM4 automation.
- next_allowed_work: use `newsroom series append-episode --series <series_id> --episode-record <path>` when a second approved episode record exists, or backfill legacy source roles only with explicit source authority.
- prohibited_work: do not auto-generate episodes, auto-promote seeds, implement autonomous recommendation, add broad crawling/social trend scraping/Inoreader OAuth/NotebookLM API automation, store raw/private/copyright-unclear text, commit runtime artifacts, or move YMM4 geometry/overlay/full `.ymmp`/publishing into newsroom.

## 2026-06-08 M7-D Source-Role Backfill Gate

- current_task: backfill legacy `copilot_watch` source-role coverage so the series report no longer shows `unclassified / no_pool`.
- decision: narrow.
- reason: Microsoft Blog already has tracked source-pool authority in `configs\sources.yml` / `configs\source_pools.yml`, and the adopted C1/NIST critical view matches the existing `standards_body` pool. This is metadata readback cleanup, not source adoption.
- active_artifact: `docs\channel_memory\copilot_watch.yml` remains the tracked channel-memory record; `data\exports\episode_756343df9853` remains checkout-local runtime evidence.
- true_blockers: none for the metadata backfill.
- stale_or_false_blockers: missing or checkout-sensitive runtime DB/export/proof artifacts do not block tracked channel-memory backfill when the source authority is already in tracked docs/config.
- next_allowed_work: run `series report --series copilot_watch` and validation; later use append only with an operator-approved episode record or run normal source/story selection if a follow-up seed is explicitly chosen.
- prohibited_work: do not promote follow-up seeds, adopt new source candidates, crawl broadly, add NotebookLM/YMM4 automation, commit runtime artifacts, store raw article body/private text, or move YMM4 geometry/overlay/full `.ymmp`/publishing into newsroom.

## Blocked Or Pending

- YMM4 GUI import proof: passed for CSV import acceptance and handoff-file readability on `episode_756343df9853`; downstream subtitle/overlay/final geometry proof remains out of newsroom scope.
- Active critical view: applied locally with C1/NIST. If ignored runtime artifacts are missing in another checkout, reapply the same selected source and rebuild before treating `critical_view` as unresolved.
- Active script materialization: approved record generated and applied for `script_d2a46430e084`; active export inspect is PASS with `script_todo_skeleton` absent.
- Approved narration authority: `docs\approved_materializations\script_d2a46430e084.materialization.yml` is the tracked sanitized authority. Runtime DB/export artifacts remain checkout-local and may need reapply/rebuild elsewhere.
- Broad script review: applied in `docs\script_review_gates\script_d2a46430e084.review.yml`; `needs_human_review` and `speculation_vs_fact` are cleared for this script slice only after explicit operator/editorial decision.
- QuoteManifest human_required noise: citation-only source refs are tightened; after the visual/asset/screenshot gate, active quote rows are 10 citation-only and 0 screenshot `human_required`.
- Packet persistence: implemented. Current critical-source relation remains durable DB input, and NotebookPacket rows now persist sanitized packet state in the runtime DB.
- Channel memory seed: implemented for `copilot_watch` as tracked sanitized YAML with validation. Follow-up candidates remain seeds, not approved story selections.
- Series report readback: implemented as read-only CLI output. It does not append episodes, promote sources, or select stories.
- Channel memory append workflow: implemented as file-based `series append-episode`. It appends only validated approved episode records and does not generate episodes, promote seeds, select sources, or mutate runtime artifacts.
- VisualIR-to-final-look gap: keep evaluating whether VisualIR changes affect actual YMM4 composition, density, whitespace, and eye flow.

## Standing Cautions

- Do not count proof/docs/readback growth as production value.
- Keep NLMYTGen as schema handoff only: CSV, JSON, Markdown.
- Keep subtitle placement authority downstream: newsroom can carry subtitle-safe intent, but NLMYTGen/YMM4-side tooling owns final subtitle geometry and overlay proof.
- Separate operator creative/GUI authority from machine-verifiable tasks.
- Do not keep expanding docs around the failed YMM4 import proof unless the artifact state changes.
- Case-specific runtime evidence can inform generic capability, but it is not the generic capability's authority by itself.

## Improvement Ideas

- Generalize critical source entry only when more cases need it; do not turn this C1/NIST runtime evidence into a broader source-selection authority by itself.
- Tighten remaining review surfaces by separating concrete visual/source-card use from broad publication concerns.
- Persist NotebookPacket records when operator packet edits must survive rebuilds beyond source classification.
- Reassess VisualIR by final visual effect, not manifest count: composition, density, whitespace, color hierarchy, and eye flow in YMM4.
