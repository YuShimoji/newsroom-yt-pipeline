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
