from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from contracts.common.envelope import ArtifactRefV1, StageEnvelopeV1, StageOutputV1
from contracts.stages.s40_sync import SynchronizedMediaV1
from orchestrator.storage import get_artifact, put_artifact
from providers.base import StageProvider


class StubSyncProvider(StageProvider):
    

    @property
    def capability(self) -> str:
        return "media_sync"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        
        video_artifact = None
        for ref in envelope.artifact_refs:
            if ref.mime_type and ref.mime_type.startswith("video/"):
                video_artifact = ref
                break

        if video_artifact is not None:
            video_data = get_artifact(video_artifact)
            mime_type = video_artifact.mime_type
        else:
            fixture_path = Path(__file__).parent.parent / "fixtures" / "stubs" / "black_5s.mp4"
            if not fixture_path.exists():
                raise FileNotFoundError(
                    f"Dummy video file not found at {fixture_path}. "
                    "Please ensure fixtures/stubs/black_5s.mp4 exists."
                )

            with open(fixture_path, "rb") as f:
                video_data = f.read()
            mime_type = "video/mp4"

        # ALWAYS create a new sync artifact
        sync_artifact = put_artifact(
            data=video_data,
            artifact_id=f"sync_{envelope.stage_id}_{envelope.attempt}_{datetime.now(timezone.utc).isoformat()}",
            mime_type=mime_type,
        )

        sync_media = SynchronizedMediaV1(
            run_id=envelope.stage_id,
            media_artifact=sync_artifact,
        )

        return StageOutputV1(
            payload=sync_media.model_dump(),
            metadata={
                "provider": "stub_sync",
                "model": "stub_v1",
                "version": "1.0.0",
                "stub": True,
                "pass_through": False,
            },
            # Return the NEW sync artifact, not the original video_artifact
            artifact_refs=[sync_artifact],
        )