"""
contracts/stages/s20_voice.py

Stage schema for S20 voice generation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from contracts.common.envelope import ArtifactRefV1


class VoiceTrackV1(BaseModel):
    """
    Generated voice audio for one pipeline run.

    Represents the audio artifact produced by the S20 voice stage. The
    actual audio file is stored externally and referenced through
    ArtifactRefV1 - this model never carries raw audio bytes.
    """

    run_id: str = Field(
        ...,
        description="Unique identifier of the pipeline run.",
    )

    voice_id: str = Field(
        ...,
        description="Which VoiceProfileV1 was used to generate this track.",
    )

    audio_artifact: ArtifactRefV1 = Field(
        ...,
        description="Reference to the generated audio file.",
    )

    duration_seconds: float = Field(
        ...,
        gt=0,
        description="Audio duration, as measured from the generated file.",
    )

    model_config = {
        "extra": "forbid",
    }


if __name__ == "__main__":
    voice_track = VoiceTrackV1(
        run_id="run_001",
        voice_id="voice_001",
        audio_artifact=ArtifactRefV1(
            artifact_id="artifact_002",
            path="artifacts/voice_run_001.wav",
            hash="b" * 64,
            mime_type="audio/wav",
        ),
        duration_seconds=42.3,
    )

    print(voice_track.model_dump_json(indent=2))