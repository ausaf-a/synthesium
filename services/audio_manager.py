import os
import random
from moviepy.editor import AudioFileClip, CompositeAudioClip
from config.settings import settings
from typing import Optional, List

class AudioManager:
    """
    Manages background music selection and audio mixing for videos.
    """
    
    def __init__(self):
        self.music_dir = settings.MUSIC_DIR
        self.enabled = settings.ENABLE_BACKGROUND_MUSIC
        self.music_volume = settings.MUSIC_VOLUME
        self.voiceover_volume = settings.VOICEOVER_VOLUME
        self.fade_duration = settings.MUSIC_FADE_DURATION
        
        # Create music directory if it doesn't exist
        os.makedirs(self.music_dir, exist_ok=True)
        
        # Scan for available music files
        self.available_tracks = self._scan_music_files()
    
    def _scan_music_files(self) -> List[str]:
        """
        Scan the music directory for audio files.
        
        Returns:
            List of paths to music files
        """
        supported_formats = ['.mp3', '.wav', '.m4a', '.aac']
        tracks = []
        
        if os.path.exists(self.music_dir):
            for file in os.listdir(self.music_dir):
                if any(file.lower().endswith(fmt) for fmt in supported_formats):
                    full_path = os.path.join(self.music_dir, file)
                    tracks.append(full_path)
        
        if tracks:
            print(f"Found {len(tracks)} music tracks")
        else:
            print(f"No music tracks found in {self.music_dir}")
            
        return tracks
    
    def select_background_track(self, scene_description: str = None) -> Optional[str]:
        """
        Select an appropriate background track for a scene.
        
        Args:
            scene_description: Optional scene description for mood matching
            
        Returns:
            Path to selected music file or None if no tracks available
        """
        if not self.enabled or not self.available_tracks:
            return None
        
        # For now, randomly select a track
        # TODO: Implement mood-based selection using scene_description
        selected_track = random.choice(self.available_tracks)
        print(f"Selected background track: {os.path.basename(selected_track)}")
        
        return selected_track
    
    def create_background_music_clip(self, music_path: str, duration: float) -> AudioFileClip:
        """
        Create a background music clip adjusted for the target duration.
        
        Args:
            music_path: Path to the music file
            duration: Target duration in seconds
            
        Returns:
            AudioFileClip configured for background use
        """
        try:
            # Load the music file
            music_clip = AudioFileClip(music_path)
            
            # Adjust duration
            if music_clip.duration > duration:
                # Trim if music is longer than needed
                music_clip = music_clip.subclip(0, duration)
            elif music_clip.duration < duration:
                # Loop if music is shorter than needed
                loops_needed = int(duration / music_clip.duration) + 1
                music_clip = music_clip.loop(n=loops_needed).subclip(0, duration)
            
            # Apply volume and fading
            music_clip = music_clip.volumex(self.music_volume)
            
            # Add fade in/out for smooth transitions
            if duration > self.fade_duration * 2:
                music_clip = music_clip.audio_fadein(self.fade_duration).audio_fadeout(self.fade_duration)
            
            return music_clip
            
        except Exception as e:
            print(f"Error processing background music: {e}")
            return None
    
    def mix_audio(self, voiceover_clip: AudioFileClip, music_path: str = None) -> AudioFileClip:
        """
        Mix voiceover with background music.
        
        Args:
            voiceover_clip: Primary voiceover audio
            music_path: Optional path to background music
            
        Returns:
            Mixed audio clip
        """
        if not self.enabled or not music_path:
            # Just return voiceover with adjusted volume
            return voiceover_clip.volumex(self.voiceover_volume)
        
        try:
            # Get duration from voiceover
            duration = voiceover_clip.duration
            
            # Create background music clip
            music_clip = self.create_background_music_clip(music_path, duration)
            
            if music_clip is None:
                print("Failed to create background music, using voiceover only")
                return voiceover_clip.volumex(self.voiceover_volume)
            
            # Adjust voiceover volume
            adjusted_voiceover = voiceover_clip.volumex(self.voiceover_volume)
            
            # Composite the audio tracks
            mixed_audio = CompositeAudioClip([adjusted_voiceover, music_clip])
            
            print(f"Mixed audio: voiceover ({self.voiceover_volume:.2f}) + music ({self.music_volume:.2f})")
            return mixed_audio
            
        except Exception as e:
            print(f"Error mixing audio: {e}")
            print("Falling back to voiceover only")
            return voiceover_clip.volumex(self.voiceover_volume)
    
    def add_sample_tracks(self):
        """
        Add information about where to get sample tracks.
        This is a helper method to guide users.
        """
        print(f"\n🎵 To add background music:")
        print(f"1. Create directory: {self.music_dir}")
        print(f"2. Add .mp3/.wav files to the directory")
        print(f"3. Recommended sources:")
        print(f"   - Pixabay Music (pixabay.com/music)")
        print(f"   - YouTube Audio Library")
        print(f"   - Zapsplat (free with account)")
        print(f"   - Any royalty-free ambient/cinematic music")
        print(f"\n💡 Tip: Look for 'ambient', 'cinematic', or 'background' music")
        print(f"Current tracks found: {len(self.available_tracks)}")
    
    def get_music_info(self) -> dict:
        """
        Get information about the current music setup.
        
        Returns:
            Dictionary with music configuration info
        """
        return {
            'enabled': self.enabled,
            'tracks_available': len(self.available_tracks),
            'music_volume': self.music_volume,
            'voiceover_volume': self.voiceover_volume,
            'music_directory': self.music_dir,
            'track_list': [os.path.basename(track) for track in self.available_tracks]
        }
