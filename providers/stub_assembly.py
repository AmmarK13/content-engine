"""
providers/stub_assembly.py

S60 Assembly Stub Provider.

Produces a deterministic MasterVideoV1 payload using a pre-generated
black-screen video fixture, persists it as a real artifact through
storage.py, and records a PASSED stage entry in the production manifest.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.common.manifest import StageRecordV1, StageStatus
from contracts.stages.idea_request import Modality
from contracts.stages.s60_assembly import MasterVideoV1
from orchestrator.storage import put_artifact


FIXTURE_VIDEO = Path("fixtures") / "stubs" / "black_5s.mp4"


class StubAssemblyProvider:
    """Stub implementation for S60 assembly capability."""

    capability: str = "assembly"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        payload_dict: dict[str, Any] = (
            getattr(envelope, "payload", {})
            if hasattr(envelope, "payload")
            else {}
        )

        run_id = payload_dict.get("run_id", "run_stub")

        video_bytes = FIXTURE_VIDEO.read_bytes()

        artifact = put_artifact(
            data=video_bytes,
            artifact_id=f"master_video_{run_id}",
            mime_type="video/mp4",
        )


        master_video = MasterVideoV1(
            run_id=run_id,
            modality=Modality.AVATAR,
            video_artifact=artifact,
            scene_count=3,
            duration_seconds=5.0,
        )

        return StageOutputV1(
            payload=master_video.model_dump(mode="json"),
            metadata={
                "stub": True,
                "provider": "stub_assembly_provider",
                "scene_count": master_video.scene_count,
                "duration_seconds": master_video.duration_seconds,
            },
            artifact_refs=[artifact],
        )