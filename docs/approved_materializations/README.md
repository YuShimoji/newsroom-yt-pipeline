# Approved Materializations

This directory is the tracked authority root for sanitized operator-approved script materialization records.

Approved records are portable across checkouts. They are intentionally separate from runtime artifacts under `data\scripts`, runtime DB rows, export bundles, proof files, screenshots, and downstream YMM4 geometry.

## Record Shape

Use one file per script:

```text
docs\approved_materializations\<script_id>.materialization.yml
```

Each record must contain:

- `artifact_type: approved_script_materialization`
- `script_id`
- `episode_plan_id`
- `story_cluster_id`
- optional `episode_id`
- `format`
- `status: approved`
- `approval.approved_by`
- `approval.approved_at`
- optional `approval.approval_note`
- one `segments` row per approved TODO replacement, containing `segment_id`, `speaker`, `approved_text`, `source_refs`, `critical_refs`, `visual_refs`, `claim_type`, `human_review_required`, and `replacement_status: approved`

## Not Allowed

Do not put these in approved records:

- raw source article body
- private data
- source catalogs with URLs or article bodies
- runtime DB paths
- screenshots or proof paths
- YMM4 geometry, subtitle coordinates, `.ymmp` patch details, or overlay proof data

## Workflow

1. Operator fills the runtime draft at `data\scripts\<script_id>\script_materialization.yml`.
2. Operator marks every replacement row `replacement_status: approved`.
3. Create the tracked sanitized record:

```powershell
.venv\Scripts\python.exe -m newsroom.cli.main --db data\ymm4_import_proof.sqlite script approve-materialization --script <script_id> --draft data\scripts\<script_id>\script_materialization.yml --episode-id <episode_id> --approved-by <operator> --output-root docs\approved_materializations
```

4. Review the generated YAML before committing it.
5. Apply it to the active ScriptIR when ready:

```powershell
.venv\Scripts\python.exe -m newsroom.cli.main --db data\ymm4_import_proof.sqlite script apply-approved-materialization --script <script_id> --record docs\approved_materializations\<script_id>.materialization.yml
```

6. Rebuild the export bundle and run `newsroom export inspect`.

The approved record proves text authority only. It does not prove subtitle placement, overlay safety, final YMM4 geometry, or publishing readiness.
