-- Stores one row for each stage attempt of a pipeline run.
-- Together these rows represent the persisted ProductionManifestV1.

CREATE TABLE IF NOT EXISTS manifest_stage_records (
    run_id TEXT NOT NULL,

    idea_request_id TEXT NOT NULL,

    stage_id TEXT NOT NULL,

    status TEXT NOT NULL,

    attempt INTEGER NOT NULL,

    manifest_created_at TIMESTAMPTZ NOT NULL,

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    output_artifact_ids TEXT[] NOT NULL,

    PRIMARY KEY (run_id, stage_id, attempt)
);