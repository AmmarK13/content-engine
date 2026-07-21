import hashlib

from contracts.common.envelope import (
    ArtifactRefV1,
    ProviderDescriptorV1,
    StageEnvelopeV1,
    StageOutputV1,
    ValidationReportV1,
)


def fake_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    artifact = ArtifactRefV1(
        path="s3://avatar-harness-poc/artifacts/script_v1.json",
        hash=fake_sha256("Today we discuss AI."),
        mime_type="application/json",
    )
    print("ArtifactRefV1 OK:", artifact)

    provider = ProviderDescriptorV1(
        provider="script_provider",
        model="stub-script-model",
        version="v0.1.0",
        capability="script_generation",
    )
    print("ProviderDescriptorV1 OK:", provider)

    envelope = StageEnvelopeV1(
        stage_id="S10",
        attempt=1,
        input_hash=fake_sha256("Today we discuss AI."),
        artifact_refs=[artifact],
        validation_ref=ArtifactRefV1(
            path="s3://avatar-harness-poc/validation/s10_validation_report.json",
            hash=fake_sha256("validation-report-s10"),
            mime_type="application/json",
        ),
        provider=provider,
    )
    print("StageEnvelopeV1 OK:", envelope)

    output = StageOutputV1(
        payload={"script_text": "Today we discuss AI."},
        metadata={"latency_ms": 842, "cost_usd": 0.002},
        artifact_refs=[artifact],
    )
    print("StageOutputV1 OK:", output)

    passing_report = ValidationReportV1(
        passed=True,
        failures=[],
        stage_id="S10",
    )
    print("ValidationReportV1 (pass) OK:", passing_report)

    failing_report = ValidationReportV1(
        passed=False,
        failures=["Voice duration mismatch", "Missing captions"],
        stage_id="S20",
    )
    print("ValidationReportV1 (fail) OK:", failing_report)

    print("\nAll three Day-1 contracts instantiated with no import or validation errors.")


if __name__ == "__main__":
    main()
