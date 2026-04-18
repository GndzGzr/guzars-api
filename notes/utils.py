import os
from django.conf import settings
from api.models import VaultConfiguration

def is_path_allowed(filepath: str) -> bool:
    """
    Checks if a given filepath from GitHub should be ingested based on VaultConfiguration.
    """
    try:
        config = VaultConfiguration.load()
        includes = config.include_paths or []
        excludes = config.exclude_paths or [".obsidian", "Templates"]
    except Exception:
        # Fallback if DB isn't ready
        includes = []
        excludes = [".obsidian", "Templates"]
    
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
