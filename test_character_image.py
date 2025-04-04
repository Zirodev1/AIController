"""
Test script for the character image generation functionality.
This allows testing the character image generation without running the full application.
"""
import os
import logging
import argparse
from PIL import Image
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function for the character image generation test."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Test character image generation")
    parser.add_argument("--preset", default="default", help="Character preset (e.g., happy, sad, selfie)")
    parser.add_argument("--env", help="Environment preset (e.g., garden, beach, bedroom)")
    parser.add_argument("--activity", help="Activity preset (e.g., reading, cooking)")
    parser.add_argument("--prompt", help="Custom prompt to add")
    parser.add_argument("--size", default="1024x1360", help="Image size (width x height)")
    args = parser.parse_args()
    
    # Parse size
    try:
        width, height = map(int, args.size.split("x"))
        size = (width, height)
    except ValueError:
        logger.error(f"Invalid size format: {args.size}. Using default 1024x1360.")
        size = (1024, 1360)
    
    # Import the ImageGenerator (after loading .env)
    from ai_core.image.image_generator import ImageGenerator
    
    # Create image generator
    image_generator = ImageGenerator()
    
    # Print available presets if requested
    if args.preset == "list":
        logger.info("Available character presets:")
        for preset in image_generator.character_presets:
            logger.info(f"  - {preset}: {image_generator.character_presets[preset]}")
            
        logger.info("\nAvailable environment presets:")
        for env in image_generator.environment_presets:
            logger.info(f"  - {env}: {image_generator.environment_presets[env]}")
            
        logger.info("\nAvailable activity presets:")
        for act in image_generator.activity_presets:
            logger.info(f"  - {act}: {image_generator.activity_presets[act]}")
        return
    
    # Display configuration
    logger.info("Character Image Generation Test")
    logger.info(f"Preset: {args.preset}")
    logger.info(f"Environment: {args.env if args.env else 'None'}")
    logger.info(f"Activity: {args.activity if args.activity else 'None'}")
    logger.info(f"Custom prompt: {args.prompt if args.prompt else 'None'}")
    logger.info(f"Size: {size[0]}x{size[1]}")
    logger.info(f"Using device: {image_generator.device}")
    
    # Try to find model
    if image_generator.model_path:
        logger.info(f"Found model at: {image_generator.model_path}")
    else:
        logger.warning("No model found, will use placeholder images")
    
    # Generate the image
    logger.info("Generating character image...")
    image = image_generator.generate_image(
        prompt=args.prompt,
        preset=args.preset,
        environment=args.env,
        activity=args.activity,
        size=size
    )
    
    if image:
        # Save the image
        filename_parts = [args.preset]
        if args.env:
            filename_parts.append(args.env)
        if args.activity:
            filename_parts.append(args.activity)
        filename_prefix = f"test_{'_'.join(filename_parts)}"
        
        saved_path = image_generator.save_image(image, filename_prefix)
        if saved_path:
            logger.info(f"Image saved to: {saved_path}")
            
            # Show image if running in interactive environment
            try:
                image.show()
                logger.info("Image displayed")
            except Exception as e:
                logger.warning(f"Could not display image: {e}")
    else:
        logger.error("Image generation failed")

if __name__ == "__main__":
    main() 