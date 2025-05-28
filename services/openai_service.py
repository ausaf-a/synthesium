import os
import requests
from openai import OpenAI
from config.settings import settings
from services.character_manager import CharacterManager
from services.cache_manager import CacheManager
from services.whisper_service import WhisperService
from typing import List, Dict
import tempfile

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.character_manager = CharacterManager()
        self.cache_manager = CacheManager()
        self.whisper_service = WhisperService()
    
    def generate_image(self, prompt: str, output_path: str) -> str:
        """
        Generate an image using DALL-E 3 and save it to the specified path.
        Uses caching to avoid regenerating identical images.
        
        Args:
            prompt: Text description for image generation
            output_path: Path where the image will be saved
            
        Returns:
            Path to the saved image file
        """
        try:
            # Enhance prompt with character consistency
            enhanced_prompt = self.character_manager.enhance_scene_prompt(prompt)
            
            # Check cache first
            cached_image = self.cache_manager.get_cached_image(enhanced_prompt)
            if cached_image:
                # Copy cached image to output path
                import shutil
                shutil.copy2(cached_image, output_path)
                return output_path
            
            print(f"Generating image: {prompt[:50]}...")
            print(f"Enhanced prompt: {enhanced_prompt[:100]}...")
            
            response = self.client.images.generate(
                model=settings.IMAGE_MODEL,
                prompt=enhanced_prompt,
                size=settings.IMAGE_SIZE,
                quality=settings.IMAGE_QUALITY,
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save the image
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            # Cache the generated image
            self.cache_manager.cache_image(enhanced_prompt, output_path)
            
            print(f"Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            raise
    
    def generate_speech(self, text: str, output_path: str) -> str:
        """
        Generate speech audio using OpenAI TTS and save it to the specified path.
        Uses caching to avoid regenerating identical audio.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio will be saved
            
        Returns:
            Path to the saved audio file
        """
        try:
            # Check cache first
            cached_audio = self.cache_manager.get_cached_audio(text)
            if cached_audio:
                # Copy cached audio to output path
                import shutil
                shutil.copy2(cached_audio, output_path)
                return output_path
            
            print(f"Generating speech: {text[:50]}...")
            
            response = self.client.audio.speech.create(
                model=settings.TTS_MODEL,
                voice=settings.TTS_VOICE,
                input=text
            )
            
            # Save the audio
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            # Cache the generated audio
            self.cache_manager.cache_audio(text, output_path)
            
            print(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise
    
    def generate_scene_assets(self, scene: Dict, scene_index: int, temp_dir: str) -> Dict:
        """
        Generate both image and audio for a single scene, with Whisper timing.
        
        Args:
            scene: Dictionary containing 'sceneDescription' and 'voiceoverText'
            scene_index: Index of the scene (for file naming)
            temp_dir: Directory to store temporary files
            
        Returns:
            Dictionary with paths to generated image and audio files, plus timing
        """
        # Create file paths
        image_path = os.path.join(temp_dir, f"scene_{scene_index}_image.png")
        audio_path = os.path.join(temp_dir, f"scene_{scene_index}_audio.mp3")
        
        # Generate assets
        self.generate_image(scene['sceneDescription'], image_path)
        self.generate_speech(scene['voiceoverText'], audio_path)
        
        # Get Whisper timing data
        whisper_timing = None
        cached_timing = self.cache_manager.get_cached_whisper_timing(scene['voiceoverText'])
        
        if cached_timing:
            whisper_timing = cached_timing
        elif self.whisper_service.enabled:
            # Get fresh Whisper timing
            word_timings = self.whisper_service.get_word_timings(audio_path, scene['voiceoverText'])
            
            if word_timings and self.whisper_service.validate_transcription(word_timings, scene['voiceoverText']):
                # Get audio duration for adjustment
                from moviepy.editor import AudioFileClip
                with AudioFileClip(audio_path) as audio_clip:
                    actual_duration = audio_clip.duration
                
                # Adjust timings to match actual audio duration
                adjusted_timings = self.whisper_service.adjust_timings_to_duration(word_timings, actual_duration)
                
                whisper_timing = {
                    'word_timings': adjusted_timings,
                    'duration': actual_duration,
                    'source': 'whisper'
                }
                
                # Cache the timing data
                self.cache_manager.cache_whisper_timing(scene['voiceoverText'], whisper_timing)
            else:
                print("Whisper timing failed or validation failed, will use fallback timing")
        
        return {
            'image_path': image_path,
            'audio_path': audio_path,
            'scene_description': scene['sceneDescription'],
            'voiceover_text': scene['voiceoverText'],
            'character_info': self.character_manager.get_character_info(),
            'whisper_timing': whisper_timing
        }
