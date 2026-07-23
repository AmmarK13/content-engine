from typing import Optional

from pydantic import BaseModel, Field


class VoiceProfileV1(BaseModel):
    """Approved voice for a run."""

    voice_id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., description="Human-readable voice name")
    reference_sample_id: str = Field(
        ..., description="Reference/pointer to the approved reference voice sample"
    )

    # Fatima (Member 4) owns consent/policy linkage - see Phase 3 team decision
    # on consent_grant_id precedence before this is enforced anywhere.
    consent_grant_id: Optional[str] = Field(
        default=None, description="Which ConsentGrantV1 covers this voice"
    )
    policy_profile_id: Optional[str] = Field(
        default=None, description="Which PolicyProfileV1 applies to this voice"
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    voice = VoiceProfileV1(
        voice_id="voice_001",
        name="Default Narrator",
        reference_sample_id="sample_001",
    )
    print(voice.model_dump_json(indent=2))