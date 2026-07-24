"""
contracts/stages/s70_qc.py

Stage schema for S70 quality control.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class QualityReportV1(BaseModel):
    """QC result for a MasterVideoV1 - feeds into G80 approval."""

    run_id: str = Field(..., description="Which run this QC pass belongs to")
    master_video_hash: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="SHA-256 of the MasterVideoV1 this report evaluates",
    )
    passed: bool = Field(..., description="Whether QC passed")
    metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Named metric scores, e.g. identity_similarity, sync_score",
    )

    model_config = {"extra": "forbid"}


if __name__ == "__main__":
    qc_report = QualityReportV1(
        run_id="run_001",
        master_video_hash="a" * 64,
        passed=True,
        metrics={"identity_similarity": 0.95, "sync_score": 0.98},
    )
    print(qc_report.model_dump_json(indent=2))

    # Test with deliberately invalid input
    try:
        QualityReportV1(
            run_id="run_001",
            master_video_hash="short_hash",
            passed=True,
        )
        raise RuntimeError("Validation failed to reject invalid master_video_hash!")
    except ValidationError:
        print("Successfully caught invalid master_video_hash")
