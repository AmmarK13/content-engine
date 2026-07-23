

from typing import Optional

from pydantic import BaseModel, Field


class PublishReceiptV1(BaseModel):
    """Confirmation that a video was published, or a dry-run was attempted."""

    run_id: str = Field(..., description="Which run this receipt belongs to")
    platform_video_id: Optional[str] = Field(
        default=None,
        description="Real platform ID, e.g. YouTube video ID - null for dry-run",
    )
    privacy: str = Field(..., description="e.g. 'unlisted'")
    dry_run: bool = Field(..., description="True if this was a dry-run, not a real upload")

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    receipt = PublishReceiptV1(
        run_id="run_001",
        platform_video_id=None,
        privacy="unlisted",
        dry_run=True,
    )
    print(receipt.model_dump_json(indent=2))