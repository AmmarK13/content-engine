import json
from pathlib import Path
from pydantic import ValidationError

from contracts.registry.profiles import (
    StyleProfileV1,
    PolicyProfileV1,
    ConsentGrantV1,
    ProviderConfigV1,
)
from contracts.stages.g90_disclosure import DisclosureDecisionV1

fixtures = [
    # Valid fixtures
    ("fixtures/valid/style_profile.json", StyleProfileV1, True),
    ("fixtures/valid/policy_profile.json", PolicyProfileV1, True),
    ("fixtures/valid/consent_grant.json", ConsentGrantV1, True),
    ("fixtures/valid/provider_config.json", ProviderConfigV1, True),
    ("fixtures/valid/disclosure_decision.json", DisclosureDecisionV1, True),

    # Malformed fixtures
# Malformed fixtures
    ("fixtures/malformed/style_profile_missing_style_id.json", StyleProfileV1, False),
    ("fixtures/malformed/policy_profile_missing_applies_to.json", PolicyProfileV1, False),
    ("fixtures/malformed/consent_grant_missing_granted_by.json", ConsentGrantV1, False),
    ("fixtures/malformed/provider_config_missing_provider_name.json", ProviderConfigV1, False),
    ("fixtures/malformed/disclosure_decision_invalid_modality.json", DisclosureDecisionV1, False),
]

for path, model, should_pass in fixtures:
    print(f"\nTesting {path}")

    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))

    try:
        model.model_validate(data)

        if should_pass:
            print("PASS (valid as expected)")
        else:
            print("FAIL (should have been rejected)")

    except ValidationError as e:
        if should_pass:
            print("FAIL (should have been accepted)")
            print(e)
        else:
            print("PASS (rejected malformed fixture as expected)")