# Development Guide

## Quick Onboarding for New Chat Sessions

### Project Overview
Synthesium is an AI video generator that creates narrative-driven videos with:
- DALL-E generated images
- OpenAI TTS voiceovers  
- Whisper-synced captions
- Dynamic camera movements
- Smart caching system

### Architecture Pattern
The codebase follows a service-oriented architecture:
- **Services** handle AI integrations and data processing
- **Video module** handles composition and rendering
- **Config** centralizes all settings
- **Caching** prevents expensive regeneration

### Key Design Decisions Made
1. **Single word pop captions** - More engaging than multi-line
2. **Center positioning** - Better than bottom for vertical videos
3. **Random camera movements** - Adds variety without manual control
4. **Content-based caching** - Hash scene content to avoid duplicates
5. **Whisper integration** - Professional timing worth the small cost

### Common Development Patterns

#### Adding New Features
1. Add settings to `config/settings.py`
2. Create/modify service in `services/`
3. Integrate in `video/composer.py` or `synth.py`
4. Update documentation

#### Testing Changes
```bash
# Test with cache (fast iteration)
python synth.py

# Test without cache (full generation)
python synth.py --regenerate-all
```

#### Cost-Conscious Development
- Always use caching during development
- Only regenerate what you're testing
- Whisper costs ~$0.003 per video (negligible)
- Image costs are the main expense ($0.04 each)

### Debugging Common Issues

#### Font Problems
- Montserrat-Bold is preferred, Helvetica-Bold is fallback
- Error handling catches font failures gracefully

#### Timing Issues  
- Whisper validation is forgiving (60% threshold)
- Falls back to equal timing if Whisper fails
- Punctuation is normalized for validation

#### Cache Issues
```bash
python synth.py --clear-cache all  # Nuclear option
python synth.py --cache-stats      # Check status
```

### Code Style
- Service classes handle specific domains
- Error handling with try/catch and fallbacks
- Print statements for user feedback
- Type hints for clarity

### Git Workflow (if using version control)
- Main branch should always work
- Feature branches for new capabilities
- Document changes in PROJECT_STATE.md

## Quick Start for New Contributors
1. Read PROJECT_STATE.md for current status
2. Check ROADMAP.md for planned features  
3. Set up environment variables (.env file)
4. Run `python synth.py --cache-stats` to verify setup
5. Make changes and test with cache for speed
