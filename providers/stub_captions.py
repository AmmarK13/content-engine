"""
providers/stub_captions.py

S50 Caption Generation Stub Provider.

Produces a deterministic CaptionTrackV1 payload and persists a small timed
captions JSON artifact through storage.py.
"""

import json
from datetime import UTC, datetime
from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.stages.s50_captions import CaptionTrackV1
from orchestrator.manifest_store import save_stage_record
from orchestrator.storage import put_artifact


class StubCaptionsProvider:
    """Stub implementation for S50 caption generation capability."""

    capability: str = "caption_generation"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        payload_dict: dict[str, Any] = (
            getattr(envelope, "payload", {})
            if hasattr(envelope, "payload")
            else {}
        )

        run_id = payload_dict.get("run_id", "run_stub")

        captions = {
            "words": [
                {"text": "Hello", "start": 0.0, "end": 0.4},
                {"text": "from", "start": 0.5, "end": 0.8},
                {"text": "Avatar", "start": 0.9, "end": 1.4},
                {"text": "Harness", "start": 1.5, "end": 2.1},
            ]
        }

        caption_bytes = json.dumps(captions).encode("utf-8")

        artifact = put_artifact(
            data=caption_bytes,
            artifact_id=f"captions_{run_id}",
            mime_type="application/json",
        )

        save_stage_record(
            run_id=run_id,
            idea_request_id=run_id,
            stage=StageRecordV1(
                stage_id="S50",
                status=StageStatus.PASSED,
                attempt=1,
                started_at=datetime.now(UTC),
                completed_at=datetime.now(UTC),
                output_artifact_ids=[artifact.artifact_id],
            ),
        )

        caption_track = CaptionTrackV1(
            run_id=run_id,
            captions_artifact=artifact,
            word_count=len(captions["words"]),
        )

        return StageOutputV1(
            payload=caption_track.model_dump(mode="json"),
            metadata={
                "stub": True,
                "provider": "stub_captions_provider",
                "word_count": caption_track.word_count,
            },
            artifact_refs=[artifact],
        )