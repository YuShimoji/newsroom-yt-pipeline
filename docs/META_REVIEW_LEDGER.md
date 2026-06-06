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

## Blocked Or Pending

- YMM4 GUI import proof: passed for CSV import acceptance and handoff-file readability on `episode_756343df9853`; downstream subtitle/overlay/final geometry proof remains out of newsroom scope.
- Active critical view: applied locally with C1/NIST. If ignored runtime artifacts are missing in another checkout, reapply the same selected source and rebuild before treating `critical_view` as unresolved.
- QuoteManifest human_required noise: P1. Do not let it consume P0 unless the active export path is already moving.
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
