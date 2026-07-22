"""
contracts/stages/s50_captions.py

Stage schema for S50 caption generation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from contracts.common.envelope import ArtifactRefV1


class CaptionTrackV1(BaseModel):
    """
    Word-level timed captions generated for a pipeline run.

    Represents the caption artifact produced by the S50 alignment/captions
    stage. The actual caption file is stored externally and referenced through
    ArtifactRefV1.
    """

    run_id: str = Field(
        ...,
        description="Unique identifier of the pipeline run.",
    )

    captions_artifact: ArtifactRefV1 = Field(
        ...,
        description="Reference to the generated captions file.",
    )

    word_count: int = Field(
        ...,
        ge=0,
        description="Total number of timed words in the captions.",
    )

    model_config = {
        "extra": "forbid",
    }


if __name__ == "__main__":
    captions = CaptionTrackV1(
        run_id="run_001",
        captions_artifact=ArtifactRefV1(
            artifact_id="artifact_001",
            path="artifacts/captions.json",
            hash="a" * 64,
            mime_type="application/json",
        ),
        word_count=125,
    )

    print(captions.model_dump_json(indent=2))