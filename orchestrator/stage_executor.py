"""
orchestrator/stage_executor.py

Wraps a provider's run() call with manifest persistence and telemetry
recording. Does NOT call put_artifact() itself - providers are responsible
for storing their own artifacts and returning real ArtifactRefV1 objects
in their StageOutputV1. Calling put_artifact() again here would duplicate
artifacts already stored by the provider.
"""

import hashlib
from datetime import datetime, timezone

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.common.telemetry import StageRunRecordV1
from orchestrator.manifest_store import save_stage_record
from orchestrator.registry import get as get_provider
from orchestrator.storage import get_artifact
from orchestrator.telemetry import record_telemetry


def _verify_artifact_hashes(output: StageOutputV1) -> None:
    """
    Checkpoint step: re-fetch every artifact the provider claims to have
    stored, recompute its SHA-256, and confirm it matches ref.hash before
    anything gets persisted. A provider can only claim a stage passed once
    what's actually in storage is verified to match its own reference.
    """
    for ref in output.artifact_refs:
        stored_bytes = get_artifact(ref)
        actual_hash = hashlib.sha256(stored_bytes).hexdigest()
        if actual_hash != ref.hash:
            raise ValueError(
                f"Hash mismatch for artifact {ref.artifact_id}: "
                f"expected {ref.hash}, got {actual_hash}"
            )


def execute_stage(
    run_id: str,
    idea_request_id: str,
    capability: str,
    envelope: StageEnvelopeV1,
) -> StageOutputV1:
    """
    Run one stage's provider, verify its output artifacts against storage,
    then record both the manifest row and the telemetry row for this
    execution. Artifact storage itself is the provider's own responsibility
    - this function only reads back and verifies what the provider already
    stored, it never calls put_artifact.
    """
    started_at = datetime.now(timezone.utc)

    provider = get_provider(capability)
    output: StageOutputV1 = provider.run(envelope)

    _verify_artifact_hashes(output)

    ended_at = datetime.now(timezone.utc)

    output_hash = output.artifact_refs[0].hash if output.artifact_refs else None
    output_artifact_ids = [ref.artifact_id for ref in output.artifact_refs]

    stage_record = StageRecordV1(
        stage_id=envelope.stage_id,
        status=StageStatus.PASSED,
        attempt=envelope.attempt,
        started_at=started_at,
        completed_at=ended_at,
        output_artifact_ids=output_artifact_ids,
    )
    save_stage_record(run_id, idea_request_id, stage_record)

    telemetry_record = StageRunRecordV1(
        run_id=run_id,
        stage_id=envelope.stage_id,
        attempt=envelope.attempt,
        input_hash=envelope.input_hash,
        output_hash=output_hash,
        provider=envelope.provider,
        started_at=started_at,
        ended_at=ended_at,
    )
    record_telemetry(telemetry_record)

    return output
