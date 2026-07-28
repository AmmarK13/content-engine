"""
contracts/common/telemetry.py

Per-stage telemetry record. Additive to the frozen M0 contracts (a new
model, not an edit to an existing one) - approved by the team at M1 Day 2
standup before being added.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from contracts.common.envelope import ProviderDescriptorV1


class StageRunRecordV1(BaseModel):
    """
    Telemetry record for a single stage execution.

    Deliberately does not duplicate cost/latency/endpoint - those already
    live on ProviderDescriptorV1, which this record embeds rather than
    re-declaring.
    """

    run_id: str = Field(..., description="Which pipeline run this stage execution belongs to")
    stage_id: str = Field(..., description="Which stage/gate this record covers, e.g. 'S10'")
    attempt: int = Field(..., ge=1, description="1-indexed attempt number for this stage execution")
    input_hash: str = Field(
        ..., min_length=64, max_length=64,
        description="SHA-256 hex digest of this stage's input payload",
    )
    output_hash: Optional[str] = Field(
        default=None, min_length=64, max_length=64,
        description="SHA-256 hex digest of this stage's output payload, if produced",
    )
    provider: ProviderDescriptorV1 = Field(
        ..., description="Which provider handled this stage - cost/latency/endpoint live here",
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this stage execution started",
    )
    ended_at: Optional[datetime] = Field(
        default=None, description="UTC timestamp when this stage execution ended, if finished",
    )

    model_config = {
        "extra": "forbid",
    }


if __name__ == "__main__":
    record = StageRunRecordV1(
        run_id="run_001",
        stage_id="S10",
        attempt=1,
        input_hash="a" * 64,
        output_hash="b" * 64,
        provider=ProviderDescriptorV1(
            provider="stub_script_provider",
            model="stub-v1",
            version="1.0.0",
            capability="script_generation",
            cost=0.0,
            latency_ms=42,
        ),
        ended_at=datetime.now(timezone.utc),
    )
    print(record.model_dump_json(indent=2))
