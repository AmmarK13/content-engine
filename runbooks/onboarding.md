# Avatar Harness — New Developer Onboarding

Everything you need to go from a fresh clone to a passing M1 pipeline run.

---

## Prerequisites

Install these before anything else.

| Tool | Minimum Version | Install |
|---|---|---|
| Python | 3.12.11 | [pyenv](https://github.com/pyenv/pyenv) recommended |
| uv | any | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker Engine | any | [docs.docker.com](https://docs.docker.com/engine/install/) |
| Docker Compose | v2 | bundled with Docker Desktop, or `apt install docker-compose-plugin` |
| git | any | system package manager |

Verify everything is available:

```bash
python --version      # Python 3.12.x
uv --version
docker --version
docker compose version
git --version
```

---

## Step 1 — Clone and Install

```bash
git clone https://github.com/AmmarK13/content-engine.git
cd content-engine
uv sync
```

`uv sync` creates the `.venv/`, installs all dependencies, and registers the `avatar-harness` CLI entry point. You should see no errors. The final line will say something like `Installed N packages`.

Verify the CLI is available:

```bash
uv run avatar-harness --help
```

Expected output:
```
usage: avatar-harness [-h] {run} ...
```

---

## Step 2 — Start Infrastructure

All five services (Postgres, Temporal, Temporal UI, MinIO, bucket init) start with one command:

```bash
docker compose up -d
```

Wait 30 seconds for Temporal to fully initialise, then verify:

```bash
docker compose ps
```

Expected state:

| Container | Status |
|---|---|
| temporal-postgresql | running |
| temporal | running |
| temporal-ui | running |
| minio | running |
| minio-createbucket | exited (0) ← correct, it created the bucket and stopped |

If any container is restarting or unhealthy, wait another 20 seconds and check again. If `temporal` stays unhealthy:

```bash
docker compose restart temporal
```

**Service URLs:**

| Service | URL | Credentials |
|---|---|---|
| Temporal UI | http://localhost:8080 | none |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |

> **Fresh environment note:** The three SQL files in `sql/` mount into Postgres's `initdb.d/` directory and run automatically on first boot — the two application tables (`manifest_stage_records`, `stage_run_records`) are created for you. No manual table creation needed.

> **Volume wipe note:** `initdb.d/` only runs on a fresh volume. If you already have a `postgres-data` volume from a previous install and need a clean slate:
> ```bash
> docker compose down -v
> docker compose up -d
> ```

---

## Step 3 — Run the Pipeline

The entire pipeline — worker, execution, approval, and verification — runs from one command:

```bash
uv run avatar-harness run \
  --config configs/runs/avatar_walking_skeleton.yaml \
  --idea "M1 walking skeleton" \
  --privacy unlisted
```

The command does everything automatically:

1. Starts the Temporal worker in the background
2. Creates a unique run ID (timestamp-based, no conflicts between runs)
3. Triggers the pipeline (S00 → S70 run automatically)
4. Waits for G80 — the human approval gate
5. Looks up the real S60 master video hash from the database
6. Sends the `HumanApprovalV1` signal with the hash bound to the decision
7. Waits for G90 + S100 to complete
8. Runs M1 verification and prints the result

**Expected output:**

```
============================================================
AVATAR HARNESS — run
  run_id:   run_20260802_183045
  topic:    M1 walking skeleton
  modality: avatar
  privacy:  unlisted
============================================================

[worker] Started on task queue: avatar-harness
[pipeline] Started workflow: pipeline-run_20260802_183045
[pipeline] Monitor: http://localhost:8080/namespaces/default/workflows/...
[pipeline] Waiting for stages S00→S70 to complete...
[pipeline] 8 stages passed — pipeline paused at G80 ✓
[approve] Signing master video hash: a8de6a44e2e1ec0...
[approve] HumanApprovalV1 signal sent ✓
[pipeline] Waiting for G90 + S100 to complete...
[pipeline] Workflow completed ✓

============================================================
M1 VERIFICATION
============================================================
  ✓ G90    | passed   | 1 artifact(s)
  ✓ S00    | passed   | 1 artifact(s)
  ✓ S10    | passed   | 1 artifact(s)
  ✓ S100   | passed   | 0 artifact(s)
  ✓ S20    | passed   | 1 artifact(s)
  ✓ S30    | passed   | 1 artifact(s)
  ✓ S40    | passed   | 1 artifact(s)
  ✓ S50    | passed   | 1 artifact(s)
  ✓ S60    | passed   | 1 artifact(s)
  ✓ S70    | passed   | 0 artifact(s)

  Stages passed:               10/10
  checkpoint_count:            11/11
  SHA checks:                  ✓ verified by stage_executor
  containsSyntheticMedia=true: ✓
  privacy=unlisted:            ✓
  publish receipt:             ✓

M1 RESULT: ✓ PASS
```

---

## Step 4 — Verify Manually (Optional)

If you want to inspect the results yourself after a run:

**Manifest (all stage rows):**
```bash
uv run python -m scripts.verify_manifest <run_id>
```

**Telemetry (provider info + latency per stage):**
```bash
docker compose exec postgresql psql -U temporal -d content_engine -c \
  "SELECT stage_id, provider_capability, provider_model, provider_latency_ms
   FROM stage_run_records
   WHERE run_id = '<run_id>'
   ORDER BY started_at;"
```

**MinIO artifacts** (content-addressed blobs):

Open http://localhost:9001 → `avatar-harness-poc` bucket → `artifacts/` prefix. Every key is a 64-character SHA-256 hash.

**Temporal UI** (workflow event history):

Open http://localhost:8080 → find your workflow by ID → click through the event timeline.

---

## Running Tests

Unit tests (no infrastructure required):

```bash
uv run pytest tests/ -q \
  --ignore=tests/integration \
  --ignore=tests/test_manifest_store.py \
  --ignore=tests/test_storage.py
```

Expected: all pass.

Integration tests (requires Docker stack running):

```bash
uv run pytest tests/integration/ -q -m integration
```

Contract lint (validates all Pydantic schemas export cleanly):

```bash
uv run python scripts/contract_lint.py
```

Expected: `contract-lint: clean`

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'contracts'`**

You ran a script directly instead of as a module. Always use `-m`:
```bash
# Wrong
python scripts/verify_manifest.py run_001

# Right
uv run python -m scripts.verify_manifest run_001
```

**Worker crashes with `connection refused` on port 7233**

Temporal isn't ready yet. Wait 30 seconds after `docker compose up -d` and try again. Check with `docker compose logs temporal | tail -20` — you want to see `Started Frontend`.

**`UniqueViolation: duplicate key value` in telemetry**

A previous run left dirty rows. The easiest fix is to just run again — each run gets a new auto-generated ID so there's no conflict. If you need to clean a specific run:
```bash
docker compose exec postgresql psql -U temporal -d content_engine -c \
  "DELETE FROM stage_run_records WHERE run_id = '<run_id>';"
docker compose exec postgresql psql -U temporal -d content_engine -c \
  "DELETE FROM manifest_stage_records WHERE run_id = '<run_id>';"
```

**Pipeline stuck — worker terminal shows no activity**

Check if a stale workflow with the same ID is already running in Temporal UI at http://localhost:8080. Terminate it there, then re-run.

**`docker compose down -v` didn't wipe the volume**

If you mixed `sudo` and non-`sudo` docker commands, volumes may be owned by root. Run both with `sudo`:
```bash
sudo docker compose down -v
sudo docker compose up -d
```

---

## Project Structure (Quick Reference)

```
content-engine/
├── cli.py                        ← avatar-harness CLI entry point
├── configs/runs/                 ← run configuration YAML files
├── contracts/
│   ├── common/                   ← shared primitives (ArtifactRefV1, StageEnvelopeV1, etc.)
│   ├── stages/                   ← per-stage input/output models
│   └── registry/                 ← identity, voice, policy, consent models
├── orchestrator/
│   ├── pipeline.py               ← Temporal workflow (AvatarPipeline)
│   ├── stage_executor.py         ← hash verification + manifest + telemetry
│   ├── worker.py                 ← Temporal worker process
│   ├── storage.py                ← MinIO artifact layer
│   ├── manifest_store.py         ← Postgres manifest reads/writes
│   ├── telemetry.py              ← Postgres telemetry writes
│   └── registry.py               ← capability → provider mapping
├── providers/                    ← stub providers (one per capability)
├── scripts/
│   ├── approve.py                ← send G80 approval signal
│   ├── verify_manifest.py        ← print 10/10 manifest view
│   └── run_pipeline.py           ← legacy single-step trigger
├── sql/                          ← Postgres table definitions
├── tests/                        ← unit + integration tests
├── runbooks/                     ← team decision logs and status docs
└── docker-compose.yaml           ← full local stack definition
```

---

## Track Ownership

If you have questions about a specific part of the codebase, here's who owns what:

| Track | Area | Owner |
|---|---|---|
| A | Contracts, orchestrator, manifest, stage executor | Ammar |
| B | Registry profiles, consent/policy, governance stubs | Fatima |
| C | Voice synthesis (S20), captions (S50), WhisperX | Arslan |
| D | Avatar render (S30), lip-sync (S40), integration tests | Mehreen |
| E | Assembly (S60), QC (S70), telemetry, publish, YouTube | Hanab |