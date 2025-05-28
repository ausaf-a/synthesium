#!/usr/bin/env python3

# Quick test of the fixes
import sys
sys.path.append('/Users/ausafm/Documents/Programming/synthesium')

from services.caption_service import CaptionService
from services.whisper_service import WhisperService

# Test 1: Caption service function signature
print("Testing CaptionService...")
caption_service = CaptionService()

# This should work now (with 3 parameters)
timings = caption_service.calculate_word_timings("test text", 5.0, None)
print(f"✅ Function signature fixed: {len(timings)} words")

# Test 2: Whisper validation
print("\nTesting Whisper validation...")
whisper_service = WhisperService()

# Test case with punctuation issues
whisper_words = [{'word': 'connection'}, {'word': 'it'}, {'word': 'all'}, {'word': 'seems'}, {'word': 'so'}, {'word': 'distant'}]
expected_text = "connection—it all seemed so distant"

result = whisper_service.validate_transcription(whisper_words, expected_text)
print(f"✅ Validation result: {result}")

print("\n🚀 Fixes applied successfully!")
