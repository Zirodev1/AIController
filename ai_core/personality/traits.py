"""
Personality traits system for AI avatars.
"""
from typing import Dict, List, Optional
import numpy as np

class PersonalityTraits:
    def __init__(self):
        """Initialize personality traits with default values."""
        self.traits = {
            # Core personality traits (Big Five model)
            'openness': 0.5,        # Openness to experience
            'conscientiousness': 0.5,  # Organization and responsibility
            'extraversion': 0.5,    # Sociability and energy
            'agreeableness': 0.5,   # Compassion and cooperation
            'neuroticism': 0.5,     # Emotional stability
            
            # Additional traits
            'empathy': 0.5,         # Ability to understand others' emotions
            'curiosity': 0.5,       # Desire to learn and explore
            'creativity': 0.5,      # Original thinking and problem-solving
            'independence': 0.5,    # Self-reliance
            'romantic': 0.5,        # Romantic interest and affection
            
            # Social traits
            'friendliness': 0.5,    # General social warmth
            'humor': 0.5,           # Sense of humor
            'playfulness': 0.5,     # Fun-loving nature
            'loyalty': 0.5,         # Commitment to relationships
            'trust': 0.5,           # Trust in others
        }
        
        # Relationship-specific traits
        self.relationship_traits = {
            'intimacy_level': 0.0,  # Current level of intimacy
            'trust_level': 0.0,     # Trust in the user
            'attachment_style': 'secure',  # secure, anxious, or avoidant
            'romantic_interest': 0.0,  # Level of romantic interest
        }
        
    def set_trait(self, trait_name: str, value: float) -> None:
        """Set a specific trait value (0.0 to 1.0)."""
        if trait_name in self.traits:
            self.traits[trait_name] = max(0.0, min(1.0, value))
            
    def get_trait(self, trait_name: str) -> Optional[float]:
        """Get the value of a specific trait."""
        return self.traits.get(trait_name)
        
    def update_relationship_trait(self, trait_name: str, value: float) -> None:
        """Update a relationship-specific trait."""
        if trait_name in self.relationship_traits:
            self.relationship_traits[trait_name] = max(0.0, min(1.0, value))
            
    def get_all_traits(self) -> Dict[str, float]:
        """Get all personality traits."""
        return self.traits.copy()
        
    def get_relationship_traits(self) -> Dict[str, Any]:
        """Get all relationship-specific traits."""
        return self.relationship_traits.copy()
        
    def adjust_traits(self, interaction_data: Dict[str, Any]) -> None:
        """
        Adjust traits based on interactions and experiences.
        This is where personality development happens over time.
        """
        # TODO: Implement trait adjustment logic based on interactions
        pass 