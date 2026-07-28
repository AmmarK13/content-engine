# Local Development Setup

## Prerequisites

* Python 3.12+
* `uv`
* Docker Engine
* Docker Compose

Verify the tools are installed:

```bash
uv --version
docker --version
docker compose version
```

---

## Start infrastructure

From the project root:

```bash
sudo docker compose up -d
```

Verify all services are running:

```bash
sudo docker compose ps
```

Expected services:

| Service            | Purpose                                   |
| ------------------ | ----------------------------------------- |
| postgresql         | Temporal metadata + project database      |
| temporal           | Temporal Server                           |
| temporal-ui        | Temporal Web UI                           |
| minio              | Object storage                            |
| minio-createbucket | Creates the development bucket then exits |

---

## Verify services

### PostgreSQL

```bash
sudo docker compose logs postgresql
```

Expected:

```
database system is ready to accept connections
```

---

### Temporal

```bash
sudo docker compose logs temporal
```

Expected:

```
Started Frontend
Started History
Started Matching
Started Worker
```

---

### Temporal UI

Open:

```
http://localhost:8080
```

The UI should load without errors.

---

### MinIO

API:

```
http://localhost:9000
```

Console:

```
http://localhost:9001
```

Default credentials:

```
Username: minioadmin
Password: minioadmin
```

---

# Running the example workflow

Open **Terminal 1**:

```bash
uv run python -m orchestrator.worker
```

Expected:

```
Worker started, polling task queue 'avatar-harness'
```

Leave this terminal running.

---

Open **Terminal 2**:

```bash
uv run python -m scripts.run_hello
```

Expected output:

```
Workflow result: Hello avatar harness!
```

The workflow should also appear in the Temporal UI.

---

# Common gotchas

## 1. Temporal starts before PostgreSQL is ready

Symptoms:

```
pq: the database system is starting up
```

or

```
Unable to setup SQL schema
```

Cause:

Temporal attempted to initialise its schema before PostgreSQL finished starting.

Fix:

The compose file should use a PostgreSQL health check together with:

```yaml
depends_on:
  postgresql:
    condition: service_healthy
```

If this occurs before the health check is added:

```bash
sudo docker compose restart temporal
```

---

## 2. ModuleNotFoundError: No module named 'orchestrator'

Run package modules instead of executing files directly.

Correct:

```bash
uv run python -m orchestrator.worker
uv run python -m scripts.run_hello
```

Avoid:

```bash
uv run python orchestrator/worker.py
uv run python scripts/run_hello.py
```

---

## 3. Docker container name conflicts

Symptoms:

```
Conflict. The container name "... " is already in use
```

Cause:

Old containers still exist from a previous Compose project.

Fix:

```bash
sudo docker compose down -v
sudo docker rm -f minio temporal temporal-ui temporal-postgresql
sudo docker compose up -d
```

---

# Success criteria

The local environment is correctly configured when:

* All Docker services are running.
* Temporal UI loads at `http://localhost:8080`.
* MinIO Console loads at `http://localhost:9001`.
* The worker starts successfully.
* Running `scripts.run_hello` completes successfully.
* The workflow appears in the Temporal UI with a **Completed** status.
