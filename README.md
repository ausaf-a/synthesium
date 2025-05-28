# Product Requirements Document (PRD)

**Project Name:** Synthesium Video Generator

**Goal:** Create short-form, narrative-driven videos composed of AI-generated images and voiceovers, optimized for YouTube Shorts.

---

## Features

- **Script Ingestion:** Accepts a structured list of scenes with descriptions and narration.
- **Image Generation:** Converts textual prompts into images using AI models (e.g., Stable Diffusion) or APIs like Unsplash.
- **Voiceover Synthesis:** Generates voiceovers using TTS engines (e.g., gTTS, Bark, or Tortoise TTS).
- **Clip Composition:** Combines images and narration into video clips using `moviepy`, with optional background music.
- **Final Video Assembly:** Stitches individual scene clips into a cohesive video.

---

## Technical Requirements

- **Python Version:** 3.8+
- **Libraries/Tools:**
  - `moviepy` for video editing
  - `gTTS` or other TTS engines for voice generation
  - `requests` for downloading images
  - Optional: Local AI models for advanced visuals or voices

---

## Success Criteria

- **Performance:** Generate a 15-second video in under 2 minutes.
- **Synchronization:** Voiceover and visuals are aligned.
- **Clarity:** Script flow is preserved and understandable.
- **Output Format:** YouTube Shorts-ready (vertical format, <60 seconds).

---

## Example Script
```python
script = [
    {
        "sceneDescription": "A lonely robot sits on a rooftop watching the city lights.",
        "voiceoverText": "He was built to serve, but all he wanted was to feel."
    },
    {
        "sceneDescription": "Raindrops fall on his metal shell as neon signs flicker below.",
        "voiceoverText": "The city pulsed with life—something he could never truly grasp."
    },
    {
        "sceneDescription": "He watches a couple sharing an umbrella across the street.",
        "voiceoverText": "Love, warmth, connection—it all seemed so distant."
    },
    {
        "sceneDescription": "A small cat curls up beside him, purring softly.",
        "voiceoverText": "And yet, in that moment, something stirred within him."
    },
    {
        "sceneDescription": "The robot gently pets the cat as the rain continues to fall.",
        "voiceoverText": "Maybe feeling wasn't programmed—but maybe it didn't need to be."
    }
]
```


## Usage
```bash
pip install -r requirements.txt
python synth.py
```