"""
orchestrator/consent_gate.py

Pre-flight validation for a run's IdeaRequestV1, called before the
Temporal workflow starts. Real registry lookup against
IdentityProfileV1/VoiceProfileV1 rows and their consent grants.
"""

from contracts.stages.idea_request import IdeaRequestV1, Modality
from orchestrator.telemetry import get_connection


def _fetch_one(query: str, params: tuple) -> tuple | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()


def validate_run(idea: IdeaRequestV1) -> None:
    if idea.modality == Modality.AVATAR:
        if not idea.identity_id:
            raise ValueError("AVATAR run missing identity_id")
        row = _fetch_one(
            "SELECT consent_status FROM identity_profiles WHERE identity_id=%s",
            (idea.identity_id,),
        )
        if row is None:
            raise ValueError(f"identity_id {idea.identity_id} not found in registry")
        if row[0] != "active":
            raise ValueError(f"identity_id {idea.identity_id} consent status is {row[0]}, not active")

    if not idea.voice_id:
        raise ValueError("Run missing voice_id")
    row = _fetch_one(
        "SELECT consent_status FROM voice_profiles WHERE voice_id=%s",
        (idea.voice_id,),
    )
    if row is None:
        raise ValueError(f"voice_id {idea.voice_id} not found in registry")
    if row[0] != "active":
        raise ValueError(f"voice_id {idea.voice_id} consent status is {row[0]}, not active")