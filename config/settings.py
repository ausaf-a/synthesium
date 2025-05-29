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
    
    # Camera Movement Configuration
    ENABLE_CAMERA_MOVEMENT = True
    ZOOM_INTENSITY = 0.1  # 0.0 to 0.3 (how much to zoom in/out)
    PAN_INTENSITY = 0.05  # 0.0 to 0.1 (how much to pan)
    MOVEMENT_DURATION_FACTOR = 1.0  # Multiplier for movement speed
    
    # Caption Configuration
    ENABLE_CAPTIONS = True
    CAPTION_FONT_SIZE = 60
    CAPTION_FONT_COLOR = 'white'
    CAPTION_STROKE_COLOR = 'black'
    CAPTION_STROKE_WIDTH = 3
    CAPTION_POSITION = ('center', 'center')  # Center of screen
    CAPTION_FONT = 'Montserrat-Bold'  # Primary font
    CAPTION_FONT_FALLBACK = 'Helvetica-Bold'  # Fallback font
    CAPTION_DISPLAY_MODE = 'single_word_pop'
    WORD_DISPLAY_DURATION = 0.6  # Seconds each word stays visible
    WORD_TRANSITION_GAP = 0.1    # Brief pause between words
    
    # Audio Configuration
    TTS_VOICE = "onyx"  # OpenAI TTS voice options: alloy, echo, fable, onyx, nova, shimmer
    TTS_MODEL = "tts-1"  # or "tts-1-hd" for higher quality
    
    # Background Music Configuration
    ENABLE_BACKGROUND_MUSIC = True
    MUSIC_VOLUME = 0.15  # Background music volume (0.0 to 1.0)
    VOICEOVER_VOLUME = 1.0  # Voiceover volume (0.0 to 1.0)
    MUSIC_FADE_DURATION = 0.5  # Fade in/out duration in seconds
    MUSIC_DIR = "assets/music"  # Directory containing music files
    
    # Image Configuration
    IMAGE_MODEL = "dall-e-3"
    IMAGE_SIZE = "1024x1792"  # Vertical format
    IMAGE_QUALITY = "standard"  # or "hd"
    
    # Character Consistency Configuration
    CHARACTER_CONSISTENCY = True
    CHARACTER_DESCRIPTION_TEMPLATE = "Cinematic vertical portrait scene featuring a sleek blue humanoid robot with glowing orange eyes and weathered metal plating"
    STYLE_ANCHOR = "photorealistic, cinematic lighting, detailed 3D render, vertical composition, portrait orientation"
    
    # Output Configuration
    OUTPUT_DIR = "output"
    TEMP_DIR = "temp"
    
    # Cache Configuration
    ENABLE_CACHE = True
    CACHE_DIR = "cache"
    FORCE_REGENERATE_IMAGES = False
    FORCE_REGENERATE_AUDIO = False
    
    # Whisper Configuration
    WHISPER_MODEL = "whisper-1"
    ENABLE_WHISPER_TIMING = True
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return True

settings = Settings()
