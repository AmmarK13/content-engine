from contracts.common.provider_descriptor_v1 import ProviderDescriptorV1
from contracts.registry.identity_profile_v1 import IdentityProfileV1
from contracts.registry.voice_profile_v1 import VoiceProfileV1

#test1
provider = ProviderDescriptorV1("Anthropic", "claude-3-opus-20240229", "text-generation")
print(provider)

#test2
identity = IdentityProfileV1("id-123", "Avatar A", "ref-image-456")
print(identity)

#test3
voice = VoiceProfileV1("voice-789", "Voice B", "sample-012")
print(voice)

print("\nSuccess")
