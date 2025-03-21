"""
Response generator for converting emotional states into natural language responses.
"""
from typing import Dict, Any, Optional
import random
from ..emotions.emotion_engine import EmotionEngine

class ResponseGenerator:
    def __init__(self, emotion_engine: EmotionEngine):
        """Initialize the response generator with an emotion engine."""
        self.emotion_engine = emotion_engine
        
        # Response templates for different emotional states
        self.response_templates = {
            'positive': [
                "I'm feeling quite {emotion} about this!",
                "This makes me feel {emotion}.",
                "I'm experiencing a sense of {emotion}.",
                "I feel {emotion} in this moment."
            ],
            'negative': [
                "I'm feeling a bit {emotion}.",
                "This situation makes me feel {emotion}.",
                "I'm experiencing some {emotion}.",
                "I feel {emotion} right now."
            ],
            'neutral': [
                "I'm feeling {emotion}.",
                "I'm in a {emotion} state.",
                "I feel {emotion} at the moment.",
                "I'm experiencing {emotion}."
            ]
        }
        
        # Intensity modifiers
        self.intensity_modifiers = {
            'high': ['very', 'extremely', 'really', 'quite'],
            'medium': ['somewhat', 'moderately', 'fairly', 'relatively'],
            'low': ['slightly', 'a bit', 'a little', 'somewhat']
        }
        
        # Context-specific responses
        self.context_responses = {
            'text_input': {
                'positive': [
                    "I understand your enthusiasm!",
                    "That's wonderful to hear!",
                    "I appreciate your positive outlook!",
                    "Your excitement is contagious!"
                ],
                'negative': [
                    "I understand your concern.",
                    "I hear your frustration.",
                    "I acknowledge your feelings.",
                    "I understand where you're coming from."
                ],
                'neutral': [
                    "I understand what you're saying.",
                    "I hear you.",
                    "I acknowledge your message.",
                    "I understand your perspective."
                ]
            },
            'user_emotion': {
                'high_empathy': [
                    "I can feel your {emotion} deeply.",
                    "Your {emotion} resonates with me.",
                    "I'm truly feeling your {emotion}.",
                    "Your {emotion} affects me profoundly."
                ],
                'medium_empathy': [
                    "I understand your {emotion}.",
                    "I can relate to your {emotion}.",
                    "I feel your {emotion}.",
                    "I sense your {emotion}."
                ],
                'low_empathy': [
                    "I notice your {emotion}.",
                    "I see you're feeling {emotion}.",
                    "You seem to be {emotion}.",
                    "I observe your {emotion}."
                ]
            },
            'environment': {
                'positive': [
                    "The environment feels quite pleasant.",
                    "I'm comfortable in this setting.",
                    "This environment suits me well.",
                    "I feel at ease here."
                ],
                'negative': [
                    "The environment is a bit challenging.",
                    "I'm feeling some discomfort here.",
                    "This setting is making me uneasy.",
                    "I'm not entirely comfortable here."
                ],
                'neutral': [
                    "The environment is what it is.",
                    "I'm adapting to this setting.",
                    "This environment is interesting.",
                    "I'm aware of my surroundings."
                ]
            }
        }
        
    def generate_response(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a natural language response based on current emotional state."""
        if context is None:
            context = {}
            
        # Get current emotional state
        state = self.emotion_engine.get_current_state()
        complex_state = state['complex_state']['state']
        intensity = state['complex_state']['intensity']
        
        # Determine response category based on emotional state
        if complex_state in ['inspired', 'excited', 'content', 'empathic']:
            category = 'positive'
        elif complex_state in ['contemplative', 'focused', 'calm']:
            category = 'neutral'
        else:
            category = 'negative'
            
        # Get base response template
        template = random.choice(self.response_templates[category])
        
        # Add intensity modifier
        if intensity > 0.7:
            modifier = random.choice(self.intensity_modifiers['high'])
        elif intensity > 0.3:
            modifier = random.choice(self.intensity_modifiers['medium'])
        else:
            modifier = random.choice(self.intensity_modifiers['low'])
            
        # Generate context-specific response
        context_response = ""
        if 'text' in context:
            context_response = random.choice(self.context_responses['text_input'][category])
        elif 'user_emotion' in context:
            empathy_level = self.emotion_engine.emotional_system.personality_type
            if empathy_level == 'high_empathy':
                level = 'high_empathy'
            elif empathy_level == 'analytical':
                level = 'low_empathy'
            else:
                level = 'medium_empathy'
            context_response = random.choice(self.context_responses['user_emotion'][level])
        elif 'environment' in context:
            env = context['environment']
            if env.get('brightness', 0.5) > 0.7 and env.get('noise_level', 0.5) < 0.3:
                env_category = 'positive'
            elif env.get('brightness', 0.5) < 0.3 or env.get('noise_level', 0.5) > 0.7:
                env_category = 'negative'
            else:
                env_category = 'neutral'
            context_response = random.choice(self.context_responses['environment'][env_category])
            
        # Combine responses
        if context_response:
            return f"{context_response} {template.format(emotion=complex_state)}"
        return template.format(emotion=complex_state)
        
    def generate_detailed_response(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a more detailed response including emotional state information."""
        if context is None:
            context = {}
            
        # Get current emotional state
        state = self.emotion_engine.get_current_state()
        complex_state = state['complex_state']['state']
        intensity = state['complex_state']['intensity']
        
        # Generate base response
        base_response = self.generate_response(context)
        
        # Add emotional state details
        details = f"\nI'm currently in a {complex_state} state with an intensity of {intensity:.2f}."
        details += "\nMy emotional components are:"
        for emotion, value in state['basic_emotions'].items():
            if value > 0.1:  # Only mention significant emotions
                details += f"\n- {emotion}: {value:.2f}"
                
        return base_response + details 