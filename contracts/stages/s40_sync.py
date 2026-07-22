

from pydantic import BaseModel, Field

from contracts.common.envelope import ArtifactRefV1


class SynchronizedMediaV1(BaseModel):
    """Voice and visual tracks synchronized together."""

    run_id: str = Field(..., description="Which run this synchronized media belongs to")
    media_artifact: ArtifactRefV1 = Field(
        ..., description="Reference to the synchronized output file"
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    artifact = ArtifactRefV1(
        artifact_id="art_010",
        path="s3://avatar-harness-poc/artifacts/synced_v1.mp4",
        hash="a" * 64,
        mime_type="video/mp4",
    )
    media = SynchronizedMediaV1(run_id="run_001", media_artifact=artifact)
    print(media.model_dump_json(indent=2))