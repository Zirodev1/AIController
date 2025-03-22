"""
Core emotion processing engine.
"""
from typing import Dict, Any, List, Optional
import json
import random

class EmotionEngine:
    def __init__(self):
        """Initialize the emotion engine with default emotional state."""
        self.emotional_state = {
            'emotions': {
                'joy': 0.0,
                'sadness': 0.0,
                'anger': 0.0,
                'fear': 0.0,
                'surprise': 0.0,
                'love': 0.0,
                'excitement': 0.0,
                'contentment': 0.0
            },
            'primary_emotion': 'neutral',
            'intensity': 0.0,
            'personality': 'balanced'
        }
        
        # Emotion decay rate (per update)
        self.decay_rate = 0.1
        
        # Personality settings
        self.personality_type = 'balanced'
        self.personality_traits = {
            'balanced': {
                'emotional_sensitivity': 0.5,
                'response_intensity': 0.5,
                'decay_modifier': 1.0
            },
            'passionate': {
                'emotional_sensitivity': 0.8,
                'response_intensity': 0.9,
                'decay_modifier': 0.7
            },
            'reserved': {
                'emotional_sensitivity': 0.3,
                'response_intensity': 0.4,
                'decay_modifier': 1.3
            }
        }

    def get_emotional_state(self) -> dict:
        """Get the current emotional state."""
        return self.emotional_state.copy()

    def process_text(self, text: str) -> None:
        """Process input text and update emotional state."""
        # Simple emotion detection based on keywords
        text = text.lower()
        
        # Update emotions based on keywords
        self._update_emotion('joy', text, ['happy', 'joy', 'excited', 'glad', 'wonderful'])
        self._update_emotion('sadness', text, ['sad', 'unhappy', 'depressed', 'miserable'])
        self._update_emotion('anger', text, ['angry', 'mad', 'furious', 'annoyed'])
        self._update_emotion('fear', text, ['afraid', 'scared', 'fearful', 'worried'])
        self._update_emotion('surprise', text, ['surprised', 'shocked', 'amazed'])
        self._update_emotion('love', text, ['love', 'adore', 'cherish', 'passionate'])
        self._update_emotion('excitement', text, ['excited', 'thrilled', 'enthusiastic'])
        self._update_emotion('contentment', text, ['content', 'satisfied', 'peaceful'])
        
        # Update primary emotion
        self._update_primary_emotion()
        
        # Apply emotional decay
        self._apply_decay()

    def _update_emotion(self, emotion: str, text: str, keywords: list) -> None:
        """Update specific emotion based on keywords."""
        sensitivity = self.personality_traits[self.personality_type]['emotional_sensitivity']
        intensity = self.personality_traits[self.personality_type]['response_intensity']
        
        for keyword in keywords:
            if keyword in text:
                current_value = self.emotional_state['emotions'][emotion]
                increase = sensitivity * intensity
                self.emotional_state['emotions'][emotion] = min(1.0, current_value + increase)

    def _update_primary_emotion(self) -> None:
        """Update the primary emotion based on current emotional state."""
        emotions = self.emotional_state['emotions']
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        
        if max_emotion[1] > 0.2:  # Threshold for emotion to be considered primary
            self.emotional_state['primary_emotion'] = max_emotion[0]
            self.emotional_state['intensity'] = max_emotion[1]
        else:
            self.emotional_state['primary_emotion'] = 'neutral'
            self.emotional_state['intensity'] = 0.0

    def _apply_decay(self) -> None:
        """Apply emotional decay to all emotions."""
        decay_modifier = self.personality_traits[self.personality_type]['decay_modifier']
        adjusted_decay = self.decay_rate * decay_modifier
        
        for emotion in self.emotional_state['emotions']:
            current_value = self.emotional_state['emotions'][emotion]
            self.emotional_state['emotions'][emotion] = max(0.0, current_value - adjusted_decay)

    def set_personality(self, personality_type: str) -> bool:
        """Set the AI's personality type."""
        if personality_type in self.personality_traits:
            self.personality_type = personality_type
            self.emotional_state['personality'] = personality_type
            return True
        return False

    def reset_emotional_state(self) -> None:
        """Reset emotional state to neutral."""
        for emotion in self.emotional_state['emotions']:
            self.emotional_state['emotions'][emotion] = 0.0
        self.emotional_state['primary_emotion'] = 'neutral'
        self.emotional_state['intensity'] = 0.0

    def simulate_user_emotion(self, emotion: str) -> None:
        """Simulate receiving an emotion from the user."""
        emotion = emotion.lower()
        if emotion in self.emotional_state['emotions']:
            # Increase the specified emotion
            self.emotional_state['emotions'][emotion] += 0.4
            
            # Adjust related emotions
            if emotion == 'joy':
                self.emotional_state['emotions']['sadness'] -= 0.2
                self.emotional_state['emotions']['excitement'] += 0.2
            elif emotion == 'sadness':
                self.emotional_state['emotions']['joy'] -= 0.2
                self.emotional_state['emotions']['intensity'] += 0.1
            elif emotion == 'anger':
                self.emotional_state['emotions']['intensity'] -= 0.3
                self.emotional_state['emotions']['joy'] -= 0.2
                
            # Normalize emotions
            self._normalize_emotions()
            
    def update_environment(self, env_data: Dict[str, Any]) -> None:
        """Update emotional state based on environmental factors."""
        # Process environmental factors
        if 'brightness' in env_data:
            if env_data['brightness'] > 0.7:
                self.emotional_state['emotions']['joy'] += 0.1
                self.emotional_state['emotions']['excitement'] += 0.1
            elif env_data['brightness'] < 0.3:
                self.emotional_state['emotions']['intensity'] += 0.1
                
        if 'noise_level' in env_data:
            if env_data['noise_level'] > 0.7:
                self.emotional_state['emotions']['excitement'] += 0.2
                self.emotional_state['emotions']['intensity'] -= 0.2
            elif env_data['noise_level'] < 0.3:
                self.emotional_state['emotions']['intensity'] += 0.2
                
        if 'temperature' in env_data:
            if env_data['temperature'] > 28:  # Too hot
                self.emotional_state['emotions']['anger'] += 0.1
                self.emotional_state['emotions']['intensity'] -= 0.1
            elif env_data['temperature'] < 18:  # Too cold
                self.emotional_state['emotions']['sadness'] += 0.1
                
        # Normalize emotions
        self._normalize_emotions()
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current emotional state."""
        # Find the primary emotion (highest value)
        primary_emotion = max(self.emotional_state['emotions'].items(), key=lambda x: x[1])[0]
        
        return {
            'emotions': self.emotional_state['emotions'],
            'primary_emotion': primary_emotion,
            'personality': self.emotional_state['personality']
        }
        
    def _normalize_emotions(self) -> None:
        """Normalize emotion values to be between 0 and 1."""
        # Ensure all emotions are between 0 and 1
        for emotion in self.emotional_state['emotions']:
            self.emotional_state['emotions'][emotion] = max(0.0, min(1.0, self.emotional_state['emotions'][emotion]))
            
        # Decay emotions slightly towards neutral
        for emotion in self.emotional_state['emotions']:
            if emotion not in ['intensity', 'primary_emotion']:
                self.emotional_state['emotions'][emotion] *= 0.95  # Slight decay
                
    def get_emotional_history(self) -> List[Dict[str, Any]]:
        """Get the history of emotional states."""
        return self.history 