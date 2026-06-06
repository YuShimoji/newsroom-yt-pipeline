# Meta-Review Ledger

Last updated: 2026-06-07

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
- next_allowed_work: P1 QuoteManifest tightening or another concrete publication/operator gate on the materialized script.
- prohibited_work: do not treat this as subtitle placement, overlay safety, final YMM4 geometry, full `.ymmp`, or publishing proof; do not commit runtime DB/export/proof/screenshots.

## Blocked Or Pending

- YMM4 GUI import proof: passed for CSV import acceptance and handoff-file readability on `episode_756343df9853`; downstream subtitle/overlay/final geometry proof remains out of newsroom scope.
- Active critical view: applied locally with C1/NIST. If ignored runtime artifacts are missing in another checkout, reapply the same selected source and rebuild before treating `critical_view` as unresolved.
- Active script materialization: approved record generated and applied for `script_d2a46430e084`; active export inspect is PASS with `script_todo_skeleton` absent.
- Approved narration authority: `docs\approved_materializations\script_d2a46430e084.materialization.yml` is the tracked sanitized authority. Runtime DB/export artifacts remain checkout-local and may need reapply/rebuild elsewhere.
- QuoteManifest human_required noise: P1. This is now a valid active next path because the spoken script is materialized.
- Packet persistence: P1. Current critical-source relation is durable DB input, but full NotebookPacket persistence remains separate.
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
- Tighten QuoteManifest by separating citation-only references from direct quote and screenshot intent.
- Persist NotebookPacket records when operator packet edits must survive rebuilds beyond source classification.
- Reassess VisualIR by final visual effect, not manifest count: composition, density, whitespace, color hierarchy, and eye flow in YMM4.
