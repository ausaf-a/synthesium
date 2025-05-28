import os
import shutil
from typing import List

def ensure_directory(path: str) -> str:
    """Ensure a directory exists, create if it doesn't."""
    os.makedirs(path, exist_ok=True)
    return path

def cleanup_directory(path: str) -> None:
    """Clean up a directory by removing all its contents."""
    if os.path.exists(path):
        shutil.rmtree(path)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0

def validate_script(script: List[dict]) -> bool:
    """Validate that script has required fields."""
    required_fields = ['sceneDescription', 'voiceoverText']
    
    for i, scene in enumerate(script):
        for field in required_fields:
            if field not in scene:
                print(f"Error: Scene {i+1} missing required field: {field}")
                return False
        
        if not scene['sceneDescription'].strip():
            print(f"Error: Scene {i+1} has empty sceneDescription")
            return False
            
        if not scene['voiceoverText'].strip():
            print(f"Error: Scene {i+1} has empty voiceoverText")
            return False
    
    return True
