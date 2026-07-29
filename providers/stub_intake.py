from datetime import UTC, datetime

"""
providers/stub_intake.py

S00 Intake Stub Provider.

Records the incoming IdeaRequestV1 as the pipeline's first tracked artifact
and returns it wrapped inside a StageOutputV1.

Design note: StageEnvelopeV1 currently does not carry the original IdeaRequestV1 payload.
Until that wiring lands, this stub deterministically reconstructs a minimal
IdeaRequestV1 from the available run_id so the storage pipeline can be exercised
without changing the frozen contracts.
"""

import json
from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.stages.idea_request import IdeaRequestV1, Modality
from orchestrator.manifest_store import save_stage_record
from orchestrator.storage import put_artifact


class StubIntakeProvider:
    """Stub implementation for S00 intake capability."""

    capability: str = "intake"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        payload_dict: dict[str, Any] = (
            getattr(envelope, "payload", {})
            if hasattr(envelope, "payload")
            else {}
        )

        run_id = payload_dict.get("run_id", "run_stub")

        idea = IdeaRequestV1(
            idea_request_id=run_id,
            modality=Modality.AVATAR,
            topic="Stub pipeline request",
            identity_id="identity_stub",
            voice_id="voice_stub",
        )

        idea_bytes = json.dumps(
            idea.model_dump(mode="json")
        ).encode("utf-8")

        artifact = put_artifact(
            data=idea_bytes,
            artifact_id=f"idea_{run_id}",
            mime_type="application/json",
        )

        save_stage_record(
            run_id=run_id,
            idea_request_id=idea.idea_request_id,
            stage=StageRecordV1(
                stage_id="S00",
                status=StageStatus.PASSED,
                attempt=1,
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                output_artifact_ids=[artifact.artifact_id],
            ),
        )

        return StageOutputV1(
            payload=idea.model_dump(mode="json"),
            metadata={
                "stub": True,
                "provider": "stub_intake_provider",
            },
            artifact_refs=[artifact],
        )