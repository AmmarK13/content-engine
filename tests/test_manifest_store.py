from datetime import UTC, datetime
import uuid
import pytest


from orchestrator.manifest_store import load_manifest, save_manifest, save_stage_record
from contracts.common.manifest import (
    ProductionManifestV1,
    StageRecordV1,
    StageStatus,
)

@pytest.mark.integration
def test_manifest_round_trip():
    """
    Saving then loading a manifest should reconstruct
    the same ProductionManifestV1 object.
    """

    # Generate a unique run ID so repeated test runs do not
    # violate the composite primary key.
    run_id = f"run_{uuid.uuid4().hex}"

    manifest = ProductionManifestV1(
        run_id=run_id,
        idea_request_id="idea_001",
        created_at=datetime.now(UTC),
        stages=[
            StageRecordV1(
                stage_id="S00",
                status=StageStatus.PASSED,
                attempt=1,
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                output_artifact_ids=["artifact_001"],
            ),
            StageRecordV1(
                stage_id="S10",
                status=StageStatus.RUNNING,
                attempt=1,
                started_at=datetime.now(UTC),
                completed_at=None,
                output_artifact_ids=[],
            ),
        ],
    )

    # Persist the manifest.
    save_manifest(manifest)

    # Read it back from the database.
    loaded = load_manifest(run_id)

    # The reconstructed manifest should match the original.
    assert loaded == manifest


@pytest.mark.integration
def test_save_stage_record():
    """
    Saving a single stage record should allow the manifest
    to be reconstructed correctly.

    Saving the same stage again should update the existing
    row rather than creating a duplicate.
    """

    run_id = f"run_{uuid.uuid4().hex}"

    stage = StageRecordV1(
        stage_id="S50",
        status=StageStatus.PASSED,
        attempt=1,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        output_artifact_ids=["artifact_123"],
    )

    save_stage_record(
        run_id=run_id,
        idea_request_id="idea_001",
        stage=stage,
    )

    # Simulate a retry of the same stage.
    updated_stage = StageRecordV1(
        stage_id="S50",
        status=StageStatus.RUNNING,
        attempt=1,
        started_at=stage.started_at,
        completed_at=None,
        output_artifact_ids=["artifact_updated"],
    )

    save_stage_record(
        run_id=run_id,
        idea_request_id="idea_001",
        stage=updated_stage,
    )

    manifest = load_manifest(run_id)

    assert manifest.run_id == run_id
    assert manifest.idea_request_id == "idea_001"
    assert len(manifest.stages) == 1

    loaded_stage = manifest.stages[0]

    assert loaded_stage.stage_id == "S50"
    assert loaded_stage.status == StageStatus.RUNNING
    assert loaded_stage.attempt == 1
    assert loaded_stage.output_artifact_ids == ["artifact_updated"]