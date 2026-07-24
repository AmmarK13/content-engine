"""
tests/test_fixtures.py

Validates every fixtures/valid/*.json against its model (should pass) and
every fixtures/malformed/*.json (should fail). Uses pytest.mark.parametrize
so each fixture is its own reported test case - a broken fixture fails the
build individually, rather than being silently swallowed inside a script
that only prints to stdout.
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from contracts.registry.profiles import (
    StyleProfileV1,
    PolicyProfileV1,
    ConsentGrantV1,
    ProviderConfigV1,
)
from contracts.stages.g90_disclosure import DisclosureDecisionV1
from contracts.stages.s10_script import ScriptPackageV1
from contracts.stages.s40_sync import SynchronizedMediaV1
from contracts.stages.s100_publish import PublishReceiptV1

VALID_FIXTURES = [
    ("fixtures/valid/style_profile.json", StyleProfileV1),
    ("fixtures/valid/policy_profile.json", PolicyProfileV1),
    ("fixtures/valid/consent_grant.json", ConsentGrantV1),
    ("fixtures/valid/provider_config.json", ProviderConfigV1),
    ("fixtures/valid/disclosure_decision.json", DisclosureDecisionV1),
    ("fixtures/valid/script_package.json", ScriptPackageV1),
    ("fixtures/valid/synchronized_media.json", SynchronizedMediaV1),
    ("fixtures/valid/publish_receipt.json", PublishReceiptV1),
]

MALFORMED_FIXTURES = [
    ("fixtures/malformed/style_profile_missing_style_id.json", StyleProfileV1),
    ("fixtures/malformed/policy_profile_missing_applies_to.json", PolicyProfileV1),
    ("fixtures/malformed/consent_grant_missing_granted_by.json", ConsentGrantV1),
    ("fixtures/malformed/provider_config_missing_provider_name.json", ProviderConfigV1),
    ("fixtures/malformed/disclosure_decision_invalid_modality.json", DisclosureDecisionV1),
    ("fixtures/malformed/script_package_empty_scenes.json", ScriptPackageV1),
    ("fixtures/malformed/synchronized_media_missing_artifact.json", SynchronizedMediaV1),
    ("fixtures/malformed/publish_receipt_missing_privacy.json", PublishReceiptV1),
]


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


@pytest.mark.parametrize("path,model", VALID_FIXTURES, ids=[p for p, _ in VALID_FIXTURES])
def test_valid_fixture_is_accepted(path, model):
    data = _load(path)
    model.model_validate(data)  # raises ValidationError -> test fails, if bad


@pytest.mark.parametrize("path,model", MALFORMED_FIXTURES, ids=[p for p, _ in MALFORMED_FIXTURES])
def test_malformed_fixture_is_rejected(path, model):
    data = _load(path)
    with pytest.raises(ValidationError):
        model.model_validate(data)