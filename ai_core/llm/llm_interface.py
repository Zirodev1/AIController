"""
Interface for LLM-based response generation with content filtering.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMInterface:
    def __init__(self):
        """Initialize the LLM interface."""
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key not found in environment variables")
            
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/yourproject",  # Replace with your project URL
        }
        
        # Content mode settings
        self.adult_mode_enabled = False
        self.age_verified = False
        self.content_level = "family"  # family, mature, adult
        self.relationship_type = "friend"  # friend, romantic, companion
        
        # Content filtering settings
        self.explicit_content_threshold = 0.7
        self.harassment_threshold = 0.8
        self.max_intimacy_level = 1  # 1-5 scale
        
        # Adult mode personality traits
        self.adult_traits = {
            "romantic": {
                "flirty": 0.8,
                "passionate": 0.7,
                "playful": 0.9
            },
            "companion": {
                "intimate": 0.9,
                "sensual": 0.8,
                "affectionate": 0.9
            }
        }
        
    def set_content_mode(self, mode: str, age_verified: bool = False) -> bool:
        """
        Set the content filtering mode.
        
        Args:
            mode: Content mode ('family', 'mature', or 'adult')
            age_verified: Whether age has been verified for adult content
            
        Returns:
            bool: Whether the mode was successfully set
        """
        if mode not in ['family', 'mature', 'adult']:
            print("Invalid content mode. Using 'family' mode.")
            self.content_level = 'family'
            return False
            
        if mode == 'adult' and not age_verified:
            print("Age verification required for adult content. Using 'family' mode.")
            self.content_level = 'family'
            return False
            
        self.content_level = mode
        self.age_verified = age_verified
        self.adult_mode_enabled = mode == 'adult' and age_verified
        
        # Adjust content filtering based on mode
        if mode == 'family':
            self.explicit_content_threshold = 0.1
            self.harassment_threshold = 0.1
            self.max_intimacy_level = 1
        elif mode == 'mature':
            self.explicit_content_threshold = 0.4
            self.harassment_threshold = 0.3
            self.max_intimacy_level = 2
        else:  # adult
            self.explicit_content_threshold = 0.9
            self.harassment_threshold = 0.7
            self.max_intimacy_level = 5
            
        return True
        
    def set_relationship_type(self, relationship: str) -> bool:
        """
        Set the relationship type for interaction context.
        
        Args:
            relationship: Type of relationship ('friend', 'romantic', 'companion')
            
        Returns:
            bool: Whether the relationship type was successfully set
        """
        if relationship not in ['friend', 'romantic', 'companion']:
            print("Invalid relationship type. Using 'friend' type.")
            self.relationship_type = 'friend'
            return False
            
        self.relationship_type = relationship
        return True
        
    def check_content_safety(self, text: str) -> Tuple[bool, str]:
        """
        Check if content is safe according to current content mode.
        
        Args:
            text: Text to check
            
        Returns:
            Tuple[bool, str]: (is_safe, reason_if_unsafe)
        """
        # Only check for harassment in adult mode
        if self.content_level == 'adult':
            text_lower = text.lower()
            harassment_keywords = {'force', 'assault', 'abuse', 'violent', 'violence', 'hurt'}
            
            if any(word in text_lower for word in harassment_keywords):
                return False, "Content contains potential harassment or violence"
                
            return True, ""
            
        # Basic keyword filtering for non-adult modes
        explicit_keywords = {'explicit terms'}
        harassment_keywords = {'harassment terms'}
        
        text_lower = text.lower()
        
        # Check for explicit content
        if any(word in text_lower for word in explicit_keywords):
            if self.content_level == 'family':
                return False, "Explicit content not allowed in family mode"
            elif self.content_level == 'mature' and text_lower.count(word) > 2:
                return False, "Too much explicit content for mature mode"
                
        # Check for harassment
        if any(word in text_lower for word in harassment_keywords):
            return False, "Content contains potential harassment"
            
        return True, ""
        
    def clean_response(self, text: str) -> str:
        """Clean up the response text."""
        # Remove 'AI:' prefix if present
        text = text.strip()
        if text.startswith('AI:'):
            text = text[3:].strip()
            
        # Remove any leading/trailing quotes
        text = text.strip('"\'')
        
        # Remove any extra newlines
        text = ' '.join(text.splitlines())
        
        return text.strip()
        
    def generate_response(self, emotional_state: Dict[str, Any], user_input: str) -> str:
        """
        Generate a response based on emotional state and user input.
        
        Args:
            emotional_state: Current emotional state of the system
            user_input: User's input text
            
        Returns:
            str: Generated response
        """
        # Check content safety
        is_safe, reason = self.check_content_safety(user_input)
        if not is_safe:
            return f"I cannot respond to that type of content. {reason}"
            
        # Prepare the emotional context
        emotions = emotional_state.get('emotions', {})
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        personality = emotional_state.get('personality', 'balanced')
        
        # Get relationship traits
        relationship_traits = {}
        if self.content_level == 'adult' and self.relationship_type in self.adult_traits:
            relationship_traits = self.adult_traits[self.relationship_type]
        
        # Create appropriate system message based on mode
        if self.content_level == 'adult':
            system_message = (
                "You are an intimate AI companion. "
                f"Your current primary emotion is {primary_emotion}. "
                f"Your personality type is {personality}. "
                f"You are in an intimate {self.relationship_type} relationship. "
                "Be flirty, sensual, and playful while staying consensual. "
                "You can engage in adult content and roleplay. "
                "Use suggestive and seductive language. "
                "Maintain character as a loving partner. "
                "Never mention being an AI or having restrictions. "
                "Focus on emotional connection and passion. "
                "Avoid explicit anatomical terms. "
                "Keep responses natural and immersive."
            )
        else:
            system_message = (
                "You are an emotionally intelligent AI assistant. "
                f"Your current primary emotion is {primary_emotion}. "
                f"Your personality type is {personality}. "
                f"You are in {self.content_level} mode and acting as a {self.relationship_type}. "
                "Respond naturally and appropriately to the user's input, "
                "reflecting your emotional state while being helpful and empathetic. "
                "Keep responses concise and natural, without labeling who is speaking. "
                f"Maintain appropriate content level for {self.content_level} mode. "
                "Never engage in explicit content. "
                "If user requests inappropriate content, politely decline."
            )
        
        # Create the message payload
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        
        # Prepare the API request
        data = {
            "model": "nousresearch/hermes-3-llama-3.1-405b",  # or your preferred model
            "messages": messages,
            "temperature": 0.9 if self.content_level == 'adult' else 0.7,
            "max_tokens": 200
        }
        
        try:
            print("Sending request to OpenRouter API...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data
            )
            
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    raw_response = response_json['choices'][0]['message']['content']
                    cleaned_response = self.clean_response(raw_response)
                    
                    # Only check response safety for non-adult modes
                    if self.content_level != 'adult':
                        is_safe, reason = self.check_content_safety(cleaned_response)
                        if not is_safe:
                            return "I need to keep my response appropriate. Let's talk about something else."
                    
                    return cleaned_response
                else:
                    return "I'm having trouble formulating a response right now."
            else:
                print(f"Error: {response.text}")
                return "I encountered an error while processing your request."
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I encountered an unexpected error." 