"""
Emotion Engine for processing and managing emotional states.
"""
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .emotional_states import EmotionalState, ComplexEmotionalSystem

class EmotionEngine:
    def __init__(self):
        """Initialize the emotion engine with default emotional state."""
        self.emotional_system = ComplexEmotionalSystem()
        self.current_state = EmotionalState()
        self.emotion_history: List[Dict[str, Any]] = []
        self.context_history: List[Dict[str, Any]] = []
        self.last_update_time = 0
        self.emotional_decay_rate = 0.1  # Rate at which emotions decay over time
        
    def process_text(self, text: str) -> None:
        """Process text input and update emotional state."""
        # Update state with text input
        self.update_state({
            'text': {'text': text},
            'context': {'context_type': 'text_input'}
        })
        
    def simulate_user_emotion(self, emotion: str) -> None:
        """Simulate user emotion and update emotional state."""
        # Update state with user emotion
        self.update_state({
            'user_emotion': {emotion: 0.8},
            'context': {'context_type': 'user_emotion'}
        })
        
    def update_environment(self, env_data: Dict[str, float]) -> None:
        """Update environmental factors and adjust emotional state."""
        # Process environmental factors with more nuanced emotional reactions
        emotional_impacts = {}
        
        # Brightness affects joy and energy levels
        if 'brightness' in env_data:
            brightness = env_data['brightness']
            emotional_impacts['joy'] = brightness * 0.3
            emotional_impacts['energy'] = brightness * 0.2
            if brightness < 0.3:
                emotional_impacts['sadness'] = 0.2
                emotional_impacts['fear'] = 0.1
                
        # Noise level affects stress and focus
        if 'noise_level' in env_data:
            noise = env_data['noise_level']
            emotional_impacts['stress'] = noise * 0.4
            emotional_impacts['focus'] = (1 - noise) * 0.3
            if noise > 0.7:
                emotional_impacts['fear'] = 0.2
                emotional_impacts['anger'] = 0.1
                
        # Temperature affects comfort and energy
        if 'temperature' in env_data:
            temp = env_data['temperature']
            if temp > 0.8:
                emotional_impacts['stress'] = 0.2
                emotional_impacts['energy'] = -0.1
            elif temp < 0.2:
                emotional_impacts['sadness'] = 0.1
                emotional_impacts['energy'] = -0.1
                
        # Crowding affects stress and social comfort
        if 'crowding' in env_data:
            crowding = env_data['crowding']
            emotional_impacts['stress'] = crowding * 0.3
            emotional_impacts['social_comfort'] = (1 - crowding) * 0.2
            if crowding > 0.8:
                emotional_impacts['fear'] = 0.1
                emotional_impacts['anger'] = 0.1
                
        # Update state with environmental impacts
        self.update_state({
            'environment': env_data,
            'emotional_impacts': emotional_impacts,
            'context': {'context_type': 'environment'}
        })
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current emotional state in a format suitable for the LLM."""
        complex_state, confidence = self.emotional_system.get_complex_state(self.current_state)
        return {
            'complex_state': {
                'state': complex_state,
                'intensity': self.current_state.intensity
            },
            'basic_emotions': self.current_state.get_vector()
        }
        
    def reset_emotions(self) -> None:
        """Reset the emotional state to neutral."""
        self.current_state = EmotionalState()
        self.emotion_history = []
        self.context_history = []
        
    def update_state(self, data: Dict[str, Any]) -> None:
        """Update the emotional state based on new data."""
        # Apply emotional decay
        self.apply_emotional_decay()
        
        # Store current state in history
        self.emotion_history.append(self.current_state.get_vector())
        self.context_history.append(data.get('context', {}))
        
        # Update basic emotions based on input
        if 'text' in data:
            # Process text emotions (simplified for now)
            text = data['text']['text'].lower()
            if any(word in text for word in ['happy', 'excited', 'great', 'amazing']):
                self.current_state.adjust_emotion('joy', 0.3)
            elif any(word in text for word in ['sad', 'unhappy', 'terrible', 'bad']):
                self.current_state.adjust_emotion('sadness', 0.3)
                
        elif 'user_emotion' in data:
            # Empathize with user emotion
            for emotion, intensity in data['user_emotion'].items():
                self.current_state.adjust_emotion(emotion, intensity * 0.5)
                
        elif 'environment' in data:
            # Apply environmental emotional impacts
            if 'emotional_impacts' in data:
                for emotion, impact in data['emotional_impacts'].items():
                    self.current_state.adjust_emotion(emotion, impact)
                    
        # Normalize emotional intensities
        self.current_state.normalize()
        
    def apply_emotional_decay(self) -> None:
        """Apply emotional decay to all emotions."""
        for emotion in self.current_state.emotions:
            current_value = self.current_state.emotions[emotion]
            decay = current_value * self.emotional_decay_rate
            self.current_state.emotions[emotion] = max(0.0, current_value - decay)
            
    def get_emotional_history(self) -> List[Dict[str, Any]]:
        """Get the history of emotional states."""
        return self.emotion_history
        
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get the history of contexts."""
        return self.context_history 