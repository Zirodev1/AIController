"""
Core emotion processing engine.
"""
from typing import Dict, Any, List, Optional
import json
import random

class EmotionEngine:
    def __init__(self):
        """Initialize the emotion engine with default states."""
        self.emotions = {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'excited': 0.0,
            'calm': 0.5,  # Default state is calm
            'neutral': 0.5
        }
        
        self.personality = 'balanced'
        self.history = []
        
    def process_text(self, text: str) -> Optional[str]:
        """
        Process input text and update emotional state.
        Returns a response if appropriate, None otherwise.
        """
        # Update emotions based on text content
        text_lower = text.lower()
        
        # Simple keyword-based emotion detection
        if any(word in text_lower for word in ['happy', 'joy', 'great', 'wonderful', 'excited']):
            self.emotions['happy'] += 0.3
            self.emotions['excited'] += 0.2
        elif any(word in text_lower for word in ['sad', 'unhappy', 'sorry', 'unfortunate']):
            self.emotions['sad'] += 0.3
            self.emotions['calm'] -= 0.1
        elif any(word in text_lower for word in ['angry', 'mad', 'frustrated']):
            self.emotions['angry'] += 0.3
            self.emotions['calm'] -= 0.2
            
        # Normalize emotions
        self._normalize_emotions()
        
        # Add to history
        self.history.append({
            'input': text,
            'emotions': self.emotions.copy()
        })
        
        return None  # Let the LLM generate the actual response
        
    def simulate_user_emotion(self, emotion: str) -> None:
        """Simulate receiving an emotion from the user."""
        emotion = emotion.lower()
        if emotion in self.emotions:
            # Increase the specified emotion
            self.emotions[emotion] += 0.4
            
            # Adjust related emotions
            if emotion == 'happy':
                self.emotions['sad'] -= 0.2
                self.emotions['excited'] += 0.2
            elif emotion == 'sad':
                self.emotions['happy'] -= 0.2
                self.emotions['calm'] += 0.1
            elif emotion == 'angry':
                self.emotions['calm'] -= 0.3
                self.emotions['happy'] -= 0.2
                
            # Normalize emotions
            self._normalize_emotions()
            
    def update_environment(self, env_data: Dict[str, Any]) -> None:
        """Update emotional state based on environmental factors."""
        # Process environmental factors
        if 'brightness' in env_data:
            if env_data['brightness'] > 0.7:
                self.emotions['happy'] += 0.1
                self.emotions['excited'] += 0.1
            elif env_data['brightness'] < 0.3:
                self.emotions['calm'] += 0.1
                
        if 'noise_level' in env_data:
            if env_data['noise_level'] > 0.7:
                self.emotions['excited'] += 0.2
                self.emotions['calm'] -= 0.2
            elif env_data['noise_level'] < 0.3:
                self.emotions['calm'] += 0.2
                
        if 'temperature' in env_data:
            if env_data['temperature'] > 28:  # Too hot
                self.emotions['angry'] += 0.1
                self.emotions['calm'] -= 0.1
            elif env_data['temperature'] < 18:  # Too cold
                self.emotions['sad'] += 0.1
                
        # Normalize emotions
        self._normalize_emotions()
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current emotional state."""
        # Find the primary emotion (highest value)
        primary_emotion = max(self.emotions.items(), key=lambda x: x[1])[0]
        
        return {
            'emotions': self.emotions,
            'primary_emotion': primary_emotion,
            'personality': self.personality
        }
        
    def reset_emotions(self) -> None:
        """Reset emotions to default state."""
        self.emotions = {
            'happy': 0.0,
            'sad': 0.0,
            'angry': 0.0,
            'excited': 0.0,
            'calm': 0.5,
            'neutral': 0.5
        }
        
    def set_personality(self, personality_type: str) -> None:
        """Set the personality type."""
        valid_types = ['empathetic', 'analytical', 'creative', 'balanced']
        if personality_type.lower() in valid_types:
            self.personality = personality_type.lower()
            
            # Adjust emotional baseline based on personality
            if personality_type == 'empathetic':
                self.emotions['calm'] += 0.2
            elif personality_type == 'analytical':
                self.emotions['neutral'] += 0.3
            elif personality_type == 'creative':
                self.emotions['excited'] += 0.2
                
            self._normalize_emotions()
        else:
            raise ValueError(f"Invalid personality type. Must be one of: {', '.join(valid_types)}")
            
    def _normalize_emotions(self) -> None:
        """Normalize emotion values to be between 0 and 1."""
        # Ensure all emotions are between 0 and 1
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
            
        # Decay emotions slightly towards neutral
        for emotion in self.emotions:
            if emotion not in ['calm', 'neutral']:
                self.emotions[emotion] *= 0.95  # Slight decay
                
    def get_emotional_history(self) -> List[Dict[str, Any]]:
        """Get the history of emotional states."""
        return self.history 