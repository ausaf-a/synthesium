import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Video Configuration
    VIDEO_WIDTH = 1080  # Vertical format for YouTube Shorts
    VIDEO_HEIGHT = 1920
    VIDEO_FPS = 30
    DEFAULT_SCENE_DURATION = 3  # seconds per scene
    
    # Audio Configuration
    TTS_VOICE = "alloy"  # OpenAI TTS voice options: alloy, echo, fable, onyx, nova, shimmer
    TTS_MODEL = "tts-1"  # or "tts-1-hd" for higher quality
    
    # Image Configuration
    IMAGE_MODEL = "dall-e-3"
    IMAGE_SIZE = "1024x1792"  # Vertical format
    IMAGE_QUALITY = "standard"  # or "hd"
    
    # Character Consistency Configuration
    CHARACTER_CONSISTENCY = True
    CHARACTER_DESCRIPTION_TEMPLATE = "Cinematic scene featuring a sleek blue humanoid robot with glowing orange eyes and weathered metal plating"
    STYLE_ANCHOR = "photorealistic, cinematic lighting, detailed 3D render"
    
    # Output Configuration
    OUTPUT_DIR = "output"
    TEMP_DIR = "temp"
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return True

settings = Settings()
