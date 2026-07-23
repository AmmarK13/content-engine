"""
contracts/stages/s30_avatar.py

Stage schema for S30 primary visual generation (avatar today; faceless later,
via a different provider behind the same contract).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from contracts.common.envelope import ArtifactRefV1


class VisualRequestV1(BaseModel):
    """
    Request to generate the primary visual track for one pipeline run.

    Deliberately modality-agnostic: identity_id is populated for avatar
    runs and left None for faceless runs, mirroring the same pattern
    already established on IdeaRequestV1. The graph and this contract
    never need to know which modality a run is - only the provider
    configured behind S30 does.
    """

    run_id: str = Field(
        ...,
        description="Unique identifier of the pipeline run.",
    )

    identity_id: Optional[str] = Field(
        default=None,
        description="Which IdentityProfileV1 to use. Populated for avatar "
        "runs; None for faceless runs.",
    )

    scene_count: int = Field(
        ...,
        ge=1,
        description="Number of scenes to generate visuals for.",
    )

    model_config = {
        "extra": "forbid",
    }


class PrimaryVisualTrackV1(BaseModel):
    """
    Generated primary visual track for one pipeline run.

    Represents the visual artifact produced by the S30 stage - an avatar
    render today, potentially a faceless/stock-based render later, behind
    the same contract. The actual video file is stored externally and
    referenced through ArtifactRefV1.
    """

    run_id: str = Field(
        ...,
        description="Unique identifier of the pipeline run.",
    )

    video_artifact: ArtifactRefV1 = Field(
        ...,
        description="Reference to the generated visual file.",
    )

    model_config = {
        "extra": "forbid",
    }


if __name__ == "__main__":
    avatar_request = VisualRequestV1(
        run_id="run_001",
        identity_id="identity_001",
        scene_count=3,
    )
    print(avatar_request.model_dump_json(indent=2))

    faceless_request = VisualRequestV1(
        run_id="run_002",
        scene_count=3,
    )
    print(faceless_request.model_dump_json(indent=2))

    visual_track = PrimaryVisualTrackV1(
        run_id="run_001",
        video_artifact=ArtifactRefV1(
            artifact_id="artifact_003",
            path="artifacts/visual_run_001.mp4",
            hash="c" * 64,
            mime_type="video/mp4",
        ),
    )
    print(visual_track.model_dump_json(indent=2))