"""
contracts/stages/g90_disclosure.py

Stage schema for G90 disclosure decisions.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DisclosureDecisionV1(BaseModel):
    """
    Records the disclosure decision for a generated video.

    This model captures whether the output contains synthetic media and
    which policy was used to make that decision.
    """

    modality: str = Field(
        ...,
        description="Content modality, e.g. 'avatar' or 'faceless'.",
    )

    master_video_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 hash of the master video.",
    )

    contains_synthetic_media: bool = Field(
        ...,
        description="Whether the output contains synthetic media.",
    )

    policy_basis: str = Field(
        ...,
        description="PolicyProfileV1 identifier used for this decision.",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the disclosure decision was made.",
    )

    model_config = {
        "extra": "forbid",
    }


if __name__ == "__main__":
    disclosure = DisclosureDecisionV1(
        modality="avatar",
        master_video_hash="a" * 64,
        contains_synthetic_media=True,
        policy_basis="policy_001",
    )

    print(disclosure.model_dump_json(indent=2))