import yaml
from pathlib import Path
from typing import Dict, Any

def load_provider_config(capability: str) -> Dict[str, Any]:
    """
    Loads provider configuration from configs/providers/{capability}.yaml
    Returns an empty dict if the file does not exist.
    """
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'configs' / 'providers' / f'{capability}.yaml'
    
    if not config_path.exists():
        return {}
        
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}
