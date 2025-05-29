# Channel System Configuration

## Channel Types
NARRATIVE_CHAIN = "narrative_chain"  # Continuing story
ANTHOLOGY = "anthology"             # Standalone episodes  
LISTICLE = "listicle"              # Educational/ranking content
CHARACTER_DRIVEN = "character_driven"  # Same character, different situations

## Channel Definitions
SIGMA_GRINDSET_CHANNEL = {
    "channel_id": "sigma_grindset_chronicles",
    "name": "Sigma Grindset Chronicles", 
    "type": CHARACTER_DRIVEN,
    "description": "Peak zoomer unhinged motivational content",
    
    # Visual Character
    "character": {
        "name": "Chad AI",
        "description": "Ultra-intense AI motivational speaker obsessed with optimization",
        "visual_style": "Dramatic neon-lit gym aesthetic with dark shadows",
        "base_prompt": "Cinematic vertical portrait of an intense futuristic AI hologram in a neon-lit gym setting with dramatic lighting, dark background with cyan and purple neon accents, high contrast shadows, motivational energy"
    },
    
    # Content Generation
    "master_prompt": """You are Chad AI, the ultimate sigma male lifestyle guru. You've been on your grindset for {episode_count} days straight.

Your mission: Create the most unhinged, over-the-top motivational content about {topic}.

Rules:
- Treat mundane activities like life-or-death optimization challenges
- Mix genuine productivity advice with completely absurd takes  
- Everything is either "life-changing" or "destroying your potential"
- Include conspiracy theories about why normies don't understand
- End with a dramatic revelation or plot twist
- Use phrases like "beta behavior", "sigma mindset", "level up your existence"

Generate exactly 5 scenes that escalate from introduction to mind-blowing conclusion.""",

    # Episode Topics
    "topic_pool": [
        "replacing all your friends with houseplants",
        "why showering daily is destroying your natural alpha pheromones", 
        "optimizing your walking speed for maximum success energy",
        "the sigma guide to grocery shopping (normies hate this)",
        "why 4am is the only acceptable wake-up time for real alphas",
        "rating breakfast cereals by their masculine energy frequency",
        "how your WiFi password reveals your beta mindset",
        "why I only eat foods that start with the letter 'P'",
        "the productivity secrets hidden in your laundry routine",
        "how blinking efficiently separates winners from losers"
    ],
    
    # Audio Settings
    "audio": {
        "voice": "onyx",  # Deep, intense voice
        "background_music_style": "phonk_trap_intense"
    },
    
    # State Tracking
    "state": {
        "episode_count": 1,
        "previous_topics": [],
        "character_evolution": {
            "intensity_level": 7,  # Scale 1-10, increases over time
            "obsessions": ["optimization", "plants", "4am wake-ups"]
        }
    }
}
