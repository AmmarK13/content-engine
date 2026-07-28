-- Stores one row for each stage attempt of a pipeline run.
-- Together these rows represent the persisted ProductionManifestV1.

CREATE TABLE IF NOT EXISTS manifest_stage_records (
    -- Pipeline run this stage belongs to.
    run_id TEXT NOT NULL,

    -- Originating IdeaRequestV1.
    idea_request_id TEXT NOT NULL,

    -- Stage identifier (S00, S10, G80, etc.).
    stage_id TEXT NOT NULL,

    -- Current status of this stage.
    status TEXT NOT NULL,

    -- Retry number for this stage.
    attempt INTEGER NOT NULL,

    -- Manifest creation time.
    manifest_created_at TIMESTAMPTZ NOT NULL,

    -- Stage execution timestamps.
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- IDs of artifacts produced by this stage.
    output_artifact_ids TEXT[] NOT NULL,

    -- One row represents one attempt of one stage within one run.
    PRIMARY KEY (run_id, stage_id, attempt)
);