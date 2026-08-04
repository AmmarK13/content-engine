"""
orchestrator/consent_gate.py

Pre-flight validation for a run's IdeaRequestV1, called before the
Temporal workflow starts. M2 Day 1 stub: checks presence only.
M2 Day 3 replaces the body with a real registry lookup against
IdentityProfileV1/VoiceProfileV1 and their consent grants.
"""

from contracts.stages.idea_request import IdeaRequestV1, Modality


def validate_run(idea: IdeaRequestV1) -> None:
    """
    Raises ValueError if the run references an identity or voice
    that does not exist in the registry or lacks a consent grant.

    Currently checks: identity_id not None and not empty string,
    voice_id not None and not empty string. Real registry lookup
    against IdentityProfileV1 and VoiceProfileV1 rows comes in M2
    Day 3 once the registry database table is created.
    """
    if idea.modality == Modality.AVATAR:
        if not idea.identity_id:
            raise ValueError("AVATAR run missing identity_id")
    if not idea.voice_id:
        raise ValueError("Run missing voice_id")