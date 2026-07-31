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
    from providers.stub_intake import StubIntakeProvider
    from providers.stub_script import StubScriptProvider
    from providers.stub_voice import StubVoiceProvider
    from providers.stub_avatar import StubAvatarProvider
    from providers.stub_sync import StubSyncProvider
    from providers.stub_captions import StubCaptionsProvider
    from providers.stub_assembly import StubAssemblyProvider
    from providers.stub_qc import StubQCProvider
    from providers.stub_disclosure import StubDisclosureProvider
    from providers.stub_publish import StubPublishProvider

    register(StubIntakeProvider())
    register(StubScriptProvider())
    register(StubVoiceProvider())
    register(StubAvatarProvider())
    register(StubSyncProvider())
    register(StubCaptionsProvider())
    register(StubAssemblyProvider())
    register(StubQCProvider())
    register(StubDisclosureProvider())
    register(StubPublishProvider())

# Auto-register stubs when this module is imported
register_all_stubs()