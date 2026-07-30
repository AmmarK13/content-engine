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

def register_all_stubs() -> None:
    """Register all stub providers for the pipeline."""
    from providers.stub_voice import StubVoiceProvider
    from providers.stub_avatar import StubAvatarProvider
    from providers.stub_sync import StubSyncProvider

    register(StubVoiceProvider())
    register(StubAvatarProvider())
    register(StubSyncProvider())

    # Note: Other stubs (S00, S10, S50, S60, S70, G90, S100) will be registered
    # by their respective owners (Fatima, Malik, Arslan)


# Auto-register stubs when this module is imported
register_all_stubs()