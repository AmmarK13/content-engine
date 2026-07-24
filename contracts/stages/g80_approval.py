"""
contracts/stages/g80_approval.py

Gate schema for G80 human approval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


class HumanApprovalV1(BaseModel):
    """A human reviewer's approval/rejection decision for one MasterVideoV1."""

    reviewer_id: str = Field(..., description="Who reviewed this")
    decision: ApprovalDecision = Field(..., description="The reviewer's decision")
    master_video_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="Which exact video (by hash) this decision applies to",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the decision was recorded",
    )
    comments: Optional[str] = Field(
        default=None, description="Optional reviewer notes"
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    approval = HumanApprovalV1(
        reviewer_id="reviewer_001",
        decision=ApprovalDecision.APPROVED,
        master_video_hash="b" * 64,
        comments="Looks good to publish.",
    )
    print(approval.model_dump_json(indent=2))

    # Test with deliberately invalid input
    try:
        HumanApprovalV1(
            reviewer_id="reviewer_001",
            decision="maybe",
            master_video_hash="b" * 64,
        )
        raise RuntimeError("Validation failed to reject invalid decision!")
    except ValidationError:
        print("Successfully caught invalid decision")
