# Synthesium - AI Video Generator

## Overview
Synthesium generates narrative-driven videos using AI. It creates scenes with DALL-E images, OpenAI TTS voiceovers, dynamic camera movements, and real-time Whisper-synced captions.

## Current Architecture

### Core Components
- **synth.py** - Main orchestrator
- **config/settings.py** - All configuration
- **services/** - AI services (OpenAI, Whisper, Caching, Characters, Captions)
- **video/** - Video composition and rendering

### Key Features Implemented
1. **Image Generation** - DALL-E 3 with character consistency
2. **Audio Generation** - OpenAI TTS with voice selection
3. **Camera Movement** - Ken Burns effects (zoom, pan)
4. **Real-time Captions** - Single word pop with Whisper timing
5. **Smart Caching** - Avoids regenerating identical content
6. **Whisper Integration** - Professional speech-to-caption sync

## Quick Start
```bash
# Normal run (uses cache)
python synth.py

# Force regenerate images
python synth.py --regenerate-images

# Check cache stats
python synth.py --cache-stats
```

## Recent Commits History
- **Commit 1**: Basic video generation pipeline
- **Commit 2**: Camera movement (Ken Burns effects)
- **Commit 3**: Real-time captions + Whisper + Caching

## Current Status
✅ Working: Full pipeline with Whisper timing
✅ Working: Smart caching system saves 99% cost on iterations
✅ Working: Professional caption sync
⚠️ Next: [See ROADMAP.md]

## Configuration
Key settings in `config/settings.py`:
- `ENABLE_CACHE` - Smart caching (default: True)
- `ENABLE_CAPTIONS` - Word-by-word captions (default: True)  
- `ENABLE_WHISPER_TIMING` - Professional timing (default: True)
- `CAPTION_FONT` - Font selection (default: Montserrat-Bold)

## Troubleshooting
- **Font issues**: Install Montserrat or uses Helvetica fallback
- **API costs**: Enable caching to avoid regeneration
- **Timing issues**: Whisper falls back to equal timing if validation fails
