# Channel Memory

This directory stores sanitized, tracked editorial continuity records. A record
connects an approved episode to a series history, recurring claims, source-role
coverage, critical-view use, open questions, and next-episode planning seeds.

Channel memory is not a recommendation engine. It does not fetch sources,
promote source candidates, automate NotebookLM, create YMM4 geometry, or approve
publishing.

## Readback

Use the CLI to inspect tracked memory without changing runtime DB/export state:

```powershell
.venv\Scripts\python.exe -m newsroom.cli.main series report --series copilot_watch
```

The report includes episode ids, story/script/packet ids, source-role coverage,
critical views, compact claims, open questions, and follow-up seeds. Follow-up
seeds are explicitly not approved stories.

## Source-Role Backfill

Backfill source-role coverage only from explicit source authority already present
in tracked config or approved episode context. For the active `copilot_watch`
record, Microsoft Blog uses `microsoft_official` / `vendor_official` from
`configs/sources.yml` and `configs/source_pools.yml`, and the adopted C1/NIST
critical view uses the existing `standards_body` pool because it is a standards
and trustworthiness framework lens.

Do not use channel memory backfill to adopt new sources, promote follow-up
seeds, crawl broadly, store raw article text, or create publishing/YMM4 proof.

## Append Workflow

Append only operator/editorial-approved episode memory. The append workflow is
for recording a completed newsroom handoff, not for selecting a story or
promoting a follow-up seed.

```powershell
.venv\Scripts\python.exe -m newsroom.cli.main series append-episode --series copilot_watch --episode-record path\to\episode_record.yml
```

The command validates the existing memory and the incoming record, rejects
duplicate `episode_id`, `story_id`, `script_id`, or `packet_id` values, writes
only the tracked memory YAML, and leaves runtime DB/export/proof artifacts
untouched.

Episode records may be either a bare episode mapping or a wrapper with:

```yaml
artifact_type: channel_memory_episode
schema_version: 1
```

Required episode fields:

- `episode_id`
- `story_id`
- `script_id`
- `packet_id`
- `topic`
- `status`

Supported review fields:

- `source_roles_used`
- `critical_views_used`
- `claims_made`
- `open_questions`
- `followup_candidates`

`followup_candidates[*].status` must remain `seed`; an append record cannot turn
a seed into an approved story.

## Record Shape

Use one YAML file per series:

```text
docs\channel_memory\<series_id>.yml
```

Each record must contain:

- `artifact_type: channel_memory`
- `schema_version: 1`
- `series_id`, `title`, `status`
- `episodes`, each with `episode_id`, `story_id`, `script_id`, `packet_id`, `topic`, `status`
- optional `source_roles_used`, `critical_views_used`, `claims_made`, `open_questions`, and `followup_candidates`

## Not Allowed

Do not put these in channel memory records:

- raw source article body
- private data
- full approved narration text
- runtime DB paths
- screenshots or proof paths
- YMM4 geometry, subtitle coordinates, `.ymmp` details, or overlay proof data
