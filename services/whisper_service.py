from openai import OpenAI
from config.settings import settings
from typing import List, Dict, Optional
import os

class WhisperService:
    """
    Service for using OpenAI Whisper to get precise word timings from audio.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.WHISPER_MODEL
        self.enabled = settings.ENABLE_WHISPER_TIMING
    
    def get_word_timings(self, audio_path: str, expected_text: str) -> Optional[List[Dict]]:
        """
        Get precise word timings from audio using Whisper.
        
        Args:
            audio_path: Path to the audio file
            expected_text: Expected text (for validation)
            
        Returns:
            List of word timing dictionaries or None if failed
        """
        if not self.enabled:
            return None
            
        try:
            print(f"Getting Whisper timings for audio: {os.path.basename(audio_path)}")
            
            with open(audio_path, "rb") as audio_file:
                # Use Whisper with word-level timestamps
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Extract word-level timings
            if hasattr(response, 'words') and response.words:
                word_timings = []
                
                for word_data in response.words:
                    word_timings.append({
                        'word': word_data.word.strip(),
                        'start_time': word_data.start,
                        'end_time': word_data.end,
                        'confidence': getattr(word_data, 'confidence', 1.0)
                    })
                
                print(f"Whisper found {len(word_timings)} words with timings")
                return word_timings
            
            else:
                print("Whisper response doesn't contain word-level timestamps")
                return None
                
        except Exception as e:
            print(f"Whisper timing failed: {e}")
            return None
    
    def validate_transcription(self, whisper_words: List[Dict], expected_text: str) -> bool:
        """
        Validate that Whisper transcription matches expected text reasonably well.
        
        Args:
            whisper_words: List of word timing dictionaries from Whisper
            expected_text: Expected text
            
        Returns:
            True if transcription is reasonable match
        """
        if not whisper_words:
            return False
        
        # Normalize both texts for comparison
        def normalize_text(text):
            # Convert to lowercase and remove punctuation
            import re
            text = text.lower()
            # Remove all punctuation including em dashes, hyphens, etc.
            text = re.sub(r'[^\w\s]', '', text)
            return text.split()
        
        # Get normalized word lists
        whisper_words_clean = [normalize_text(w['word'])[0] if normalize_text(w['word']) else '' 
                              for w in whisper_words]
        whisper_words_clean = [w for w in whisper_words_clean if w]  # Remove empty
        
        expected_words_clean = normalize_text(expected_text)
        
        # Simple word-by-word comparison
        matching_words = 0
        for expected_word in expected_words_clean:
            if expected_word in whisper_words_clean:
                matching_words += 1
        
        similarity = matching_words / len(expected_words_clean) if expected_words_clean else 0
        
        print(f"Transcription similarity: {similarity:.2f}")
        print(f"Expected: {' '.join(expected_words_clean)}")
        print(f"Whisper:  {' '.join(whisper_words_clean)}")
        
        # Lower threshold to 60% to account for minor variations
        return similarity >= 0.6
    
    def adjust_timings_to_duration(self, word_timings: List[Dict], target_duration: float) -> List[Dict]:
        """
        Adjust Whisper timings to fit target duration if needed.
        
        Args:
            word_timings: Original word timings from Whisper
            target_duration: Target duration in seconds
            
        Returns:
            Adjusted word timings
        """
        if not word_timings:
            return word_timings
        
        # Get the actual duration from Whisper
        whisper_duration = max(w['end_time'] for w in word_timings)
        
        # If timings are close to target, use as-is
        if abs(whisper_duration - target_duration) < 0.5:
            return word_timings
        
        # Scale timings to fit target duration
        scale_factor = target_duration / whisper_duration
        
        adjusted_timings = []
        for word_data in word_timings:
            adjusted_timings.append({
                'word': word_data['word'],
                'start_time': word_data['start_time'] * scale_factor,
                'end_time': word_data['end_time'] * scale_factor,
                'confidence': word_data.get('confidence', 1.0)
            })
        
        print(f"Adjusted Whisper timings: {whisper_duration:.2f}s → {target_duration:.2f}s (scale: {scale_factor:.2f})")
        return adjusted_timings
