"""
System for defining and managing complex emotional states and their relationships.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

class EmotionalState:
    def __init__(self):
        """Initialize emotional state with basic emotions."""
        # Core emotions (Plutchik's wheel of emotions)
        self.emotions = {
            'joy': 0.0,
            'trust': 0.0,
            'fear': 0.0,
            'surprise': 0.0,
            'sadness': 0.0,
            'disgust': 0.0,
            'anger': 0.0,
            'anticipation': 0.0,
            'energy': 0.0,
            'focus': 0.0,
            'stress': 0.0,
            'social_comfort': 0.0
        }
        self.intensity = 0.5  # Overall emotional intensity
        
    def adjust_emotion(self, emotion: str, amount: float) -> None:
        """Adjust the intensity of an emotion."""
        if emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion] + amount))
            
    def normalize(self) -> None:
        """Normalize emotional intensities."""
        # Calculate the maximum value
        max_value = max(self.emotions.values())
        if max_value > 0:
            # Normalize all emotions
            for emotion in self.emotions:
                self.emotions[emotion] /= max_value
                
        # Update overall intensity
        self.intensity = np.mean(list(self.emotions.values()))
        
    def get_vector(self) -> Dict[str, float]:
        """Get the current emotional state as a vector."""
        return self.emotions.copy()
        
    def get_emotions(self) -> Dict[str, float]:
        """Get the current emotional state."""
        return self.emotions.copy()

class ComplexEmotionalSystem:
    def __init__(self):
        """Initialize the complex emotional system."""
        # Define complex emotional states and their relationships
        self.complex_states = {
            'inspired': {
                'joy': 0.7,
                'energy': 0.8,
                'focus': 0.6,
                'anticipation': 0.5
            },
            'contemplative': {
                'focus': 0.7,
                'trust': 0.5,
                'energy': 0.3,
                'social_comfort': 0.4
            },
            'empathic': {
                'trust': 0.8,
                'social_comfort': 0.7,
                'joy': 0.4,
                'energy': 0.5
            },
            'focused': {
                'focus': 0.9,
                'energy': 0.6,
                'stress': 0.2,
                'social_comfort': 0.3
            },
            'content': {
                'joy': 0.6,
                'trust': 0.5,
                'energy': 0.4,
                'social_comfort': 0.5
            },
            'excited': {
                'joy': 0.8,
                'energy': 0.9,
                'anticipation': 0.7,
                'focus': 0.5
            },
            'calm': {
                'stress': 0.1,
                'energy': 0.3,
                'social_comfort': 0.6,
                'focus': 0.4
            },
            'determined': {
                'focus': 0.8,
                'energy': 0.7,
                'stress': 0.3,
                'anticipation': 0.6
            }
        }
        
        # Personality types and their emotional thresholds
        self.personality_types = {
            'high_empathy': {
                'trust_threshold': 0.6,
                'social_comfort_weight': 1.2,
                'stress_sensitivity': 1.5
            },
            'analytical': {
                'focus_weight': 1.3,
                'energy_threshold': 0.7,
                'stress_sensitivity': 0.8
            },
            'creative': {
                'energy_weight': 1.2,
                'focus_threshold': 0.5,
                'social_comfort_sensitivity': 1.3
            },
            'balanced': {
                'trust_threshold': 0.5,
                'energy_threshold': 0.5,
                'focus_threshold': 0.5
            }
        }
        
    def get_complex_state(self, emotional_state: EmotionalState) -> Tuple[str, float]:
        """Calculate the most likely complex emotional state."""
        emotions = emotional_state.get_vector()
        best_state = 'contemplative'
        best_confidence = 0.0
        
        for state, state_emotions in self.complex_states.items():
            confidence = 0.0
            for emotion, target_value in state_emotions.items():
                if emotion in emotions:
                    # Calculate similarity between current and target emotion
                    diff = abs(emotions[emotion] - target_value)
                    confidence += 1 - diff
                    
            confidence /= len(state_emotions)
            if confidence > best_confidence:
                best_confidence = confidence
                best_state = state
                
        return best_state, best_confidence
        
    def adjust_emotional_thresholds(self, personality_type: str) -> Dict[str, float]:
        """Adjust emotional thresholds based on personality type."""
        if personality_type in self.personality_types:
            return self.personality_types[personality_type]
        return self.personality_types['balanced']
        
    def get_emotional_response(self, current_state: str, personality_type: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Generate emotional response based on current state and context."""
        # Get personality-based thresholds
        thresholds = self.adjust_emotional_thresholds(personality_type)
        
        # Initialize response
        response = {}
        
        # Process context-specific responses
        if 'user_emotion' in context:
            user_emotion = context['user_emotion']
            # Empathize with user emotion
            for emotion, intensity in user_emotion.items():
                response[emotion] = intensity * 0.5
                
        if 'environment' in context:
            env = context['environment']
            # Adjust response based on environmental factors
            if 'brightness' in env:
                response['joy'] = env['brightness'] * 0.3
                response['energy'] = env['brightness'] * 0.2
                
            if 'noise_level' in env:
                response['stress'] = env['noise_level'] * 0.4
                response['focus'] = (1 - env['noise_level']) * 0.3
                
        # Apply personality-based adjustments
        for emotion, value in response.items():
            if emotion in thresholds:
                threshold = thresholds.get(f'{emotion}_threshold', 0.5)
                weight = thresholds.get(f'{emotion}_weight', 1.0)
                response[emotion] = value * weight
                
        return response
        
    def get_emotional_chain(self, current_state: str, personality_type: str) -> List[str]:
        """
        Get likely emotional transitions based on current state and personality.
        
        Args:
            current_state: Current complex emotional state
            personality_type: Type of personality
            
        Returns:
            List of likely next emotional states
        """
        # Define emotional transition patterns
        transitions = {
            'nostalgic': ['contemplative', 'sadness', 'joy', 'reflective'],
            'determined': ['playful', 'contemplative', 'anger', 'inspired'],
            'playful': ['joy', 'curious', 'trust', 'optimistic'],
            'caring': ['joy', 'trust', 'contemplative', 'grateful'],
            'inspired': ['optimistic', 'determined', 'joy', 'playful'],
            'grateful': ['joy', 'trust', 'caring', 'optimistic'],
            'optimistic': ['joy', 'inspired', 'anticipation', 'playful'],
            'anxious': ['fear', 'contemplative', 'trust', 'overwhelmed'],
            'frustrated': ['anger', 'contemplative', 'determined', 'disappointed'],
            'lonely': ['sadness', 'anxious', 'caring', 'melancholic'],
            'overwhelmed': ['anxious', 'fear', 'contemplative', 'reflective'],
            'disappointed': ['sadness', 'frustrated', 'contemplative', 'melancholic'],
            'jealous': ['anger', 'disgust', 'frustrated', 'anxious'],
            'contemplative': ['curious', 'determined', 'nostalgic', 'reflective'],
            'curious': ['playful', 'contemplative', 'determined', 'inspired'],
            'reflective': ['contemplative', 'mindful', 'nostalgic', 'melancholic'],
            'mindful': ['contemplative', 'reflective', 'trust', 'calm'],
            'bittersweet': ['nostalgic', 'melancholic', 'joy', 'sadness'],
            'melancholic': ['sadness', 'contemplative', 'nostalgic', 'reflective']
        }
        
        # Adjust transitions based on personality
        if personality_type == 'high_empathy':
            # Add more emotional transitions and caring states
            transitions = {
                k: v + ['caring', 'trust', 'grateful'] for k, v in transitions.items()
            }
        elif personality_type == 'low_empathy':
            # Reduce emotional transitions and focus on basic emotions
            transitions = {
                k: v[:2] for k, v in transitions.items()
            }
            
        return transitions.get(current_state, [])
        
    def _update_emotional_learning(self, current_state: str, context: Dict[str, Any]) -> None:
        """
        Update emotional learning data based on current state and context.
        
        Args:
            current_state: Current complex emotional state
            context: Current context information
        """
        # Track state transitions
        if 'previous_state' in context:
            prev_state = context['previous_state']
            if prev_state not in self.emotional_learning['state_transitions']:
                self.emotional_learning['state_transitions'][prev_state] = {}
            if current_state not in self.emotional_learning['state_transitions'][prev_state]:
                self.emotional_learning['state_transitions'][prev_state][current_state] = 0
            self.emotional_learning['state_transitions'][prev_state][current_state] += 1
            
        # Track context patterns
        if 'context_type' in context:
            context_type = context['context_type']
            if context_type not in self.emotional_learning['context_patterns']:
                self.emotional_learning['context_patterns'][context_type] = {}
            if current_state not in self.emotional_learning['context_patterns'][context_type]:
                self.emotional_learning['context_patterns'][context_type][current_state] = 0
            self.emotional_learning['context_patterns'][context_type][current_state] += 1
            
        # Track user interactions
        if 'user_interaction' in context:
            interaction = context['user_interaction']
            if interaction not in self.emotional_learning['user_interactions']:
                self.emotional_learning['user_interactions'][interaction] = {}
            if current_state not in self.emotional_learning['user_interactions'][interaction]:
                self.emotional_learning['user_interactions'][interaction][current_state] = 0
            self.emotional_learning['user_interactions'][interaction][current_state] += 1 