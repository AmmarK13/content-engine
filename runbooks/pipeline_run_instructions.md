# G80 Approval — How to Use approve.py

`scripts/approve.py` sends a `HumanApprovalV1` signal to a running pipeline workflow paused at G80.

It automatically looks up the real S60 master video hash from the database — you no longer need to find it manually.

---

## Usage

```bash
uv run python -m scripts.approve <workflow_id> <run_id> [decision]
```

| Argument | Required | Description |
|---|---|---|
| `workflow_id` | Yes | The Temporal workflow ID printed by `run_pipeline.py` |
| `run_id` | Yes | The pipeline run ID (same as `idea_request_id`) |
| `decision` | No | `approved`, `rejected`, or `changes_requested` — defaults to `approved` |

---

## Example

After starting a pipeline run:

```
Pipeline started: workflow_id=pipeline-run_m1_day4
Run ID: run_m1_day4
```

Send approval:

```bash
uv run python -m scripts.approve pipeline-run_m1_day4 run_m1_day4
```

Or with an explicit decision:

```bash
uv run python -m scripts.approve pipeline-run_m1_day4 run_m1_day4 approved
```

Expected output:

```
Found S60 hash from telemetry: a8de6a44e2e1ec07d783500afe878b5485751b6c84247ed4fd4d418778d31b52
Approval signal sent to workflow 'pipeline-run_m1_day4' with decision 'approved'.
Hash used: a8de6a44e2e1ec07d783500afe878b5485751b6c84247ed4fd4d418778d31b52
```

After this, G90 and S100 run automatically and the workflow completes.

---

## What it does internally

1. Connects to the local Postgres DB and queries `stage_run_records` for the S60 `output_hash`
2. Builds a `HumanApprovalV1` with that hash bound to the approval decision
3. Sends it as a signal to the Temporal workflow

The G80 gate in the pipeline checks that the hash in the approval matches the hash of the assembled video — this prevents a stale or mismatched approval from unblocking the wrong run.

---

## Troubleshooting

**`Ignoring stale approval signal`** in the worker logs  
The hash didn't match. Make sure you're passing the correct `run_id` as the second argument.

**`Warning: could not find S60 hash`**  
S60 hasn't completed yet, or the telemetry row is missing. Wait for S00–S70 to finish before approving. Check `verify_manifest <run_id>` to confirm S60 shows `passed`.

**`No workflow found`**  
The workflow ID is wrong or the workflow was already terminated. Check the Temporal UI at http://localhost:8080 for the correct ID.