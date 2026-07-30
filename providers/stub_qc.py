"""
providers/stub_qc.py

S70 Quality Control Stub Provider.

Produces a deterministic QualityReportV1 payload wrapped inside a StageOutputV1.
"""

from typing import Any

from contracts.common.envelope import StageEnvelopeV1, StageOutputV1
from contracts.stages.s70_qc import QualityReportV1


class StubQCProvider:
    """
    Stub implementation for S70 quality control capability.

    Always returns a deterministic QualityReportV1 payload with passed=True
    and dummy quality metrics.
    """

    capability: str = "quality_control"

    def run(self, envelope: StageEnvelopeV1) -> StageOutputV1:
        payload_dict: dict[str, Any] = getattr(envelope, "payload", {}) if hasattr(envelope, "payload") else {}
        run_id = payload_dict.get("run_id", "run_stub_s70")
        master_video_hash = payload_dict.get("master_video_hash", "a" * 64)

        qc_report = QualityReportV1(
            run_id=run_id,
            master_video_hash=master_video_hash,
            passed=True,
            metrics={
                "identity_similarity": 0.96,
                "sync_score": 0.98,
            },
        )

        return StageOutputV1(
            payload=qc_report.model_dump(),
            metadata={
                "stub": True,
                "provider": "stub_qc_provider",
                "passed": qc_report.passed,
            },
            artifact_refs=[],
        )
