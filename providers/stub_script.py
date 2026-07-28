"""
providers/stub_script.py

S10 Script Generation Stub Provider.

Produces a deterministic ScriptPackageV1 payload wrapped inside a StageOutputV1.
"""

from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.stages.s10_script import ScriptPackageV1


class StubScriptProvider:
    """
    Stub implementation for S10 script generation capability.

    Always returns a deterministic ScriptPackageV1 payload matching the input run_id or default.
    """

    capability: str = "script_generation"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        # Extract run_id from payload if available, or generate a deterministic default
        payload_dict: dict[str, Any] = getattr(envelope, "payload", {}) if hasattr(envelope, "payload") else {}
        run_id = payload_dict.get("run_id", "run_stub_s10")

        script_package = ScriptPackageV1(
            run_id=run_id,
            scenes=[
                "Welcome to this AI avatar demonstration.",
                "In this video, we explore how deterministic pipelines ensure reliable automated publishing.",
                "Thank you for watching!",
            ],
        )

        return StageOutputV1(
            payload=script_package.model_dump(),
            metadata={
                "stub": True,
                "provider": "stub_script_provider",
                "scene_count": len(script_package.scenes),
            },
            artifact_refs=[],
        )
