"""
providers/stub_intake.py

S00 Intake Stub Provider.

Receives the incoming IdeaRequestV1, stores it as the pipeline's
first tracked artifact, and returns a StageOutputV1.
"""

import json
from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.stages.idea_request import IdeaRequestV1, Modality
from orchestrator.storage import put_artifact


class StubIntakeProvider:
    """Stub implementation for S00 intake."""

    capability = "intake"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:

        payload_dict: dict[str, Any] = (
            getattr(envelope, "payload", {})
            if hasattr(envelope, "payload")
            else {}
        )

        idea = IdeaRequestV1(
            idea_request_id=payload_dict.get("run_id", "run_stub"),
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
            artifact_id=f"idea_{idea.idea_request_id}",
            mime_type="application/json",
        )

        return StageOutputV1(
            payload=idea.model_dump(mode="json"),
            metadata={
                "stub": True,
                "provider": "stub_intake_provider",
            },
            artifact_refs=[artifact],
        )