-- Stores one row per stage execution, for cost/latency/provider telemetry.
-- Additive alongside manifest_stage_records - this is telemetry, not status.

CREATE TABLE IF NOT EXISTS stage_run_records (
    run_id TEXT NOT NULL,
    stage_id TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    input_hash TEXT NOT NULL,
    output_hash TEXT,

    provider_name TEXT NOT NULL,
    provider_model TEXT NOT NULL,
    provider_version TEXT NOT NULL,
    provider_capability TEXT NOT NULL,
    provider_endpoint TEXT,
    provider_cost DOUBLE PRECISION,
    provider_latency_ms INTEGER,

    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,

    PRIMARY KEY (run_id, stage_id, attempt)
);
