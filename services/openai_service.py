import os
import requests
from openai import OpenAI
from config.settings import settings
from services.character_manager import CharacterManager
from typing import List, Dict
import tempfile

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.character_manager = CharacterManager()
    
    def generate_image(self, prompt: str, output_path: str) -> str:
        """
        Generate an image using DALL-E 3 and save it to the specified path.
        
        Args:
            prompt: Text description for image generation
            output_path: Path where the image will be saved
            
        Returns:
            Path to the saved image file
        """
        try:
            # Enhance prompt with character consistency
            enhanced_prompt = self.character_manager.enhance_scene_prompt(prompt)
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
            
            print(f"Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            raise
    
    def generate_speech(self, text: str, output_path: str) -> str:
        """
        Generate speech audio using OpenAI TTS and save it to the specified path.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio will be saved
            
        Returns:
            Path to the saved audio file
        """
        try:
            print(f"Generating speech: {text[:50]}...")
            
            response = self.client.audio.speech.create(
                model=settings.TTS_MODEL,
                voice=settings.TTS_VOICE,
                input=text
            )
            
            # Save the audio
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise
    
    def generate_scene_assets(self, scene: Dict, scene_index: int, temp_dir: str) -> Dict:
        """
        Generate both image and audio for a single scene.
        
        Args:
            scene: Dictionary containing 'sceneDescription' and 'voiceoverText'
            scene_index: Index of the scene (for file naming)
            temp_dir: Directory to store temporary files
            
        Returns:
            Dictionary with paths to generated image and audio files
        """
        # Create file paths
        image_path = os.path.join(temp_dir, f"scene_{scene_index}_image.png")
        audio_path = os.path.join(temp_dir, f"scene_{scene_index}_audio.mp3")
        
        # Generate assets
        self.generate_image(scene['sceneDescription'], image_path)
        self.generate_speech(scene['voiceoverText'], audio_path)
        
        return {
            'image_path': image_path,
            'audio_path': audio_path,
            'scene_description': scene['sceneDescription'],
            'voiceover_text': scene['voiceoverText'],
            'character_info': self.character_manager.get_character_info()
        }
