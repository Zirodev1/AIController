"""
Interface for LLM-based response generation.
"""
import os
import json
import requests
from typing import Dict, Any, Optional
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
        # Prepare the emotional context
        emotions = emotional_state.get('emotions', {})
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        personality = emotional_state.get('personality', 'balanced')
        
        # Create the system message with emotional guidance
        system_message = (
            "You are an emotionally intelligent AI assistant. "
            f"Your current primary emotion is {primary_emotion}. "
            f"Your personality type is {personality}. "
            "Respond naturally and appropriately to the user's input, "
            "reflecting your emotional state while being helpful and empathetic. "
            "Keep responses concise and natural, without labeling who is speaking."
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
            "temperature": 0.7,
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
                    return self.clean_response(raw_response)
                else:
                    return "I apologize, but I'm having trouble formulating a response right now."
            else:
                print(f"Error: {response.text}")
                return "I apologize, but I encountered an error while processing your request."
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an unexpected error." 