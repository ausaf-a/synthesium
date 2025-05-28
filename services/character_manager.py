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
    
    def generate_character_sheet_prompt(self) -> str:
        """
        Generate a prompt for creating a character reference sheet.
        Useful for establishing the character design before scenes.
        """
        return f"{self.character_description}, character reference sheet showing multiple angles and poses, {self.style_anchor}"
