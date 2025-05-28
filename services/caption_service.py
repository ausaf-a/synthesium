import re
from typing import List, Dict, Tuple
from config.settings import settings

class CaptionService:
    """
    Service for generating timed captions that appear word by word.
    """
    
    def __init__(self):
        self.font_size = settings.CAPTION_FONT_SIZE
        self.font_color = settings.CAPTION_FONT_COLOR
        self.stroke_color = settings.CAPTION_STROKE_COLOR
        self.stroke_width = settings.CAPTION_STROKE_WIDTH
        self.position = settings.CAPTION_POSITION
        self.font = settings.CAPTION_FONT
        self.font_fallback = settings.CAPTION_FONT_FALLBACK
        self.display_mode = settings.CAPTION_DISPLAY_MODE
        self.word_duration = settings.WORD_DISPLAY_DURATION
        self.transition_gap = settings.WORD_TRANSITION_GAP
        self.enabled = settings.ENABLE_CAPTIONS
    
    def split_text_into_words(self, text: str) -> List[str]:
        """
        Split text into individual words, preserving punctuation.
        
        Args:
            text: Input text to split
            
        Returns:
            List of words with punctuation preserved
        """
        # Split by spaces but keep punctuation attached to words
        words = text.split()
        return [word.strip() for word in words if word.strip()]
    
    def calculate_word_timings(self, text: str, duration: float, whisper_timing: Dict = None) -> List[Dict]:
        """
        Calculate timing for each word, preferring Whisper data if available.
        
        Args:
            text: The text to be displayed
            duration: Total duration of the audio in seconds
            whisper_timing: Optional Whisper timing data from OpenAI service
            
        Returns:
            List of dictionaries with word, start_time, end_time
        """
        # Use Whisper timing if available
        if whisper_timing and whisper_timing.get('word_timings'):
            print("Using Whisper timing for captions")
            return whisper_timing['word_timings']
        
        # Fallback to our timing calculation
        print("Using fallback timing for captions")
        words = self.split_text_into_words(text)
        
        if not words:
            return []
        
        if self.display_mode == 'single_word_pop':
            # Each word gets fixed duration + transition gap
            word_with_gap = self.word_duration + self.transition_gap
            
            # Adjust timing to fit within audio duration
            total_needed_time = len(words) * word_with_gap
            if total_needed_time > duration:
                # Compress timing to fit
                word_with_gap = duration / len(words)
                actual_word_duration = max(0.3, word_with_gap - self.transition_gap)
            else:
                actual_word_duration = self.word_duration
            
            timings = []
            current_time = 0
            
            for i, word in enumerate(words):
                start_time = current_time
                end_time = start_time + actual_word_duration
                
                timings.append({
                    'word': word,
                    'start_time': start_time,
                    'end_time': end_time,
                    'index': i
                })
                
                # Move to next word position (with gap)
                current_time = end_time + self.transition_gap
            
            return timings
        
        else:
            # Fallback to equal distribution
            word_duration = duration / len(words)
            
            timings = []
            for i, word in enumerate(words):
                start_time = i * word_duration
                end_time = (i + 1) * word_duration
                
                timings.append({
                    'word': word,
                    'start_time': start_time,
                    'end_time': end_time,
                    'index': i
                })
            
            return timings
    
    def create_progressive_text(self, word_timings: List[Dict], current_time: float) -> str:
        """
        Get the word that should be visible at the current time.
        For single word pop, returns only one word or empty string.
        
        Args:
            word_timings: List of word timing dictionaries
            current_time: Current time in the video
            
        Returns:
            String with the word that should be visible at current_time
        """
        if self.display_mode == 'single_word_pop':
            # Return only the word that should be visible right now
            for word_timing in word_timings:
                if word_timing['start_time'] <= current_time < word_timing['end_time']:
                    return word_timing['word']
            return ''  # No word visible during transition gaps
        
        else:
            # Progressive text (original behavior)
            visible_words = []
            for word_timing in word_timings:
                if current_time >= word_timing['start_time']:
                    visible_words.append(word_timing['word'])
                else:
                    break
            return ' '.join(visible_words)
    
    def wrap_text(self, text: str, max_chars_per_line: int = 40) -> str:
        """
        Wrap text to multiple lines for better readability.
        
        Args:
            text: Text to wrap
            max_chars_per_line: Maximum characters per line
            
        Returns:
            Text with line breaks
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars_per_line:
                current_line.append(word)
                current_length += len(word) + 1  # +1 for space
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def get_caption_style(self) -> Dict:
        """
        Get the styling configuration for captions.
        
        Returns:
            Dictionary with caption styling options
        """
        return {
            'fontsize': self.font_size,
            'color': self.font_color,
            'stroke_color': self.stroke_color,
            'stroke_width': self.stroke_width,
            'method': 'caption',  # MoviePy caption method
            'align': 'center',
            'font': self.font  # Montserrat-Bold with fallback handling
        }
    
    def get_caption_position(self, video_width: int, video_height: int) -> str:
        """
        Get caption position for center of screen.
        
        Args:
            video_width: Width of the video in pixels
            video_height: Height of the video in pixels
            
        Returns:
            Position string for MoviePy
        """
        # Return exact center position
        return 'center'
    
    def generate_caption_data(self, text: str, duration: float, whisper_timing: Dict = None) -> Dict:
        """
        Generate all caption data needed for video composition.
        
        Args:
            text: Text to be captioned
            duration: Duration of the audio/video
            whisper_timing: Optional Whisper timing data
            
        Returns:
            Dictionary with all caption information
        """
        if not self.enabled:
            return {'enabled': False}
        
        word_timings = self.calculate_word_timings(text, duration, whisper_timing)
        
        return {
            'enabled': True,
            'word_timings': word_timings,
            'duration': duration,
            'style': self.get_caption_style(),
            'text': text
        }
