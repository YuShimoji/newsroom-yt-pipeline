# Newsroom Export Fixture For NLMYTGen v1

This document defines the fake newsroom-side export fixture used to answer the
NLMYTGen upstream export delta request. It is a contract/readback artifact, not
a real export, not real source acquisition, and not production or YMM4
readiness.

Fixture path:

```text
samples/_probe/newsroom_handoff/newsroom_export_fixture_v1.json
```

## Boundary

- RSS/source discovery remains newsroom-side.
- NLMYTGen should not scrape articles, fetch missing URLs, infer missing rights,
  download media, or fill provenance gaps.
- Rights, provenance, media availability, source confidence, and human approval
  may require `hold_for_review` or `block_transfer`.
- The fake fixture does not mean real packet approval.
- No production, publication, YMM4 import, subtitle placement, overlay safety,
  final geometry, or `.ymmp` readiness is implied.

## Field Contract

| Field | Owner | Required before | Source within newsroom | Fake fixture value | NLMYTGen expected consumer | Failure behavior | Implementation status | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `episode_id` | newsroom-yt-pipeline | NLMYTGen ingest | export metadata | `episode_fake_nlmytgen_delta_v1` | handoff manifest mapper | fail | fake_only | Replace with real export episode id after packet approval. |
| `title` | newsroom-yt-pipeline | NLMYTGen ingest | episode plan title | Fake upstream export delta for NLMYTGen | operator review header | warn | fake_only | Replace with reviewed title. |
| `topic_summary` | newsroom-yt-pipeline | human review | story packet summary | fake placeholder summary | packet readiness checklist | hold_for_review | fake_only | Replace with human-reviewed summary. |
| `source_notes` | newsroom-yt-pipeline | transfer candidate | NotebookPacket source refs and critical views | two fake source notes without URLs | source/provenance readback | block_transfer | fake_only | Replace with sanitized approved source refs. |
| `provenance` | newsroom-yt-pipeline | transfer candidate | article ledger and packet build readback | all collection actions marked not_performed | provenance gate | block_transfer | policy_only | Populate from real ledger without raw bodies or URLs. |
| `rights_summary` | newsroom-yt-pipeline with human review | transfer candidate; human review | asset and quote manifests plus human review | hold_for_review | rights gate | block_transfer | policy_only | Record reviewed rights state before transfer. |
| `notebooklm_packet` | newsroom-yt-pipeline | NLMYTGen ingest | NotebookPacket builder | fake manual_bridge_seed packet | packet input adapter | fail | fake_only | Supply sanitized packet or transcript seed from an approved story. |
| `script_beats` | newsroom-yt-pipeline | NLMYTGen ingest | ScriptIR segments | two fake stable script beats | script beat mapper | fail | fake_only | Map from ScriptIR segment ids. |
| `visual_plan` | newsroom-yt-pipeline | NLMYTGen ingest | VisualIR and visual_plan.md | two fake visual units | visual adapter mapper | warn | fake_only | Map from VisualIR units. |
| `g28_slot_hints` | newsroom-yt-pipeline for intent only | optional enrichment | visual intent readback | two fake G-28 slot hints | G-28 layout contract mapper | warn | fake_only | Keep geometry authority downstream while passing stable ids. |
| `review_warnings` | newsroom-yt-pipeline | human review | export inspector and review manifests | rights hold and no production readiness | readiness checklist | hold_for_review | fake_only | Replace with real export warnings. |
| `downstream_readiness` | newsroom-yt-pipeline | transfer candidate | export inspector plus human approval state | warn/block_transfer/hold/fail | transfer gate | block_transfer | fake_only | Promote only after real packet review. |
| `export_metadata` | newsroom-yt-pipeline | NLMYTGen ingest | export manifest | fake fixture metadata | manifest provenance | fail | fake_only | Replace with real export metadata. |
| `source_confidence` | newsroom-yt-pipeline | optional enrichment | source role and review metadata | fake_only | operator checklist | warn | fake_only | Replace with reviewed confidence if available. |
| `editorial_priority` | newsroom-yt-pipeline with human review | optional enrichment | editorial planning | medium_fake | operator sorting | warn | fake_only | Replace with real priority after editor selection. |
| `reviewer_notes` | newsroom-yt-pipeline with human review | human review | operator review notes | freeform note placeholder | review intake | hold_for_review | fake_only | Use freeform reviewer notes without prescribed response words. |
| `localization_notes` | newsroom-yt-pipeline | optional enrichment | script/speaker policy | ja-JP fake speaker label policy | speaker/localization mapper | warn | fake_only | Replace with real speaker and locale policy. |
| `channel_metadata` | newsroom-yt-pipeline | optional enrichment | series/channel memory | fake series/package ids | package grouping | warn | fake_only | Replace with approved channel memory metadata. |

## Readback

- Fixture review status: `fake_only_contract_probe`.
- Fixture includes no real URLs, raw article bodies, credentials, media, external
  downloads, screenshots, render outputs, or account data.
- `downstream_readiness.production_ymm4` is `fail`; the fixture is not an import
  proof or production handoff.
- `rights_summary.status` is `hold_for_review`; NLMYTGen must not infer missing
  rights.
- `g28_slot_hints` provides stable intent ids only; final layout geometry remains
  downstream NLMYTGen/YMM4 authority.
