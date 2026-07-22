from dataclasses import dataclass
from typing import Optional

@dataclass
class VoiceProfileV1:
    id: str
    display_name: str
    reference_sample_id: str  
    
    # placeholders for Member 4
    consent_grant_id: Optional[str] = None
    policy_profile_id: Optional[str] = None