#!/usr/bin/env python
"""
Character Image Generation Demo

This script demonstrates the AI companion's character image generation capabilities
using integrated Stable Diffusion.
"""
import os
import time
import logging
import argparse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_user_request(request_text):
    """Simulate a user request and print it"""
    print(f"\n\033[94mUser: {request_text}\033[0m")
    time.sleep(1)

def simulate_ai_response(response_text):
    """Simulate an AI response and print it"""
    print(f"\033[92mAI: {response_text}\033[0m")
    time.sleep(1)

def main():
    """Main function for the character image generation demo."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Demo character image generation with AI companion")
    parser.add_argument("--show", action="store_true", help="Show generated images")
    args = parser.parse_args()
    
    # Import ImageGenerator (after loading .env)
    from ai_core.image.image_generator import ImageGenerator
    
    # Create image generator
    image_generator = ImageGenerator()
    
    print("\n\033[1m=== Character Image Generation Demo ===\033[0m")
    print("\nThis demo shows how the AI companion can generate character images.")
    print("It uses direct integration with Stable Diffusion models.")
    
    if image_generator.model_path:
        print(f"\nUsing model: {os.path.basename(image_generator.model_path)}")
    else:
        print("\nNo model found - using placeholder images")
    
    print("\n\033[1m--- Demo Starting ---\033[0m")
    time.sleep(1)
    
    # Simulate a conversation with image requests
    
    # Basic selfie request
    simulate_user_request("Can you send me a selfie?")
    
    # Parse the request
    params = image_generator.parse_image_request("Can you send me a selfie?")
    simulate_ai_response("Sure, I'll take a selfie for you!")
    
    # Generate the image
    print("\nGenerating selfie image...")
    image = image_generator.generate_image(**params)
    
    if image:
        # Save the image
        saved_path = image_generator.save_image(image, "demo_selfie")
        print(f"Image saved to: {saved_path}")
        
        # Show image if requested
        if args.show:
            try:
                image.show()
            except Exception as e:
                logger.warning(f"Could not display image: {e}")
    
    time.sleep(2)
    
    # Happy in garden request
    simulate_user_request("Can I see you happy in a garden?")
    
    # Parse the request
    params = image_generator.parse_image_request("Can I see you happy in a garden?")
    simulate_ai_response("Of course! Here's a picture of me enjoying a beautiful garden!")
    
    # Generate the image
    print("\nGenerating happy garden image...")
    image = image_generator.generate_image(preset="happy", environment="garden")
    
    if image:
        # Save the image
        saved_path = image_generator.save_image(image, "demo_happy_garden")
        print(f"Image saved to: {saved_path}")
        
        # Show image if requested
        if args.show:
            try:
                image.show()
            except Exception as e:
                logger.warning(f"Could not display image: {e}")
    
    time.sleep(2)
    
    # Activity request
    simulate_user_request("Show me a picture of you reading a book")
    
    # Parse the request
    params = image_generator.parse_image_request("Show me a picture of you reading a book")
    simulate_ai_response("I love reading! Here's a picture of me with a book.")
    
    # Generate the image
    print("\nGenerating reading image...")
    image = image_generator.generate_image(activity="reading", environment="library")
    
    if image:
        # Save the image
        saved_path = image_generator.save_image(image, "demo_reading")
        print(f"Image saved to: {saved_path}")
        
        # Show image if requested
        if args.show:
            try:
                image.show()
            except Exception as e:
                logger.warning(f"Could not display image: {e}")
    
    time.sleep(2)
    
    # Custom prompt request
    simulate_user_request("Can you send me a picture of yourself in an elegant dress at a party?")
    simulate_ai_response("Here's me in an elegant dress at a party! I hope you like it.")
    
    # Generate the image
    print("\nGenerating custom prompt image...")
    image = image_generator.generate_image(preset="elegant", prompt="at a party, celebration, ballroom")
    
    if image:
        # Save the image
        saved_path = image_generator.save_image(image, "demo_elegant_party")
        print(f"Image saved to: {saved_path}")
        
        # Show image if requested
        if args.show:
            try:
                image.show()
            except Exception as e:
                logger.warning(f"Could not display image: {e}")
    
    # Show available presets
    print("\n\033[1m--- Available Presets ---\033[0m")
    print("\n\033[4mCharacter Presets:\033[0m")
    for preset in image_generator.character_presets:
        print(f"  - {preset}")
    
    print("\n\033[4mEnvironment Presets:\033[0m")
    for env in image_generator.environment_presets:
        print(f"  - {env}")
    
    print("\n\033[4mActivity Presets:\033[0m")
    for act in image_generator.activity_presets:
        print(f"  - {act}")
    
    print("\n\033[1m--- Demo Complete ---\033[0m")
    print("\nThe generated images can be found in the 'generated_images' directory.")
    print("You can run 'test_character_image.py' for more image generation options.")

if __name__ == "__main__":
    main() 