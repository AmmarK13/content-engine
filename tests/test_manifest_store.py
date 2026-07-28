from datetime import UTC, datetime
import uuid
import pytest



from orchestrator.manifest_store import load_manifest, save_manifest
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