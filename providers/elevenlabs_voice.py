import json

from elevenlabs.client import ElevenLabs

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.stages.s20_voice import VoiceTrackV1
from orchestrator.provider_config import load_provider_config
from orchestrator.storage import get_artifact, put_artifact


class ElevenLabsVoiceProvider:
    capability: str = "voice_synthesis"

    def __init__(self):
        config = load_provider_config("voice_synthesis")
        self._client = ElevenLabs(api_key=config["api_key"])
        self._model_id = config.get("model_id", "eleven_multilingual_v2")

    def run(self, envelope: StageEnvelopeV1, run_id: str) -> StageOutputV1:
        script_ref = next(
            (r for r in envelope.artifact_refs if "script" in r.artifact_id),
            None,
        )
        if script_ref is None:
            raise ValueError("S20 requires script artifact from S10")

        script_bytes = get_artifact(script_ref)
        script_data = json.loads(script_bytes)
        narration = " ".join(script_data.get("scenes", []))

        voice_id = envelope.provider.model  # temporary — real registry lookup comes M2 Day 3

        audio_generator = self._client.text_to_speech.convert(
            text=narration,
            voice_id=voice_id,
            model_id=self._model_id,
        )
        audio_bytes = b"".join(audio_generator)

        artifact = put_artifact(
            data=audio_bytes,
            artifact_id=f"voice_{run_id}",
            mime_type="audio/mpeg",
        )

        duration_seconds = len(audio_bytes) / (128_000 / 8)  # rough MP3 estimate, refined later

        voice_track = VoiceTrackV1(
            run_id=run_id,
            voice_id=voice_id,
            audio_artifact=artifact,
            duration_seconds=max(duration_seconds, 0.1),
        )

        return StageOutputV1(
            payload=voice_track.model_dump(),
            metadata={"provider": "elevenlabs", "model": self._model_id},
            artifact_refs=[artifact],
        )