from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StyleProfileV1(BaseModel):
    """Approved visual style definition for a run."""

    style_id: str = Field(..., description="Unique style identifier")
    name: str = Field(..., description="Human-readable style name")
    description: Optional[str] = Field(
        default=None,
        description="Short description of the visual style",
    )
    model_config= {"extra":"forbid"}

    


class PolicyProfileV1(BaseModel):
    """Content policy applied during a run."""

    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Human-readable policy name")
    applies_to: str = Field(
        ...,
        description="What this policy governs",
    )
    model_config= {"extra":"forbid"}


class ConsentGrantV1(BaseModel):
    """Consent record for use of a person's likeness or voice."""

    granted_by: str = Field(
        ...,
        description="Person granting consent",
    )
    scope: str = Field(
        ...,
        description="What the consent covers",
    )
    granted_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Consent timestamp",
    )
    model_config= {"extra":"forbid"}


class ProviderConfigV1(BaseModel):
    """Configuration for a provider integration."""

    provider_name: str = Field(
        ...,
        description="Provider name",
    )
    config: dict[str, str] = Field(
        default_factory=dict,
        description="Provider configuration values",
    )
    model_config= {"extra":"forbid"}


if __name__ == "__main__":
    style = StyleProfileV1(
        style_id="style_001",
        name="Anime",
    )

    policy = PolicyProfileV1(
        policy_id="policy_001",
        name="Default Policy",
        applies_to="image_generation",
    )

    consent = ConsentGrantV1(
        granted_by="John Doe",
        scope="face_and_voice",
    )

    provider = ProviderConfigV1(
        provider_name="Gemini",
    )

    print(style.model_dump_json(indent=2))
    print(policy.model_dump_json(indent=2))
    print(consent.model_dump_json(indent=2))
    print(provider.model_dump_json(indent=2))