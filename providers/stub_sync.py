from __future__ import annotations


import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from contracts.common.envelope import ArtifactRefV1, StageEnvelopeV1, StageOutputV1
from contracts.stages.s40_sync import SynchronizedMediaV1
from orchestrator.storage import put_artifact  # Import at top level
from providers.base import StageProvider


class StubSyncProvider(StageProvider):
    """Stub sync provider that passes through the video artifact from S30."""

    @property
    def capability(self) -> str:
        return "media_sync"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        """
        Return a SynchronizedMediaV1 referencing the same video artifact from S30.

        For the stub, we assume voice and visual are already in sync.
        We look for the video artifact from S30 in the input envelope's artifact_refs.
        """
        # Find the video artifact from S30 (should be in artifact_refs)
        video_artifact = None
        for ref in envelope.artifact_refs:
            if ref.mime_type and ref.mime_type.startswith("video/"):
                video_artifact = ref
                break

        if video_artifact is None:
            # Fallback: create a new reference to the dummy video
            # (In a real workflow, S30 would have provided the reference)
            fixture_path = Path(__file__).parent.parent / "fixtures" / "stubs" / "black_5s.mp4"
            if not fixture_path.exists():
                raise FileNotFoundError(
                    f"Dummy video file not found at {fixture_path}. "
                    "Please ensure fixtures/stubs/black_5s.mp4 exists."
                )

            with open(fixture_path, "rb") as f:
                video_data = f.read()

            artifact_id = f"sync_{envelope.stage_id}_{envelope.attempt}_{datetime.now(timezone.utc).isoformat()}"
            video_artifact = put_artifact(
                data=video_data,
                artifact_id=artifact_id,
                mime_type="video/mp4",
            )

        
        sync_media = SynchronizedMediaV1(
            run_id=envelope.stage_id,  # Using stage_id as run_id for stub
            media_artifact=video_artifact,
        )

        
        return StageOutputV1(
            payload=sync_media.model_dump(),
            metadata={
                "provider": "stub_sync",
                "model": "stub_v1",
                "version": "1.0.0",
                "stub": True,
                "pass_through": True,
            },
            artifact_refs=[video_artifact],
        )