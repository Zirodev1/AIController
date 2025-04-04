#!/usr/bin/env python
"""
Character Image Preset Gallery

This script generates a gallery of all available character preset images
to showcase the different options available in the AI Companion.
"""
import os
import sys
import logging
import argparse
import time
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PresetGallery:
    """Creates a gallery of character image presets"""
    
    def __init__(self):
        """Initialize the preset gallery"""
        from ai_core.image.image_generator import ImageGenerator
        self.image_generator = ImageGenerator()
        self.output_dir = os.path.join("generated_images", "gallery")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get all preset categories
        self.character_presets = list(self.image_generator.character_presets.keys())
        self.environment_presets = list(self.image_generator.environment_presets.keys())
        self.activity_presets = list(self.image_generator.activity_presets.keys())
        
        # Set image size for gallery
        self.preset_image_size = (512, 768)
        
        # Get a font for labels
        self._initialize_font()
        
    def _initialize_font(self):
        """Initialize a font for labels."""
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
            self.small_font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
            try:
                self.font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 24)
                self.small_font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 16) 
            except IOError:
                # Fallback to default font
                logger.warning("Arial font not found. Using default font.")
                self.font = ImageFont.load_default()
                self.small_font = ImageFont.load_default()
    
    def generate_character_gallery(self):
        """Generate images for all character presets."""
        logger.info("Generating character preset gallery...")
        
        for preset in self.character_presets:
            logger.info(f"Generating image for '{preset}' preset...")
            image = self.image_generator.generate_image(
                preset=preset,
                size=self.preset_image_size
            )
            
            if image:
                # Add a label with the preset name
                image = self._add_label(image, preset)
                
                # Save the image
                image_path = os.path.join(self.output_dir, f"character_{preset}.png")
                image.save(image_path, "PNG")
                logger.info(f"Saved {image_path}")
                
    def generate_environment_gallery(self):
        """Generate images for all environment presets."""
        logger.info("Generating environment preset gallery...")
        
        # Use a consistent character preset
        character_preset = "default"
        
        for env in self.environment_presets:
            logger.info(f"Generating image for '{env}' environment...")
            image = self.image_generator.generate_image(
                preset=character_preset,
                environment=env,
                size=self.preset_image_size
            )
            
            if image:
                # Add a label with the environment name
                image = self._add_label(image, f"Environment: {env}")
                
                # Save the image
                image_path = os.path.join(self.output_dir, f"env_{env}.png")
                image.save(image_path, "PNG")
                logger.info(f"Saved {image_path}")
                
    def generate_activity_gallery(self):
        """Generate images for all activity presets."""
        logger.info("Generating activity preset gallery...")
        
        # Use a consistent character preset
        character_preset = "default"
        
        for activity in self.activity_presets:
            logger.info(f"Generating image for '{activity}' activity...")
            image = self.image_generator.generate_image(
                preset=character_preset,
                activity=activity,
                size=self.preset_image_size
            )
            
            if image:
                # Add a label with the activity name
                image = self._add_label(image, f"Activity: {activity}")
                
                # Save the image
                image_path = os.path.join(self.output_dir, f"activity_{activity}.png")
                image.save(image_path, "PNG")
                logger.info(f"Saved {image_path}")
    
    def generate_combined_presets(self):
        """Generate a few images with combinations of presets."""
        logger.info("Generating combined preset examples...")
        
        # Define some interesting combinations
        combinations = [
            {"preset": "happy", "environment": "garden", "name": "happy_garden"},
            {"preset": "sad", "environment": "bedroom", "name": "sad_bedroom"},
            {"preset": "elegant", "environment": "city", "name": "elegant_city"},
            {"preset": "casual", "activity": "reading", "name": "casual_reading"},
            {"preset": "happy", "activity": "cooking", "name": "happy_cooking"},
            {"preset": "selfie", "environment": "beach", "name": "selfie_beach"},
            {"preset": "surprised", "activity": "shopping", "name": "surprised_shopping"},
            {"preset": "happy", "environment": "garden", "activity": "reading", "name": "happy_garden_reading"},
        ]
        
        for combo in combinations:
            name = combo.pop("name")
            logger.info(f"Generating image for combination: {name}...")
            
            image = self.image_generator.generate_image(
                size=self.preset_image_size,
                **combo
            )
            
            if image:
                # Add a label with the combination name
                label = " + ".join(f"{k}: {v}" for k, v in combo.items())
                image = self._add_label(image, label)
                
                # Save the image
                image_path = os.path.join(self.output_dir, f"combo_{name}.png")
                image.save(image_path, "PNG")
                logger.info(f"Saved {image_path}")
    
    def create_montage(self, category="character"):
        """Create a montage of all images in a category."""
        logger.info(f"Creating montage for '{category}' category...")
        
        # Get list of images in the category
        if category == "character":
            prefix = "character_"
            title = "Character Presets"
        elif category == "environment":
            prefix = "env_"
            title = "Environment Presets"
        elif category == "activity":
            prefix = "activity_"
            title = "Activity Presets"
        elif category == "combo":
            prefix = "combo_"
            title = "Combined Presets"
        else:
            logger.error(f"Unknown category: {category}")
            return
            
        # Find all images in the category
        image_files = [f for f in os.listdir(self.output_dir) if f.startswith(prefix) and f.endswith('.png')]
        
        if not image_files:
            logger.warning(f"No images found for category: {category}")
            return
            
        # Calculate grid dimensions
        n_images = len(image_files)
        cols = min(4, n_images)
        rows = (n_images + cols - 1) // cols  # Ceiling division
        
        # Get the dimensions of the first image as a reference
        first_image = Image.open(os.path.join(self.output_dir, image_files[0]))
        img_width, img_height = first_image.size
        
        # Create a canvas for the montage
        margin = 20
        title_height = 60
        montage_width = cols * img_width + (cols + 1) * margin
        montage_height = title_height + rows * img_height + (rows + 1) * margin
        
        montage = Image.new('RGB', (montage_width, montage_height), (240, 240, 240))
        draw = ImageDraw.Draw(montage)
        
        # Draw the title
        draw.rectangle([(0, 0), (montage_width, title_height)], fill=(200, 200, 200))
        text_width = draw.textlength(title, font=self.font)
        draw.text(
            ((montage_width - text_width) // 2, (title_height - 24) // 2),
            title,
            font=self.font,
            fill=(0, 0, 0)
        )
        
        # Place each image in the grid
        for i, img_file in enumerate(image_files):
            row = i // cols
            col = i % cols
            
            img = Image.open(os.path.join(self.output_dir, img_file))
            
            # Calculate position
            x = margin + col * (img_width + margin)
            y = title_height + margin + row * (img_height + margin)
            
            # Paste the image
            montage.paste(img, (x, y))
        
        # Save the montage
        montage_path = os.path.join(self.output_dir, f"{category}_montage.png")
        montage.save(montage_path, "PNG")
        logger.info(f"Montage saved to: {montage_path}")
        
        return montage_path
    
    def _add_label(self, image, label_text):
        """Add a label to the bottom of an image."""
        # Create a new image with extra space for the label
        label_height = 40
        width, height = image.size
        new_img = Image.new('RGB', (width, height + label_height), (0, 0, 0))
        
        # Paste the original image
        new_img.paste(image, (0, 0))
        
        # Add the label
        draw = ImageDraw.Draw(new_img)
        draw.rectangle([(0, height), (width, height + label_height)], fill=(30, 30, 30))
        
        # Calculate text position
        text_width = draw.textlength(label_text, font=self.small_font)
        text_x = (width - text_width) // 2
        text_y = height + (label_height - 16) // 2
        
        # Draw text
        draw.text((text_x, text_y), label_text, font=self.small_font, fill=(255, 255, 255))
        
        return new_img
    
    def generate_full_gallery(self):
        """Generate all preset galleries and montages."""
        
        print("Generating preset galleries. This may take some time...")
        
        # Generate individual preset images
        self.generate_character_gallery()
        self.generate_environment_gallery()
        self.generate_activity_gallery()
        self.generate_combined_presets()
        
        # Create montages
        char_montage = self.create_montage("character")
        env_montage = self.create_montage("environment")
        act_montage = self.create_montage("activity")
        combo_montage = self.create_montage("combo")
        
        print("\nGallery generation complete!")
        print(f"Images saved to: {self.output_dir}")
        
        # Return the montage paths
        return [char_montage, env_montage, act_montage, combo_montage]

def main():
    """Main function for the gallery generator."""
    parser = argparse.ArgumentParser(description="Generate a gallery of character image presets")
    parser.add_argument("--show", action="store_true", help="Show montages after generation")
    args = parser.parse_args()
    
    gallery = PresetGallery()
    montages = gallery.generate_full_gallery()
    
    # Show montages if requested
    if args.show and montages:
        for montage_path in montages:
            if montage_path:
                image = Image.open(montage_path)
                image.show()

if __name__ == "__main__":
    main()