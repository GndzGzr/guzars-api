import json
import os
from django.conf import settings

def is_path_allowed(filepath: str) -> bool:
    """
    Checks if a given filepath from GitHub should be ingested based on obsidian_config.json.
    """
    config_path = os.path.join(settings.BASE_DIR, 'obsidian_config.json')
    if not os.path.exists(config_path):
        return True
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception:
        return True
        
    includes = config.get("include_paths", [])
    excludes = config.get("exclude_paths", [".obsidian", "Templates"])
    
    # 1. Check excludes first (Exclude takes priority)
    for ex in excludes:
        if filepath.startswith(ex) or f"/{ex}/" in filepath or filepath == ex:
            return False
            
    # 2. Check includes (If includes are defined, the path MUST match at least one)
    if includes:
        for inc in includes:
            if filepath.startswith(inc) or f"/{inc}/" in filepath:
                return True
        return False
        
    # If no includes are specified, everything not excluded is allowed
    return True
