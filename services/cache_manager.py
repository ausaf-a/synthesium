import os
import json
import hashlib
from typing import Dict, Optional, Tuple
from config.settings import settings

class CacheManager:
    """
    Manages caching of generated images and audio files to avoid regeneration.
    """
    
    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        self.images_dir = os.path.join(self.cache_dir, "images")
        self.audio_dir = os.path.join(self.cache_dir, "audio")
        self.metadata_file = os.path.join(self.cache_dir, "metadata.json")
        self.enabled = settings.ENABLE_CACHE
        
        # Create cache directories
        if self.enabled:
            os.makedirs(self.images_dir, exist_ok=True)
            os.makedirs(self.audio_dir, exist_ok=True)
            
        # Load existing metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from disk."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache metadata: {e}")
        return {"images": {}, "audio": {}, "whisper": {}}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache metadata: {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to use as cache key."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_cached_image(self, scene_description: str) -> Optional[str]:
        """
        Get cached image path if it exists.
        
        Args:
            scene_description: Scene description text
            
        Returns:
            Path to cached image file or None if not cached
        """
        if not self.enabled or settings.FORCE_REGENERATE_IMAGES:
            return None
            
        content_hash = self._generate_content_hash(scene_description)
        
        if content_hash in self.metadata["images"]:
            cached_path = self.metadata["images"][content_hash]
            if os.path.exists(cached_path):
                print(f"Using cached image: {scene_description[:50]}...")
                return cached_path
            else:
                # Remove invalid cache entry
                del self.metadata["images"][content_hash]
                self._save_metadata()
        
        return None
    
    def cache_image(self, scene_description: str, image_path: str) -> str:
        """
        Cache an image file.
        
        Args:
            scene_description: Scene description text
            image_path: Path to the generated image file
            
        Returns:
            Path to the cached image file
        """
        if not self.enabled:
            return image_path
            
        content_hash = self._generate_content_hash(scene_description)
        cached_filename = f"image_{content_hash}.png"
        cached_path = os.path.join(self.images_dir, cached_filename)
        
        # Copy to cache if not already there
        if not os.path.exists(cached_path):
            import shutil
            shutil.copy2(image_path, cached_path)
        
        # Update metadata
        self.metadata["images"][content_hash] = cached_path
        self._save_metadata()
        
        print(f"Cached image: {cached_path}")
        return cached_path
    
    def get_cached_audio(self, voiceover_text: str) -> Optional[str]:
        """
        Get cached audio path if it exists.
        
        Args:
            voiceover_text: Voiceover text
            
        Returns:
            Path to cached audio file or None if not cached
        """
        if not self.enabled or settings.FORCE_REGENERATE_AUDIO:
            return None
            
        content_hash = self._generate_content_hash(voiceover_text)
        
        if content_hash in self.metadata["audio"]:
            cached_path = self.metadata["audio"][content_hash]
            if os.path.exists(cached_path):
                print(f"Using cached audio: {voiceover_text[:50]}...")
                return cached_path
            else:
                # Remove invalid cache entry
                del self.metadata["audio"][content_hash]
                self._save_metadata()
        
        return None
    
    def cache_audio(self, voiceover_text: str, audio_path: str) -> str:
        """
        Cache an audio file.
        
        Args:
            voiceover_text: Voiceover text
            audio_path: Path to the generated audio file
            
        Returns:
            Path to the cached audio file
        """
        if not self.enabled:
            return audio_path
            
        content_hash = self._generate_content_hash(voiceover_text)
        cached_filename = f"audio_{content_hash}.mp3"
        cached_path = os.path.join(self.audio_dir, cached_filename)
        
        # Copy to cache if not already there
        if not os.path.exists(cached_path):
            import shutil
            shutil.copy2(audio_path, cached_path)
        
        # Update metadata
        self.metadata["audio"][content_hash] = cached_path
        self._save_metadata()
        
        print(f"Cached audio: {cached_path}")
        return cached_path
    
    def get_cached_whisper_timing(self, voiceover_text: str) -> Optional[Dict]:
        """
        Get cached Whisper timing data if it exists.
        
        Args:
            voiceover_text: Voiceover text
            
        Returns:
            Whisper timing data or None if not cached
        """
        if not self.enabled:
            return None
            
        content_hash = self._generate_content_hash(voiceover_text)
        
        if content_hash in self.metadata["whisper"]:
            print(f"Using cached Whisper timing: {voiceover_text[:50]}...")
            return self.metadata["whisper"][content_hash]
        
        return None
    
    def cache_whisper_timing(self, voiceover_text: str, timing_data: Dict):
        """
        Cache Whisper timing data.
        
        Args:
            voiceover_text: Voiceover text
            timing_data: Whisper timing data
        """
        if not self.enabled:
            return
            
        content_hash = self._generate_content_hash(voiceover_text)
        self.metadata["whisper"][content_hash] = timing_data
        self._save_metadata()
        
        print(f"Cached Whisper timing for: {voiceover_text[:50]}...")
    
    def clear_cache(self, cache_type: str = "all"):
        """
        Clear cache of specified type.
        
        Args:
            cache_type: "images", "audio", "whisper", or "all"
        """
        if cache_type in ["images", "all"]:
            self.metadata["images"] = {}
            # Remove image files
            import shutil
            if os.path.exists(self.images_dir):
                shutil.rmtree(self.images_dir)
                os.makedirs(self.images_dir, exist_ok=True)
            
        if cache_type in ["audio", "all"]:
            self.metadata["audio"] = {}
            # Remove audio files
            import shutil
            if os.path.exists(self.audio_dir):
                shutil.rmtree(self.audio_dir)
                os.makedirs(self.audio_dir, exist_ok=True)
            
        if cache_type in ["whisper", "all"]:
            self.metadata["whisper"] = {}
        
        self._save_metadata()
        print(f"Cleared {cache_type} cache")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            "images_cached": len(self.metadata["images"]),
            "audio_cached": len(self.metadata["audio"]),
            "whisper_cached": len(self.metadata["whisper"]),
            "cache_enabled": self.enabled
        }
