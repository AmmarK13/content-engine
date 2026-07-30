"""
orchestrator/stage_executor.py

Wraps a provider's run() call with manifest persistence and telemetry
recording. Does NOT call put_artifact() itself - providers are responsible
for storing their own artifacts and returning real ArtifactRefV1 objects
in their StageOutputV1. Calling put_artifact() again here would duplicate
artifacts already stored by the provider.
"""

from datetime import datetime, timezone

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.common.telemetry import StageRunRecordV1
from orchestrator.manifest_store import save_stage_record
from orchestrator.registry import get as get_provider
from orchestrator.telemetry import record_telemetry


def execute_stage(
    run_id: str,
    idea_request_id: str,
    capability: str,
    envelope: StageEnvelopeV1,
) -> StageOutputV1:
    """
    Run one stage's provider, then record both the manifest row and the
    telemetry row for this execution. Artifact storage is the provider's
    own responsibility - this function only reads back what the provider
    already returned.
    """
    started_at = datetime.now(timezone.utc)

    provider = get_provider(capability)
    output: StageOutputV1 = provider.run(envelope)

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
