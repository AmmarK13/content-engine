"""
tests/test_providers.py

Unit tests for provider interfaces and stub implementations.
"""

import pytest

from contracts.common.envelope import ProviderDescriptorV1, StageEnvelopeV1, StageOutputV1
from contracts.stages.g90_disclosure import DisclosureDecisionV1
from contracts.stages.s10_script import ScriptPackageV1
from contracts.stages.s70_qc import QualityReportV1
from providers.base import StageProvider
from providers.stub_disclosure import StubDisclosureProvider
from providers.stub_qc import StubQCProvider
from providers.stub_script import StubScriptProvider


def test_stub_script_provider_satisfies_protocol():
    """Verify that StubScriptProvider satisfies the StageProvider Protocol."""
    provider = StubScriptProvider()
    assert isinstance(provider, StageProvider)
    assert provider.capability == "script_generation"


def test_stub_script_provider_run():
    """Verify that StubScriptProvider consumes StageEnvelopeV1 and returns valid StageOutputV1 with ScriptPackageV1 payload."""
    provider = StubScriptProvider()

    envelope = StageEnvelopeV1(
        stage_id="S10",
        attempt=1,
        input_hash="a" * 64,
        artifact_refs=[],
        validation_ref=None,
        provider=ProviderDescriptorV1(
            provider="stub_script_provider",
            model="stub-v1",
            version="1.0.0",
            capability="script_generation",
        ),
    )

    output = provider.run(envelope)

    assert isinstance(output, StageOutputV1)
    assert output.metadata.get("stub") is True

    # Validate output payload against real M0 ScriptPackageV1 contract
    script_pkg = ScriptPackageV1.model_validate(output.payload)
    assert script_pkg.run_id == "run_stub_s10"
    assert len(script_pkg.scenes) == 3
    assert script_pkg.scenes[0] == "Welcome to this AI avatar demonstration."


def test_stub_qc_provider_satisfies_protocol_and_runs():
    """Verify that StubQCProvider satisfies StageProvider and returns valid QualityReportV1."""
    provider = StubQCProvider()
    assert isinstance(provider, StageProvider)
    assert provider.capability == "quality_control"

    envelope = StageEnvelopeV1(
        stage_id="S70",
        attempt=1,
        input_hash="b" * 64,
        artifact_refs=[],
        validation_ref=None,
        provider=ProviderDescriptorV1(
            provider="stub_qc_provider",
            model="stub-v1",
            version="1.0.0",
            capability="quality_control",
        ),
    )

    output = provider.run(envelope)
    assert isinstance(output, StageOutputV1)
    assert output.metadata.get("passed") is True

    report = QualityReportV1.model_validate(output.payload)
    assert report.passed is True
    assert "identity_similarity" in report.metrics


def test_stub_disclosure_provider_satisfies_protocol_and_runs():
    """Verify that StubDisclosureProvider satisfies StageProvider and returns valid DisclosureDecisionV1."""
    provider = StubDisclosureProvider()
    assert isinstance(provider, StageProvider)
    assert provider.capability == "disclosure_check"

    envelope = StageEnvelopeV1(
        stage_id="G90",
        attempt=1,
        input_hash="c" * 64,
        artifact_refs=[],
        validation_ref=None,
        provider=ProviderDescriptorV1(
            provider="stub_disclosure_provider",
            model="stub-v1",
            version="1.0.0",
            capability="disclosure_check",
        ),
    )

    output = provider.run(envelope)
    assert isinstance(output, StageOutputV1)
    assert output.metadata.get("contains_synthetic_media") is True

    disclosure = DisclosureDecisionV1.model_validate(output.payload)
    assert disclosure.contains_synthetic_media is True
