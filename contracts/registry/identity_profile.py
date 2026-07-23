from typing import Optional

from pydantic import BaseModel, Field


class IdentityProfileV1(BaseModel):
    """Approved avatar identity for a run."""

    identity_id: str = Field(..., description="Unique identity identifier")
    name: str = Field(..., description="Human-readable identity name")
    reference_asset: str = Field(
        ..., description="Reference/pointer to the approved identity's source image"
    )

    # Fatima (Member 4) owns consent/policy linkage - see Phase 3 team decision
    # on consent_grant_id precedence before this is enforced anywhere.
    consent_grant_id: Optional[str] = Field(
        default=None, description="Which ConsentGrantV1 covers this identity"
    )
    policy_profile_id: Optional[str] = Field(
        default=None, description="Which PolicyProfileV1 applies to this identity"
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    identity = IdentityProfileV1(
        identity_id="identity_001",
        name="Default Presenter",
        reference_asset="s3://bucket/identities/identity_001_ref.png",
    )
    print(identity.model_dump_json(indent=2))