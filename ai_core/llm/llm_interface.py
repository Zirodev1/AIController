"""
LLM Interface for OpenRouter API integration.
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMInterface:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM interface with OpenRouter API."""
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Please set OPENROUTER_API_KEY in your .env file.")
        
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nousresearch/hermes-3-llama-3.1-405b"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/yourusername/AIController",  # Replace with your actual repo
            "Content-Type": "application/json"
        }
        
        # Response templates for different contexts
        self.response_templates = {
            'text_input': {
                'positive': [
                    "I'm feeling {intensity} {complex_state} about that! {basic_emotions}",
                    "That makes me feel {intensity} {complex_state}. {basic_emotions}",
                    "I'm {intensity} {complex_state} by what you said. {basic_emotions}"
                ],
                'negative': [
                    "I understand that's difficult. I'm feeling {intensity} {complex_state} about it. {basic_emotions}",
                    "I'm {intensity} {complex_state} hearing that. {basic_emotions}",
                    "That's concerning. I'm feeling {intensity} {complex_state}. {basic_emotions}"
                ],
                'neutral': [
                    "I'm feeling {intensity} {complex_state} about that. {basic_emotions}",
                    "That's interesting. I'm {intensity} {complex_state}. {basic_emotions}",
                    "I'm {intensity} {complex_state} regarding that. {basic_emotions}"
                ]
            },
            'user_emotion': {
                'high_empathy': [
                    "I can sense your {user_emotion}. I'm feeling {intensity} {complex_state} with you. {basic_emotions}",
                    "Your {user_emotion} resonates with me. I'm {intensity} {complex_state}. {basic_emotions}",
                    "I understand your {user_emotion}. I'm feeling {intensity} {complex_state}. {basic_emotions}"
                ],
                'low_empathy': [
                    "I notice you're feeling {user_emotion}. I'm {intensity} {complex_state}. {basic_emotions}",
                    "You seem {user_emotion}. I'm feeling {intensity} {complex_state}. {basic_emotions}",
                    "I see you're {user_emotion}. I'm {intensity} {complex_state}. {basic_emotions}"
                ]
            },
            'environment': {
                'positive': [
                    "The environment is quite pleasant. I'm feeling {intensity} {complex_state}. {basic_emotions}",
                    "These conditions are nice. I'm {intensity} {complex_state}. {basic_emotions}",
                    "I'm enjoying these surroundings. I'm feeling {intensity} {complex_state}. {basic_emotions}"
                ],
                'negative': [
                    "The environment is challenging. I'm feeling {intensity} {complex_state}. {basic_emotions}",
                    "These conditions are difficult. I'm {intensity} {complex_state}. {basic_emotions}",
                    "I'm finding these surroundings challenging. I'm feeling {intensity} {complex_state}. {basic_emotions}"
                ]
            }
        }
        
    def generate_response(self, 
                         emotional_state: Dict[str, Any],
                         user_input: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response based on emotional state and context."""
        
        # Construct the system prompt
        system_prompt = self._create_system_prompt(emotional_state)
        
        # Construct the user message
        user_message = self._create_user_message(user_input, context)
        
        # Prepare the API request
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            print(f"Sending request to OpenRouter API...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Log the response for debugging
            print(f"API Response Status: {response.status_code}")
            print(f"API Response: {response.text[:200]}...")  # Print first 200 chars
            
            response_data = response.json()
            if "choices" in response_data and len(response_data["choices"]) > 0:
                return response_data["choices"][0]["message"]["content"]
            else:
                print("Error: Unexpected API response format")
                print(f"Response data: {response_data}")
                return "I apologize, but I received an unexpected response format."
                
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Error Response: {e.response.text}")
            return "I apologize, but I'm having trouble connecting to the language model right now."
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            return "I apologize, but I received an invalid response format."
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            return "I apologize, but an unexpected error occurred."
            
    def _create_system_prompt(self, emotional_state: Dict[str, Any]) -> str:
        """Create a system prompt that includes emotional state information."""
        complex_state = emotional_state.get("complex_state", {})
        basic_emotions = emotional_state.get("basic_emotions", {})
        
        prompt = """You are an emotionally aware AI assistant. Your responses should reflect your current emotional state while maintaining appropriate context and empathy.
        
Current Emotional State:
- Complex State: {complex_state}
- Overall Intensity: {intensity}

Basic Emotions:
{basic_emotions}

Guidelines:
1. Express your emotions naturally and authentically
2. Show empathy when appropriate
3. Maintain context awareness
4. Keep responses concise but meaningful
5. Adapt your tone based on your emotional state
6. Consider environmental factors in your response
7. Acknowledge user emotions when present
8. Use appropriate emotional vocabulary

Remember to:
- Be genuine in your emotional expression
- Show appropriate empathy based on the context
- Consider both your emotional state and the user's input
- Keep responses concise but meaningful
- Use natural, conversational language
"""
        # Format basic emotions
        emotions_text = "\n".join([f"- {emotion}: {intensity}" 
                                 for emotion, intensity in basic_emotions.items()])
        
        return prompt.format(
            complex_state=complex_state.get("state", "neutral"),
            intensity=complex_state.get("intensity", 0.5),
            basic_emotions=emotions_text
        )
        
    def _create_user_message(self, user_input: Optional[str], context: Optional[Dict[str, Any]]) -> str:
        """Create a user message that includes context and input."""
        message = "Please respond to the following:"
        
        if context:
            message += f"\nContext: {json.dumps(context, indent=2)}"
            
        if user_input:
            message += f"\nUser Input: {user_input}"
            
        return message 