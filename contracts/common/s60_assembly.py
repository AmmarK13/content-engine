#final video made before approval from next stage
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
from contracts.common.envelope import ArtifactRefV1
from contracts.common.idea_request import Modality

__all__ = ["MasterVideoV1"]


class MasterVideoV1(BaseModel):
    """
    The fully assembled video, prior to QC (S70) and approval (G80).

    Does not carry its own hash field - video_artifact.hash (via
    ArtifactRefV1) is the single source of truth for this video's identity.
    HumanApprovalV1 and DisclosureDecisionV1 each store their own copy of
    that hash to bind a specific decision to a specific version.
    """

    run_id: str = Field(..., description="Which run this master video belongs to")
    modality: Modality = Field(
        ..., description="Which kind of video this is - avatar or faceless"
    )
    video_artifact: ArtifactRefV1 = Field(
        ..., description="Reference to the assembled video file"
    )
    scene_count: int = Field(..., ge=1, description="Number of scenes in this assembly")
    duration_seconds: float = Field(
        ..., gt=0, description="Total video duration, as measured by ffprobe"
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Non-schema contextual data, mirroring StageOutputV1's metadata "
        "field - an intentional escape hatch for fields we haven't formalized yet.",
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    master = MasterVideoV1(
        run_id="run_001",
        modality=Modality.AVATAR,
        video_artifact=ArtifactRefV1(
            artifact_id="artifact_001",
            path="s3://bucket/artifacts/<sha256>.mp4",
            hash="0" * 64,
            mime_type="video/mp4",
        ),
        scene_count=3,
        duration_seconds=42.5,
    )
    print(master.model_dump_json(indent=2))