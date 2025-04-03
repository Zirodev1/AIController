"""
Placeholder for the Image Generation system.
"""
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random
import time # Added missing import

class ImageGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("ImageGenerator initialized.")
        # Attempt to load a default font
        try:
            # Try a common font path
            self.font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            try:
                # Try another common font path (adjust if needed for your system)
                # For Windows, common fonts might be in C:\\Windows\\Fonts
                # Example: self.font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 15)
                # For Linux: self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
                 self.font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 15) # Added Windows specific path
            except IOError:
                 # Fallback to default font if specific fonts are not found
                self.logger.warning("Arial font not found. Using Pillow's default font.")
                self.font = ImageFont.load_default()

    def generate_image(self, prompt: str) -> Image.Image:
        """
        Generates a placeholder image based on the prompt.
        Replace this with actual Stable Diffusion or other model integration.
        """
        self.logger.info(f"Generating placeholder image for prompt: {prompt}")

        # Create a simple placeholder image
        img_width = 512
        img_height = 512

        # Random background color
        bg_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        image = Image.new('RGB', (img_width, img_height), color=bg_color)
        draw = ImageDraw.Draw(image)

        # Wrap text
        lines = []
        max_width = img_width - 40  # Padding
        words = prompt.split()
        current_line = ""
        for word in words:
            # Test width with the new word
            test_line = f"{current_line} {word}".strip()

            # Calculate text bounding box accurately with Draw.textbbox
            bbox = draw.textbbox((0, 0), test_line, font=self.font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line) # Add the last line

        # Draw the text line by line
        text_color = (255, 255, 255)
        y_text = 50
        # Use textlength to get height, fallback if needed
        try:
             # Use textbbox for more accurate height calculation if possible
            line_height = draw.textbbox((0, 0), "Tg", font=self.font)[3] + 5 # Add padding
        except AttributeError:
             # Fallback for older Pillow versions or default font
            line_height = 15 + 5

        # Center the text block vertically
        total_text_height = len(lines) * line_height
        start_y = (img_height - total_text_height) // 2
        if start_y < 20: # Ensure text doesn't start too close to the top
             start_y = 20

        for i, line in enumerate(lines):
             # Calculate text width for centering
            bbox = draw.textbbox((0, 0), line, font=self.font)
            line_width = bbox[2] - bbox[0]
            x_text = (img_width - line_width) // 2

            draw.text((x_text, start_y + i * line_height), line, font=self.font, fill=text_color)

        # Add a placeholder shape (e.g., a circle) below the text
        shape_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        # Ensure shape doesn't overlap text
        shape_y = start_y + total_text_height + 50
        if shape_y > img_height - 60: # Ensure shape fits within image bounds
             shape_y = img_height - 60
        center_x, center_y = img_width // 2, shape_y
        radius = 40
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=shape_color)


        self.logger.info("Placeholder image generated.")
        return image

    def save_image(self, image: Image.Image, filename_prefix="generated") -> str:
        """Saves the image to the output directory."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        try:
            image.save(filepath, "PNG")
            self.logger.info(f"Image saved to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to save image to {filepath}: {e}")
            return None
