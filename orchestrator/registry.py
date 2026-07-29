from providers.base import StageProvider


_providers: dict[str,StageProvider] ={}


def register(provider:StageProvider)->None:
    _providers[provider.capability]=provider


def get(capability: str) -> StageProvider:
    if capability not in _providers:
        raise KeyError(
            f"No provider registered for capability '{capability}'. "
            f"Registered: {list(_providers.keys())}"
        )
    return _providers[capability]


def clear() -> None:
    """Remove all registrations. Useful for testing."""
    _providers.clear()