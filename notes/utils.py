import os
import json
from django.conf import settings
from api.models import VaultConfiguration

def load_local_config():
    local_config_file = os.path.join(settings.BASE_DIR, "vault-config.json")
    if os.path.exists(local_config_file):
        try:
            with open(local_config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def is_path_allowed(filepath: str, config=None) -> bool:
    """
    Checks if a given filepath from GitHub should be ingested.
    Defaults to vault-config.json locally, falls back to VaultConfiguration database model.
    """
    includes = []
    excludes = [".obsidian", "Templates"]
    
    try:
        if config is None:
            # If nothing was explicitly provided, load local or DB
            local_data = load_local_config()
            if local_data:
                config = local_data
            else:
                config = VaultConfiguration.load()
                
        # Parse it out
        if isinstance(config, dict):
            includes = config.get("include_paths", [])
            excludes = config.get("exclude_paths", [".obsidian", "Templates"])
        else:
            includes = config.include_paths or []
            excludes = config.exclude_paths or [".obsidian", "Templates"]
    except Exception:
        pass
        
    # 1. Check excludes first (Exclude takes priority)
    for ex in excludes:
        if filepath.startswith(ex) or f"/{ex}/" in filepath or filepath == ex:
            return False
            
    # 2. Check includes 
    if includes:
        for inc in includes:
            if filepath.startswith(inc) or f"/{inc}/" in filepath:
                return True
        return False
        
    return True
