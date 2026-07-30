from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone

from contracts.common.envelope import (
    ProviderDescriptorV1,
    StageEnvelopeV1,
    StageOutputV1,
)
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.common.telemetry import StageRunRecordV1
from orchestrator.manifest_store import save_stage_record
from orchestrator.registry import get as get_provider
from orchestrator.storage import get_artifact, put_artifact
from orchestrator.telemetry import record_telemetry


def execute_stage(
    run_id: str,
    capability: str,
    envelope_dict: dict,
    attempt: int = 1,
) -> StageOutputV1:
    """Execute a stage, persist its output artifact, verify hashes, and checkpoint it."""
    envelope = StageEnvelopeV1.model_validate(envelope_dict)
    provider = get_provider(capability)

    start_ts = time.time()
    output = provider.run(envelope)
    elapsed_ms = int((time.time() - start_ts) * 1000)

    provider_descriptor = ProviderDescriptorV1(**envelope.provider.model_dump(), latency_ms=elapsed_ms, timestamp=datetime.now(timezone.utc))
    envelope = envelope.model_copy(update={"provider": provider_descriptor})

    payload_bytes = json.dumps(output.payload, sort_keys=True).encode("utf-8")
    payload_artifact_id = f"{run_id}_{envelope.stage_id}_payload_attempt{attempt}"
    payload_ref = put_artifact(
        data=payload_bytes,
        artifact_id=payload_artifact_id,
        mime_type="application/json",
    )

    stored_bytes = get_artifact(payload_ref)
    actual_hash = hashlib.sha256(stored_bytes).hexdigest()
    if actual_hash != payload_ref.hash:
        raise ValueError(
            f"Stored artifact hash mismatch for stage {envelope.stage_id}: "
            f"expected {payload_ref.hash}, got {actual_hash}"
        )

    # Preserve the provider-created artifact refs and add the stored payload artifact.
    output.artifact_refs.append(payload_ref)

    artifact_ids = [ref.artifact_id for ref in output.artifact_refs]

    save_stage_record(
        run_id=run_id,
        idea_request_id=run_id,
        stage=StageRecordV1(
            stage_id=envelope.stage_id,
            status=StageStatus.PASSED,
            attempt=attempt,
            started_at=datetime.fromtimestamp(start_ts, timezone.utc),
            completed_at=datetime.now(timezone.utc),
            output_artifact_ids=artifact_ids,
        ),
    )

    record_telemetry(
        StageRunRecordV1(
            run_id=run_id,
            stage_id=envelope.stage_id,
            attempt=attempt,
            input_hash=envelope.input_hash,
            output_hash=payload_ref.hash,
            provider=provider_descriptor,
            started_at=datetime.fromtimestamp(start_ts, timezone.utc),
            ended_at=datetime.now(timezone.utc),
        )
    )

    return output
