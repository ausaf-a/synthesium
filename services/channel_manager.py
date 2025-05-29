import json
import random
import os
from typing import Dict, List, Optional
from pathlib import Path

class ChannelManager:
    """
    Manages content channels defined in JSON files.
    Discovers channels from ./channels/ directory structure.
    """
    
    def __init__(self):
        self.channels_base_dir = Path("channels")
        self.channels_base_dir.mkdir(exist_ok=True)
        
        # Discover available channels
        self.available_channels = self._discover_channels()
    
    def _discover_channels(self) -> Dict:
        """
        Discover all channels by scanning the channels directory.
        
        Returns:
            Dictionary of channel_id -> channel_config
        """
        channels = {}
        
        if not self.channels_base_dir.exists():
            return channels
        
        for channel_dir in self.channels_base_dir.iterdir():
            if channel_dir.is_dir():
                config_file = channel_dir / "config.json"
                
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        
                        channels[config["channel_id"]] = {
                            "config": config,
                            "path": channel_dir
                        }
                        
                        print(f"📺 Discovered channel: {config['name']}")
                        
                    except Exception as e:
                        print(f"⚠️  Error loading channel {channel_dir.name}: {e}")
        
        return channels
    
    def get_available_channels(self) -> Dict:
        """Get list of all available channels."""
        result = {}
        
        for channel_id, channel_data in self.available_channels.items():
            config = channel_data["config"]
            state = self._load_channel_state(channel_id)
            
            result[channel_id] = {
                "name": config["name"],
                "description": config["description"],
                "type": config["type"],
                "episode_count": state.get("episode_count", 1),
                "videos_generated": len(self._get_existing_videos(channel_id))
            }
        
        return result
    
    def _load_channel_state(self, channel_id: str) -> Dict:
        """Load persistent state for a channel from config.json."""
        if channel_id not in self.available_channels:
            return {}
        
        config = self.available_channels[channel_id]["config"]
        return config.get("state", {})
    
    def _save_channel_state(self, channel_id: str, state: Dict):
        """Save persistent state back to config.json."""
        if channel_id not in self.available_channels:
            return
        
        channel_path = self.available_channels[channel_id]["path"]
        config_file = channel_path / "config.json"
        
        try:
            # Load current config
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update state
            config["state"] = state
            
            # Save back
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save channel state: {e}")
    
    def _get_existing_videos(self, channel_id: str) -> List[str]:
        """Get list of existing video directories for a channel (only completed ones)."""
        if channel_id not in self.available_channels:
            return []
        
        channel_path = self.available_channels[channel_id]["path"]
        videos_dir = channel_path / "videos"
        
        if not videos_dir.exists():
            return []
        
        completed_videos = []
        for video_dir in videos_dir.iterdir():
            if video_dir.is_dir() and video_dir.name.isdigit():
                # Check if video file exists (episode is complete)
                video_files = list(video_dir.glob("episode_*.mp4"))
                if video_files:  # Episode is complete
                    completed_videos.append(video_dir.name)
        
        return sorted(completed_videos, key=lambda x: int(x))
    
    def _get_incomplete_episode(self, channel_id: str) -> Optional[str]:
        """Find the first incomplete episode (has script but no video)."""
        if channel_id not in self.available_channels:
            return None
        
        channel_path = self.available_channels[channel_id]["path"]
        videos_dir = channel_path / "videos"
        
        if not videos_dir.exists():
            return None
        
        for video_dir in sorted(videos_dir.iterdir(), key=lambda x: x.name):
            if video_dir.is_dir() and video_dir.name.isdigit():
                script_file = video_dir / "script.json"
                video_files = list(video_dir.glob("episode_*.mp4"))
                
                # Has script but no video = incomplete
                if script_file.exists() and not video_files:
                    return video_dir.name
        
        return None
    
    def _get_next_video_number(self, channel_id: str) -> str:
        """Get the next video number for a channel."""
        existing_videos = self._get_existing_videos(channel_id)
        
        if not existing_videos:
            return "001"
        
        last_number = int(existing_videos[-1])
        return f"{last_number + 1:03d}"
    
    def load_character(self, channel_id: str) -> Dict:
        """
        Load character configuration for a channel.
        
        Args:
            channel_id: ID of the channel
            
        Returns:
            Character configuration dictionary
        """
        if channel_id not in self.available_channels:
            raise ValueError(f"Channel '{channel_id}' not found")
        
        channel_path = self.available_channels[channel_id]["path"]
        character_file = channel_path / "character" / "character.json"
        
        if not character_file.exists():
            raise ValueError(f"Character file not found for channel '{channel_id}'")
        
        try:
            with open(character_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading character for channel '{channel_id}': {e}")
    
    def generate_episode_script(self, channel_id: str, custom_topic: str = None) -> Dict:
        """
        Generate a script for the next episode of a channel.
        Checks for incomplete episodes first and resumes them.
        
        Args:
            channel_id: ID of the channel
            custom_topic: Optional custom topic, otherwise picks from pool
            
        Returns:
            Dictionary with episode script and metadata
        """
        if channel_id not in self.available_channels:
            raise ValueError(f"Channel '{channel_id}' not found")
        
        config = self.available_channels[channel_id]["config"]
        state = self._load_channel_state(channel_id)
        character = self.load_character(channel_id)
        
        # Check for incomplete episodes first
        incomplete_episode = self._get_incomplete_episode(channel_id)
        
        if incomplete_episode:
            print(f"🔄 Found incomplete episode {incomplete_episode}, resuming...")
            
            # Load existing script from incomplete episode
            channel_path = self.available_channels[channel_id]["path"]
            episode_dir = channel_path / "videos" / incomplete_episode
            script_file = episode_dir / "script.json"
            
            try:
                with open(script_file, 'r') as f:
                    script_data = json.load(f)
                
                return {
                    "channel_id": channel_id,
                    "channel_name": config["name"],
                    "episode_number": script_data["episode_number"],
                    "video_number": incomplete_episode,
                    "topic": script_data["topic"],
                    "script": script_data["scenes"],
                    "character": character,
                    "audio_settings": config.get("audio_settings", {}),
                    "video_dir": str(episode_dir),
                    "is_resume": True
                }
            except Exception as e:
                print(f"⚠️  Error loading incomplete episode {incomplete_episode}: {e}")
                print("Creating new episode instead...")
        
        # No incomplete episodes, create new one
        print(f"🎆 Creating new episode...")
        
        # Select topic
        if custom_topic:
            topic = custom_topic
        else:
            # Pick random topic that hasn't been used recently
            topic_pool = config["content_generation"]["topic_pool"]
            previous_topics = state.get("previous_topics", [])
            
            available_topics = [
                t for t in topic_pool 
                if t not in previous_topics[-3:]  # Avoid last 3
            ]
            
            if not available_topics:
                available_topics = topic_pool  # Reset if all used
            
            topic = random.choice(available_topics)
        
        # Generate content using master prompt
        master_prompt = config["content_generation"]["master_prompt"].format(
            episode_count=state.get("episode_count", 1),
            topic=topic
        )
        
        # Use OpenAI to generate the script
        script_content = self._generate_script_with_ai(master_prompt, config, character)
        
        # Get next video number
        video_number = self._get_next_video_number(channel_id)
        
        # Create video directory
        channel_path = self.available_channels[channel_id]["path"]
        video_dir = channel_path / "videos" / video_number
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Save script to video directory
        script_file = video_dir / "script.json"
        script_data = {
            "episode_number": int(video_number),
            "topic": topic,
            "scenes": script_content,
            "character": character,
            "generated_at": str(Path().cwd()),
            "channel_config": config
        }
        
        with open(script_file, 'w') as f:
            json.dump(script_data, f, indent=2)
        
        # Update channel state
        new_state = state.copy()
        new_state["episode_count"] = new_state.get("episode_count", 1) + 1
        
        if "previous_topics" not in new_state:
            new_state["previous_topics"] = []
        new_state["previous_topics"].append(topic)
        
        # Keep only last 10 topics in memory
        if len(new_state["previous_topics"]) > 10:
            new_state["previous_topics"] = new_state["previous_topics"][-10:]
        
        self._save_channel_state(channel_id, new_state)
        
        return {
            "channel_id": channel_id,
            "channel_name": config["name"],
            "episode_number": int(video_number),
            "video_number": video_number,
            "topic": topic,
            "script": script_content,
            "character": character,
            "audio_settings": config.get("audio_settings", {}),
            "video_dir": str(video_dir)
        }
    
    def _generate_script_with_ai(self, master_prompt: str, config: Dict, character: Dict) -> List[Dict]:
        """
        Generate script content using OpenAI based on master prompt and character.
        
        Args:
            master_prompt: The formatted prompt for content generation
            config: Channel configuration
            character: Character configuration
            
        Returns:
            List of scene dictionaries
        """
        try:
            from services.openai_service import OpenAIService
            
            # Initialize OpenAI service
            openai_service = OpenAIService()
            
            # Build character visual description
            visual_style = character["visual_style"]
            character_description = f"{visual_style['base_description']}, {visual_style['lighting']}, {visual_style['background']}, {visual_style['character_features']}"
            
            # Create full prompt for script generation
            script_prompt = f"""{master_prompt}
            
            Character Visual Style: {character_description}
            Character Mood: {visual_style['mood']}
            
            Respond with exactly 5 scenes in this JSON format:
            {{
                "scenes": [
                    {{
                        "sceneDescription": "Visual description for image generation using the character style",
                        "voiceoverText": "What the character says during this scene"
                    }}
                ]
            }}
            
            Make each scene visually distinct and escalate the intensity. Each scene's voiceoverText should be 10-25 words maximum for good pacing. Include the character's visual style in each scene description."""
            
            response = openai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a creative content generator specializing in viral short-form video content."},
                    {"role": "user", "content": script_prompt}
                ],
                temperature=0.8
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            print(f"Debug: Full AI Response:\n{content}\n")  # Show full response
            
            # Clean up the content first
            content = content.strip()
            
            # Try to extract JSON from response (handle multiple formats)
            import re
            
            # First try: Look for JSON in code blocks
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Second try: Look for any complete JSON-like structure
                json_match = re.search(r'({\s*"scenes"\s*:\s*\[.*?\]\s*})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Third try: Extract just the scenes array and wrap it
                    scenes_match = re.search(r'"scenes"\s*:\s*(\[.*?\])', content, re.DOTALL)
                    if scenes_match:
                        json_str = '{"scenes": ' + scenes_match.group(1) + '}'
                    else:
                        print("❌ Could not find valid JSON structure in AI response")
                        print("Using fallback script for this episode")
                        return self._get_fallback_script(character)
            
            try:
                # Clean up common JSON issues
                json_str = json_str.replace('\n', ' ').replace('\t', ' ')
                json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
                
                script_data = json.loads(json_str)
                scenes = script_data.get("scenes", [])
                if scenes and len(scenes) == 5:
                    print(f"✅ Successfully parsed {len(scenes)} scenes from AI")
                    return scenes
                else:
                    print(f"⚠️  AI returned {len(scenes) if scenes else 0} scenes, expected 5")
                    print("Using fallback script for consistency")
                    return self._get_fallback_script(character)
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Attempted to parse: {json_str[:200]}...")
                print("Using fallback script")
                return self._get_fallback_script(character)
                
        except Exception as e:
            print(f"Error generating script with AI: {e}")
            return self._get_fallback_script(character)
    
    def _get_fallback_script(self, character: Dict) -> List[Dict]:
        """Fallback script if AI generation fails."""
        visual_style = character["visual_style"]
        base_desc = f"{visual_style['base_description']}, {visual_style['lighting']}"
        
        return [
            {
                "sceneDescription": f"{base_desc}, intense introduction scene",
                "voiceoverText": "Day 1,738 of my sigma journey. Today we're optimizing everything."
            },
            {
                "sceneDescription": f"{base_desc}, dramatic revelation scene with holographic charts",
                "voiceoverText": "While betas waste time, I discovered the secret to maximum efficiency."
            },
            {
                "sceneDescription": f"{base_desc}, conspiracy theory presentation with neon graphics", 
                "voiceoverText": "The mainstream doesn't want you to know this one simple trick."
            },
            {
                "sceneDescription": f"{base_desc}, intense demonstration with glowing holograms",
                "voiceoverText": "This completely changed my life and mindset forever."
            },
            {
                "sceneDescription": f"{base_desc}, dramatic conclusion with intense neon lighting",
                "voiceoverText": "Your potential is limitless. Start your grindset journey today."
            }
        ]
    
    def get_channel_stats(self, channel_id: str) -> Dict:
        """Get statistics for a specific channel."""
        if channel_id not in self.available_channels:
            return {"error": "Channel not found"}
        
        config = self.available_channels[channel_id]["config"]
        state = self._load_channel_state(channel_id)
        existing_videos = self._get_existing_videos(channel_id)
        
        return {
            "name": config["name"],
            "description": config["description"],
            "type": config["type"],
            "episodes_generated": len(existing_videos),
            "next_episode": state.get("episode_count", 1),
            "topics_used": len(state.get("previous_topics", [])),
            "available_topics": len(config["content_generation"]["topic_pool"]),
            "recent_topics": state.get("previous_topics", [])[-5:],
            "videos": existing_videos
        }
