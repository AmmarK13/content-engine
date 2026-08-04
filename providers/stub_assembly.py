"""
providers/stub_assembly.py
S60 Assembly Stub Provider.
Produces a deterministic MasterVideoV1 payload using a pre-generated
black-screen video fixture, persists it as a real artifact through
storage.py, and records a PASSED stage entry in the production manifest.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.stages.idea_request import Modality
from contracts.stages.s60_assembly import MasterVideoV1
from orchestrator.storage import put_artifact

FIXTURE_VIDEO = Path("fixtures") / "stubs" / "black_5s.mp4"


def _measure_duration(video_bytes: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(video_bytes)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", tmp_path],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        duration = float(data["streams"][0].get("duration", 5.0))
        return duration
    except Exception:
        return 5.0  # fallback if ffprobe unavailable
    finally:
        os.unlink(tmp_path)


class StubAssemblyProvider:
    """Stub implementation for S60 assembly capability."""
    capability: str = "assembly"

    def run(self, envelope: StageEnvelopeV1, run_id: str) -> StageOutputV1:
        video_bytes = FIXTURE_VIDEO.read_bytes()

        artifact = put_artifact(
            data=video_bytes,
            artifact_id=f"master_video_{run_id}",
            mime_type="video/mp4",
        )

        duration = _measure_duration(video_bytes)

        master_video = MasterVideoV1(
            run_id=run_id,
            modality=Modality.AVATAR,
            video_artifact=artifact,
            scene_count=3,
            duration_seconds=duration,
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
