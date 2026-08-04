"""
orchestrator/provider_config.py

Loads per-capability provider configuration (API keys, model IDs,
endpoint URLs). Priority: environment variables > configs/providers/
<capability>.yaml > defaults. Real values (API keys) must never be
committed — see configs/providers/*.yaml in .gitignore.
"""

import os
from pathlib import Path

import yaml


def load_provider_config(capability: str) -> dict:
    """
    Load configuration for a provider capability.
    Priority: environment variables > configs/providers/<capability>.yaml > defaults.
    """
    config = {}

    config_path = Path("configs/providers") / f"{capability}.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    # Environment variables override YAML
    prefix = capability.upper().replace("-", "_")
    for key in list(config.keys()):
        env_key = f"{prefix}_{key.upper()}"
        if env_key in os.environ:
            config[key] = os.environ[env_key]

    return config
