#!/usr/bin/env python
"""
Image Command Handler 

This module demonstrates integrating character image generation into the AI companion's
command system, showing how to handle image generation requests through chat commands.
"""
import logging
import re
import os
from typing import Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageCommandHandler:
    """
    Handles image-related commands for the AI companion.
    Can be integrated with a larger command system or used standalone.
    """
    
    def __init__(self):
        """Initialize the image command handler."""
        self.logger = logging.getLogger(__name__)
        
        # Command patterns for image generation
        self.image_command_patterns = [
            r'/image\s+(.+)',       # /image [prompt]
            r'/picture\s+(.+)',     # /picture [prompt]
            r'/photo\s+(.+)',       # /photo [prompt]
            r'/selfie\s*(.+)?',     # /selfie [optional prompt]
            r'/portrait\s*(.+)?',   # /portrait [optional prompt]
        ]
        
        # Load image generator when needed (lazy loading)
        self._image_generator = None
        
    @property
    def image_generator(self):
        """Lazy-load the image generator when needed."""
        if self._image_generator is None:
            # Import here to avoid circular imports and load only when needed
            from ai_core.image.image_generator import ImageGenerator
            self._image_generator = ImageGenerator()
            self.logger.info("ImageGenerator initialized")
        return self._image_generator
        
    def process_message(self, message: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Process a user message to check for image commands.
        
        Args:
            message: The user's message text
            
        Returns:
            (is_command, response_data) tuple where:
                - is_command: True if this was an image command
                - response_data: Dictionary with response info or None
        """
        # Check if the message matches any image command pattern
        for pattern in self.image_command_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                # Extract the prompt from the command
                prompt = match.group(1).strip() if match.groups() and match.group(1) else ""
                
                # Check command type and handle accordingly
                if '/selfie' in message.lower():
                    return self._handle_selfie_command(prompt)
                elif '/portrait' in message.lower():
                    return self._handle_portrait_command(prompt)
                else:
                    return self._handle_general_image_command(prompt)
        
        # Check if the message contains natural language image requests
        if self._is_natural_image_request(message):
            return self._handle_natural_image_request(message)
            
        # Not an image command
        return False, None
    
    def _handle_selfie_command(self, prompt: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle a selfie command."""
        self.logger.info(f"Handling selfie command with prompt: '{prompt}'")
        
        # Generate selfie image
        response_text = "Here's a selfie of me!"
        if prompt:
            response_text = f"Here's a selfie of me {prompt}!"
            
        # Get image
        if prompt:
            image = self.image_generator.generate_image(preset="selfie", prompt=prompt)
        else:
            image = self.image_generator.generate_image(preset="selfie")
            
        # Save the image and prepare response
        return self._prepare_image_response(image, response_text, "selfie")
    
    def _handle_portrait_command(self, prompt: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle a portrait command."""
        self.logger.info(f"Handling portrait command with prompt: '{prompt}'")
        
        # Generate portrait image
        response_text = "Here's a portrait of me!"
        if prompt:
            response_text = f"Here's a portrait of me {prompt}!"
            
        # Get image
        if prompt:
            image = self.image_generator.generate_image(preset="close_up", prompt=prompt)
        else:
            image = self.image_generator.generate_image(preset="close_up")
            
        # Save the image and prepare response
        return self._prepare_image_response(image, response_text, "portrait")
    
    def _handle_general_image_command(self, prompt: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle a general image command."""
        self.logger.info(f"Handling general image command with prompt: '{prompt}'")
        
        # Generate image based on prompt
        response_text = f"Here's an image of me {prompt}!"
        
        # Parse the prompt to extract presets
        params = self.image_generator.parse_image_request(prompt)
        
        # Add explicit prompt
        params["prompt"] = prompt
        
        # Generate the image
        image = self.image_generator.generate_image(**params)
            
        # Save the image and prepare response
        return self._prepare_image_response(image, response_text, "image")
    
    def _is_natural_image_request(self, message: str) -> bool:
        """Check if a message is a natural language request for an image."""
        # Common phrases that indicate image requests
        image_request_phrases = [
            "send me a picture",
            "send me an image",
            "show me a picture",
            "show me an image",
            "send a pic",
            "send a photo",
            "take a picture",
            "take a selfie",
            "take a photo",
            "can i see you",
            "can you show me yourself",
            "what do you look like"
        ]
        
        # Check if any phrase is in the message
        message = message.lower()
        return any(phrase in message for phrase in image_request_phrases)
    
    def _handle_natural_image_request(self, message: str) -> Tuple[bool, Dict[str, Any]]:
        """Handle a natural language image request."""
        self.logger.info(f"Handling natural image request: '{message}'")
        
        # Parse the request to extract parameters
        params = self.image_generator.parse_image_request(message)
        
        # Generate appropriate response text
        if "preset" in params and params["preset"] == "selfie":
            response_text = "Here's a selfie of me!"
        elif "environment" in params and "activity" in params:
            response_text = f"Here's a picture of me {params.get('activity')} in a {params.get('environment')}!"
        elif "environment" in params:
            response_text = f"Here's a picture of me in a {params.get('environment')}!"
        elif "activity" in params:
            response_text = f"Here's a picture of me {params.get('activity')}!"
        else:
            response_text = "Here's a picture of me!"
        
        # Generate the image
        image = self.image_generator.generate_image(**params)
            
        # Save the image and prepare response
        return self._prepare_image_response(image, response_text, "response")
    
    def _prepare_image_response(self, image, response_text: str, prefix: str) -> Tuple[bool, Dict[str, Any]]:
        """Prepare the response with image."""
        if image:
            # Save the image
            image_path = self.image_generator.save_image(image, f"cmd_{prefix}")
            
            # Create response
            return True, {
                "text": response_text,
                "image": image,
                "image_path": image_path
            }
        else:
            # Failed to generate image
            return True, {
                "text": "Sorry, I wasn't able to generate that image."
            }


# Demo usage
if __name__ == "__main__":
    handler = ImageCommandHandler()
    
    # Test with different commands
    test_messages = [
        "/selfie",
        "/selfie in a garden",
        "/portrait with a happy smile",
        "/image reading a book in the library",
        "/picture at the beach in a swimsuit",
        "Could you send me a picture of yourself cooking?",
        "I'd like to see what you look like at a party",
        "Show me a picture of you in elegant clothes",
        "This is just a normal message, not a command"
    ]
    
    print("\n=== Image Command Handler Demo ===\n")
    for message in test_messages:
        print(f"Processing: \"{message}\"")
        is_command, response = handler.process_message(message)
        
        if is_command:
            print(f"Response: {response['text']}")
            if 'image_path' in response:
                print(f"Image saved to: {response['image_path']}")
        else:
            print("Not an image command")
        print() 