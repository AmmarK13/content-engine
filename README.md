# Content Engine

AI-powered backend for automated video content generation.

## Project Structure

- contracts/ — Shared Pydantic contracts and schemas.
- graph/ — Pipeline graph definitions.
- orchestrator/ — Workflow orchestration.
- registry/ — Shared profiles and metadata.
- providers/ — AI provider integrations.
- fixtures/ — Test fixtures.
- runbooks/ — Operational documentation.
- dashboards/ — Monitoring assets.
- configs/runs/ — Runtime configuration.


## Setup

### Install uv

https://docs.astral.sh/uv/

### Clone

```bash
git clone <repo>
cd content-engine
```

### Create virtual environment

```bash
uv venv
```

### Install dependencies

```bash
uv sync
```

### Run tests

```bash
uv run pytest
```

### Run the application

```bash
uv run python main.py
```