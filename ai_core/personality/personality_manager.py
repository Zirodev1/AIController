"""
Personality manager for handling different personas across platforms.
"""
from enum import Enum
from typing import Dict, Optional
import json
import logging

class PersonaType(Enum):
    TWITTER = "twitter"  # Professional, friendly, engaging
    ONLYFANS = "onlyfans"  # Adult content, flirty, intimate

class PersonalityManager:
    def __init__(self):
        self.personas: Dict[PersonaType, dict] = {}
        self.current_persona: Optional[PersonaType] = None
        self.logger = logging.getLogger(__name__)
        
    def load_persona(self, persona_type: PersonaType, config_path: str):
        """Load a persona configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.personas[persona_type] = config
                self.logger.info(f"Loaded {persona_type.value} persona")
                return True
        except Exception as e:
            self.logger.error(f"Error loading {persona_type.value} persona: {str(e)}")
            return False
            
    def set_active_persona(self, persona_type: PersonaType):
        """Set the currently active persona."""
        if persona_type in self.personas:
            self.current_persona = persona_type
            self.logger.info(f"Set active persona to {persona_type.value}")
            return True
        return False
        
    def get_persona_config(self) -> Optional[dict]:
        """Get configuration for the current persona."""
        if not self.current_persona:
            return None
        return self.personas[self.current_persona]
        
    def get_response_style(self) -> dict:
        """Get the response style for the current persona."""
        if not self.current_persona:
            return {}
        return self.personas[self.current_persona].get('response_style', {})
        
    def get_content_rules(self) -> dict:
        """Get content rules for the current persona."""
        if not self.current_persona:
            return {}
        return self.personas[self.current_persona].get('content_rules', {})
        
    def get_interaction_style(self) -> dict:
        """Get interaction style for the current persona."""
        if not self.current_persona:
            return {}
        return self.personas[self.current_persona].get('interaction_style', {})
        
    def validate_content(self, content: str) -> bool:
        """Validate content against current persona's rules."""
        if not self.current_persona:
            return False
            
        rules = self.get_content_rules()
        # TODO: Implement content validation logic
        return True
        
    def format_response(self, response: str) -> str:
        """Format response according to current persona's style."""
        if not self.current_persona:
            return response
            
        style = self.get_response_style()
        # TODO: Implement response formatting logic
        return response 