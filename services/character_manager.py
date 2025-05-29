from config.settings import settings
from typing import Dict, List

class CharacterManager:
    """
    Manages character consistency across scenes by maintaining character descriptions
    and style anchors that get prepended to scene prompts.
    """
    
    def __init__(self):
        self.character_description = settings.CHARACTER_DESCRIPTION_TEMPLATE
        self.style_anchor = settings.STYLE_ANCHOR
        self.consistency_enabled = settings.CHARACTER_CONSISTENCY
    
    def enhance_scene_prompt(self, scene_description: str) -> str:
        """
        Enhance a scene description with character consistency details.
        
        Args:
            scene_description: Original scene description
            
        Returns:
            Enhanced prompt with character and style details
        """
        if not self.consistency_enabled:
            return scene_description
        
        # Build the enhanced prompt with explicit portrait orientation
        enhanced_prompt = f"{self.character_description}. {scene_description}. Vertical portrait format, tall composition. {self.style_anchor}"
        
        return enhanced_prompt
    
    def set_character_description(self, description: str):
        """Update the character description template."""
        self.character_description = description
    
    def set_style_anchor(self, style: str):
        """Update the style anchor."""
        self.style_anchor = style
    
    def get_character_info(self) -> Dict:
        """Get current character configuration."""
        return {
            'character_description': self.character_description,
            'style_anchor': self.style_anchor,
            'consistency_enabled': self.consistency_enabled
        }
    
    def set_channel_character(self, character_config: Dict):
        """
        Set character configuration from channel data.
        
        Args:
            character_config: Character configuration dictionary from channel
        """
        if not character_config:
            return
        
        visual_style = character_config.get("visual_style", {})
        
        # Build enhanced character description from channel character
        if "base_description" in visual_style:
            self.character_description = f"""{visual_style['base_description']}
            
Lighting: {visual_style.get('lighting', 'dramatic lighting')}
Background: {visual_style.get('background', 'dark background')}
Character Features: {visual_style.get('character_features', 'distinctive character')}
Mood: {visual_style.get('mood', 'intense energy')}"""
        
        # Update style anchor with channel-specific style
        if "color_palette" in visual_style:
            self.style_anchor = f"Color palette: {visual_style['color_palette']}. Style: Cinematic, high-quality, professional video production. Vertical portrait format."
        
        character_name = character_config.get("name", "Channel Character")
        print(f"📺 Using channel character: {character_name}")
        print(f"🎭 Description: {character_config.get('description', 'Custom character')}")
    
    def generate_character_sheet_prompt(self) -> str:
        """
        Generate a prompt for creating a character reference sheet.
        Useful for establishing the character design before scenes.
        """
        return f"{self.character_description}, character reference sheet showing multiple angles and poses, {self.style_anchor}"
