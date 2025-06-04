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
        Enforces portrait orientation for video compatibility.
        
        Args:
            prompt: Text description for image generation
            output_path: Path where the image will be saved
            
        Returns:
            Path to the saved image file
        """
        try:
            # Check if we have character info for optimization
            character_info = self.character_manager.get_character_info()
            if character_info.get('consistency_enabled') and character_info.get('character_description'):
                # Extract character info from the character manager
                character_description = character_info.get('character_description', '')
                style_anchor = character_info.get('style_anchor', '')
                
                # Combine character info for optimization
                full_character_description = f"{character_description} {style_anchor}".strip()
                
                # Use AI optimization to create a focused prompt
                enhanced_prompt = self.optimize_image_prompt(prompt, full_character_description)
            else:
                enhanced_prompt = f"Cinematic vertical portrait image: {prompt}"
            
            # Ensure portrait orientation is explicitly requested
            orientation_keywords = ["vertical portrait", "tall composition", "portrait orientation", "9:16"]
            if not any(keyword in enhanced_prompt.lower() for keyword in orientation_keywords):
                enhanced_prompt = f"{enhanced_prompt}, vertical portrait orientation, tall composition suitable for mobile video"
            
            # Check cache first
            cached_image = self.cache_manager.get_cached_image(enhanced_prompt)
            if cached_image:
                # Copy cached image to output path
                import shutil
                shutil.copy2(cached_image, output_path)
                return output_path
            
            print(f"Generating image: {prompt[:50]}...")
            print(f"Using prompt: {enhanced_prompt[:100]}...")
            
            response = self.client.images.generate(
                model=settings.IMAGE_MODEL,
                prompt=enhanced_prompt,
                size=settings.IMAGE_SIZE,  # Should be "1024x1792" for portrait
                quality=settings.IMAGE_QUALITY,
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Process the image to ensure portrait orientation
            from PIL import Image
            from io import BytesIO
            
            # Open the downloaded image
            image = Image.open(BytesIO(image_response.content))
            width, height = image.size
            
            print(f"Downloaded image dimensions: {width}x{height}")
            
            # Check if image is actually portrait (height > width)
            if width >= height:
                print(f"⚠️  Image is landscape ({width}x{height}), converting to portrait...")
                
                # Force portrait by cropping to center
                target_width = settings.VIDEO_WIDTH   # 1080
                target_height = settings.VIDEO_HEIGHT  # 1920
                aspect_ratio = target_width / target_height  # 1080/1920 = 0.5625
                
                if width > height:
                    # Landscape - crop sides to make it portrait
                    new_width = int(height * aspect_ratio)
                    if new_width <= width:
                        # Crop from center
                        left = (width - new_width) // 2
                        image = image.crop((left, 0, left + new_width, height))
                        print(f"Cropped to: {new_width}x{height}")
                    else:
                        # If can't crop enough, crop height instead
                        new_height = int(width / aspect_ratio)
                        top = (height - new_height) // 2
                        image = image.crop((0, top, width, top + new_height))
                        print(f"Cropped to: {width}x{new_height}")
                
                # Resize to exact target dimensions
                try:
                    # Try newer PIL version first
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback for older PIL versions
                    image = image.resize((target_width, target_height), Image.LANCZOS)
                print(f"Final size: {target_width}x{target_height}")
            
            elif height > width:
                print(f"✅ Image is portrait: {width}x{height}")
                # Resize to target dimensions while maintaining aspect ratio
                target_width = settings.VIDEO_WIDTH
                target_height = settings.VIDEO_HEIGHT
                try:
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    image = image.resize((target_width, target_height), Image.LANCZOS)
                print(f"Resized to: {target_width}x{target_height}")
            
            else:
                print(f"ℹ️  Image is square: {width}x{height}, converting to portrait...")
                # Square image - extend height to make portrait
                target_width = settings.VIDEO_WIDTH
                target_height = settings.VIDEO_HEIGHT
                try:
                    image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                except AttributeError:
                    image = image.resize((target_width, target_height), Image.LANCZOS)
                print(f"Resized square to portrait: {target_width}x{target_height}")
            
            # Save the processed image
            image.save(output_path, 'PNG', quality=95)
            
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
    
    def optimize_image_prompt(self, scene_description: str, character_description: str) -> str:
        """
        Use a cheap OpenAI call to create an optimized DALL-E prompt.
        Combines scene description with character info without creating montages.
        
        Args:
            scene_description: Description of what's happening in the scene
            character_description: Character's visual style info
            
        Returns:
            Optimized prompt for DALL-E
        """
        try:
            optimization_prompt = f"""Create a single, focused DALL-E prompt for ONE specific scene. Combine these elements:

SCENE: {scene_description}
CHARACTER INFO: {character_description}

Rules:
1. Create ONE focused scene description (not a montage or collage)
2. Include the character's visual style but focus on THIS specific moment
3. Specify the exact location and action happening
4. Keep it under 300 characters for DALL-E
5. Make it cinematic and visually specific
6. Don't mention "various scenes" or "different situations"

Output only the optimized DALL-E prompt:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheapest model for simple tasks
                messages=[
                    {"role": "user", "content": optimization_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            optimized_prompt = response.choices[0].message.content.strip()
            print(f"🤖 AI-optimized prompt: {optimized_prompt[:80]}...")
            return optimized_prompt
            
        except Exception as e:
            print(f"⚠️  Prompt optimization failed, using fallback: {e}")
            # Fallback: clean up the basic concatenation
            fallback = f"{scene_description}. {character_description}"
            # Remove problematic phrases that cause montages
            fallback = fallback.replace("various situations", "this specific scene")
            fallback = fallback.replace("different locations", "the current location")
            fallback = fallback.replace("multiple scenes", "single scene")
            return fallback[:500]  # Keep within DALL-E limits
    
    def generate_scene_assets(self, scene: Dict, scene_index: int, episode_dir: str, character_config: Dict = None) -> Dict:
        """
        Generate both image and audio for a single scene, with Whisper timing.
        Saves assets to the episode directory instead of temp.
        
        Args:
            scene: Dictionary containing 'sceneDescription' and 'voiceoverText'
            scene_index: Index of the scene (for file naming)
            episode_dir: Episode directory to store assets (not temp)
            character_config: Optional character configuration for channel-based generation
            
        Returns:
            Dictionary with paths to generated image and audio files, plus timing
        """
        # Set channel character if provided
        if character_config:
            self.character_manager.set_channel_character(character_config)
        
        # Create assets directory within episode
        assets_dir = os.path.join(episode_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Create file paths in episode assets directory
        image_path = os.path.join(assets_dir, f"scene_{scene_index}_image.png")
        audio_path = os.path.join(assets_dir, f"scene_{scene_index}_audio.mp3")
        
        # Check if assets already exist (for reuse)
        image_exists = os.path.exists(image_path)
        audio_exists = os.path.exists(audio_path)
        
        if image_exists:
            print(f"♻️  Reusing existing image: scene_{scene_index}_image.png")
        else:
            # Generate new image
            self.generate_image(scene['sceneDescription'], image_path)
            
        if audio_exists:
            print(f"♻️  Reusing existing audio: scene_{scene_index}_audio.mp3")
        else:
            # Generate new audio
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
