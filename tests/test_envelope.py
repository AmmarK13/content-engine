"""
tests/test_envelope.py

Real pytest coverage for the Day-1 common models (ArtifactRefV1,
ProviderDescriptorV1, StageEnvelopeV1, StageOutputV1, ValidationReportV1).

Replaces the old verify_envelope.py, which was a print()-based smoke
script that pytest never collected (its filename didn't match pytest's
default discovery pattern, test_*.py / *_test.py) and which only checked
the happy path - it never confirmed invalid input is actually rejected.
"""

import hashlib

import pytest
from pydantic import ValidationError

from contracts.common.envelope import (
    ArtifactRefV1,
    ProviderDescriptorV1,
    StageEnvelopeV1,
    StageOutputV1,
    ValidationReportV1,
)


def fake_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.fixture
def artifact() -> ArtifactRefV1:
    return ArtifactRefV1(
        artifact_id="art_001",
        path="s3://avatar-harness-poc/artifacts/script_v1.json",
        hash=fake_sha256("Today we discuss AI."),
        mime_type="application/json",
    )


@pytest.fixture
def provider() -> ProviderDescriptorV1:
    return ProviderDescriptorV1(
        provider="script_provider",
        model="stub-script-model",
        version="v0.1.0",
        capability="script_generation",
    )


class TestArtifactRefV1:
    def test_construction(self, artifact):
        assert artifact.artifact_id == "art_001"
        assert artifact.mime_type == "application/json"

    def test_rejects_extra_fields(self, artifact):
        with pytest.raises(ValidationError):
            ArtifactRefV1(
                artifact_id="art_001",
                path="s3://bucket/key",
                hash=fake_sha256("x"),
                mime_type="application/json",
                sneaky="not allowed",
            )


class TestProviderDescriptorV1:
    def test_construction(self, provider):
        assert provider.capability == "script_generation"

    def test_missing_required_field_rejected(self):
        with pytest.raises(ValidationError):
            ProviderDescriptorV1(model="x", version="1", capability="y")  # missing provider


class TestStageEnvelopeV1:
    def test_construction(self, artifact, provider):
        envelope = StageEnvelopeV1(
            stage_id="S10",
            attempt=1,
            input_hash=fake_sha256("Today we discuss AI."),
            artifact_refs=[artifact],
            validation_ref=ArtifactRefV1(
                artifact_id="art_002",
                path="s3://avatar-harness-poc/validation/s10_validation_report.json",
                hash=fake_sha256("validation-report-s10"),
                mime_type="application/json",
            ),
            provider=provider,
        )
        assert envelope.stage_id == "S10"
        assert envelope.attempt == 1

    def test_rejects_missing_provider(self, artifact):
        with pytest.raises(ValidationError):
            StageEnvelopeV1(
                stage_id="S10",
                attempt=1,
                input_hash=fake_sha256("x"),
                artifact_refs=[artifact],
            )  # missing required provider

    def test_rejects_extra_fields(self, artifact, provider):
        with pytest.raises(ValidationError):
            StageEnvelopeV1(
                stage_id="S10",
                attempt=1,
                input_hash=fake_sha256("x"),
                artifact_refs=[artifact],
                provider=provider,
                sneaky="not allowed",
            )


class TestStageOutputV1:
    def test_construction(self, artifact):
        output = StageOutputV1(
            payload={"script_text": "Today we discuss AI."},
            metadata={"latency_ms": 842, "cost_usd": 0.002},
            artifact_refs=[artifact],
        )
        assert output.payload["script_text"] == "Today we discuss AI."


class TestValidationReportV1:
    def test_passing_report(self):
        report = ValidationReportV1(passed=True, failures=[], stage_id="S10")
        assert report.passed is True
        assert report.failures == []

    def test_failing_report(self):
        report = ValidationReportV1(
            passed=False,
            failures=["Voice duration mismatch", "Missing captions"],
            stage_id="S20",
        )
        assert report.passed is False
        assert len(report.failures) == 2

    def test_requires_stage_id(self):
        with pytest.raises(ValidationError):
            ValidationReportV1(passed=True, failures=[])