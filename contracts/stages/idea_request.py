# starting point of each run
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

__all__ = ["Modality", "IdeaRequestV1"]


class Modality(str, Enum):
    """
    Which kind of video this run produces. Shared across IdeaRequestV1,
    MasterVideoV1, and DisclosureDecisionV1 — import this rather than
    redefining modality as a plain string elsewhere.
    """

    AVATAR = "avatar"
    FACELESS = "faceless"


class IdeaRequestV1(BaseModel):
    """
    The starting input for a run - what the person asked for.

    identity_id is required only when modality is AVATAR (faceless runs
    have no avatar identity). voice_id is required for both modalities,
    since faceless runs still have narration.
    """

    idea_request_id: str = Field(..., description="Unique ID for this idea request")
    modality: Modality = Field(..., description="Which kind of video this run produces")
    topic: str = Field(..., description="What the video should be about")

    identity_id: Optional[str] = Field(
        default=None,
        description="Which IdentityProfileV1 to use. Required when modality=AVATAR; "
        "must be omitted/None for FACELESS runs.",
    )
    voice_id: str = Field(..., description="Which VoiceProfileV1 to use")
    style_id: Optional[str] = Field(
        default=None, description="Which StyleProfileV1 to use, if one was chosen"
    )
    consent_grant_id: Optional[str] = Field(
        default=None,
        description="Which ConsentGrantV1 covers this request's identity/voice. "
        "Optional for now - whether this should be mandatory before a run is "
        "allowed to proceed is a pending team decision, not yet enforced here.",
    )
    requested_by: Optional[str] = Field(
        default=None, description="Who requested this video, if known"
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Non-schema contextual data, mirroring StageOutputV1's metadata "
        "field - an intentional escape hatch for fields we haven't formalized yet.",
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def _identity_required_for_avatar(self) -> "IdeaRequestV1":
        if self.modality == Modality.AVATAR and not self.identity_id:
            raise ValueError("identity_id is required when modality is AVATAR")
        if self.modality == Modality.FACELESS and self.identity_id:
            raise ValueError("identity_id must not be set when modality is FACELESS")
        return self


if __name__ == "__main__":
    avatar_request = IdeaRequestV1(
        idea_request_id="idea_001",
        modality=Modality.AVATAR,
        topic="Intro to the harness",
        identity_id="identity_001",
        voice_id="voice_001",
    )
    print(avatar_request.model_dump_json(indent=2))

    faceless_request = IdeaRequestV1(
        idea_request_id="idea_002",
        modality=Modality.FACELESS,
        topic="Stock-footage explainer",
        voice_id="voice_001",
    )
    print(faceless_request.model_dump_json(indent=2))