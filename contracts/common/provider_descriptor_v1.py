from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ProviderDescriptorV1:
    provider_name: str
    model_version: str
    capability: str
    
    endpoint: Optional[str] = None
    cost: Optional[float] = None
    latency_ms: Optional[int] = None
    timestamp: Optional[datetime] = None