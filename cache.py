import os
import json
import time
from typing import Optional, Any
from pathlib import Path

class FileCache:
    def __init__(self, cache_dir: str = "/tmp/torah_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        # Simple key sanitization
        safe_key = "".join(c for c in key if c.isalnum() or c in "_-")
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[str]:
        """Get cached value if it exists and isn't expired"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            age_hours = (time.time() - data['timestamp']) / 3600
            if age_hours > max_age_hours:
                cache_path.unlink(missing_ok=True)
                return None
            
            return data['content']
        
        except Exception as e:
            print(f"Cache read error: {e}")
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, content: str) -> None:
        """Store content in cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'content': content,
                'timestamp': time.time()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
        
        except Exception as e:
            print(f"Cache write error: {e}")