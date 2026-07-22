from dataclasses import dataclass
from typing import Optional

@dataclass
class IdentityProfileV1:
    id: str
    display_name: str
    reference_asset: str 
    
    # placeholder for Member 4
    consent_grant_id: Optional[str] = None
    policy_profile_id: Optional[str] = None