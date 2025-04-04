"""
Image Generation system using Stable Diffusion.
"""
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import os
import random
import time
import torch
import glob
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple, List, Union
import numpy as np

# Load environment variables
load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load config if available
        self.config = self._load_config()
        
        # Character model settings
        self.model_path = os.getenv(
            "SD_MODEL_PATH", 
            self._find_model_path("waiNSFWIllustrious_v120.safetensors")
        )
        
        # Check if we have a model path from config
        if self.config and 'model_path' in self.config and os.path.exists(self.config['model_path']):
            self.model_path = self.config['model_path']
        
        # Default generation settings (will be overridden by config if available)
        self.width = 1024
        self.height = 1360
        self.steps = 30
        self.guidance_scale = 7.0
        self.use_hires_fix = False
        self.upscaler = "R-ESRGAN 4x+ Anime6B"
        self.upscale_factor = 1.5
        self.hires_steps = 20
        self.denoising_strength = 0.7
        
        # Apply settings from config if available
        if self.config and 'settings' in self.config:
            settings = self.config['settings']
            self.width = settings.get('width', self.width)
            self.height = settings.get('height', self.height)
            self.steps = settings.get('steps', self.steps)
            self.guidance_scale = settings.get('cfg_scale', self.guidance_scale)
            # self.use_hires_fix = settings.get('hires_fix', self.use_hires_fix) # Override config setting
            self.upscaler = settings.get('hr_upscaler', self.upscaler)
            self.upscale_factor = settings.get('hr_scale', self.upscale_factor)
            self.hires_steps = settings.get('hr_second_pass_steps', self.hires_steps)
            self.denoising_strength = settings.get('denoising_strength', self.denoising_strength)
            
            # Log that we're using configuration settings
            self.logger.info(f"Loaded settings from config: width={self.width}, height={self.height}, steps={self.steps}, cfg_scale={self.guidance_scale}")
            self.logger.info("Hires fix disabled in code.")
        
        # Default negative prompt
        self.default_negative = "bad quality, worst quality, worst detail, sketch, censor"
        
        # Load negative prompt from config if available
        if self.config and 'settings' in self.config and 'negative_prompt' in self.config['settings']:
            self.default_negative = self.config['settings']['negative_prompt']
            self.logger.info(f"Using negative prompt from config: {self.default_negative}")
            
        # Character prompt templates
        self.character_presets = {
            "default": "1girl, beautiful, looking at viewer, standing",
            "happy": "1girl, beautiful, looking at viewer, happy, smiling",
            "sad": "1girl, beautiful, looking at viewer, sad, crying",
            "surprised": "1girl, beautiful, looking at viewer, surprised, shocked",
            "casual": "1girl, beautiful, looking at viewer, casual clothes",
            "elegant": "1girl, beautiful, looking at viewer, elegant dress",
            "selfie": "1girl, beautiful, selfie, smartphone, looking at viewer",
            "outdoor": "1girl, beautiful, looking at viewer, outdoors, nature",
            "sitting": "1girl, beautiful, looking at viewer, sitting",
            "close_up": "1girl, beautiful, close-up, looking at viewer",
            "full_body": "1girl, beautiful, full body, looking at viewer, standing"
        }
        
        # Load character presets from config if available
        if self.config and 'character_presets' in self.config:
            self.character_presets.update(self.config['character_presets'])
            self.logger.info("Loaded character presets from config")
            
        # Environment prompts
        self.environment_presets = {
            "bedroom": "in bedroom, bed, cozy",
            "garden": "in garden, flowers, grass, trees",
            "beach": "at beach, ocean, sand, waves",
            "city": "in city, buildings, urban",
            "cafe": "in cafe, coffee, table, chairs",
            "library": "in library, books, bookshelves",
            "park": "in park, trees, bench, pathway"
        }
        
        # Activity prompts
        self.activity_presets = {
            "reading": "reading book",
            "cooking": "cooking, kitchen",
            "sleeping": "sleeping, eyes closed",
            "eating": "eating food",
            "walking": "walking",
            "dancing": "dancing",
            "working": "working, desk, computer",
            "shopping": "shopping, bags"
        }
        
        # Check GPU availability - improved detection
        self.device = self._get_best_device()
        
        # Initialize model later when needed (lazy loading)
        self.model = None
        self.model_initialized = False
        
        # Initialize fallback font for placeholder images
        self._initialize_font()
        
        self.logger.info(f"ImageGenerator initialized. Using device: {self.device}")
        if self.model_path:
            self.logger.info(f"Model path: {self.model_path}")
        else:
            self.logger.warning("No model path found - will use placeholder images")
    
    def _get_best_device(self) -> str:
        """Determine the best available device for tensor operations."""
        if torch.cuda.is_available():
            # Use first CUDA device
            device = f"cuda:{0}"
            # Log GPU info
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # Convert to GB
            self.logger.info(f"Using GPU: {gpu_name} with {vram:.2f}GB VRAM")
            return device
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # For MacOS with M1/M2 chips
            self.logger.info("Using Apple Metal Performance Shaders (MPS)")
            return "mps"
        else:
            # Fallback to CPU
            self.logger.warning("No GPU detected. Using CPU - image generation will be slow")
            return "cpu"
            
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from sd_config.json if available."""
        config_path = os.path.join(os.getcwd(), "sd_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded configuration from {config_path}")
                return config
            except Exception as e:
                self.logger.error(f"Error loading configuration from {config_path}: {e}")
        return None
    
    def _find_model_path(self, model_filename: str) -> Optional[str]:
        """Attempt to find the model in common locations."""
        # Common locations for Stable Diffusion models
        search_paths = [
            # Current directory
            os.path.join(os.getcwd(), model_filename),
            # Explicit path from environment
            os.getenv("SD_MODEL_PATH", ""),
            # Common SD WebUI locations
            os.path.join(os.path.expanduser("~"), "stable-diffusion-webui", "models", "Stable-diffusion", model_filename),
            os.path.join("C:", os.sep, "stable-diffusion-webui", "models", "Stable-diffusion", model_filename),
            os.path.join("C:", os.sep, "Users", os.getenv("USERNAME", ""), "Desktop", "stable-diffusion-webui", "models", "Stable-diffusion", model_filename),
            os.path.join("C:", os.sep, "Users", os.getenv("USERNAME", ""), "Desktop", "stable-diffusion-webui-1.7.0", "models", "Stable-diffusion", model_filename),
            # Models directory in the project
            os.path.join(os.getcwd(), "models", "stable-diffusion", model_filename),
        ]
        
        # Also try to find any .safetensors file in the project directory
        model_files = glob.glob(os.path.join(os.getcwd(), "**", "*.safetensors"), recursive=True)
        search_paths.extend(model_files)
        
        # Check each path
        for path in search_paths:
            if path and os.path.isfile(path):
                return path
        
        return None
            
    def _initialize_model(self) -> bool:
        """Initialize the Stable Diffusion model."""
        if self.model_initialized:
            return True
            
        # Skip initialization if no model path found
        if not self.model_path:
            self.logger.warning("No model path available, skipping model initialization")
            return False
            
        try:
            # Import diffusers here to avoid startup dependency
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, EulerAncestralDiscreteScheduler
            
            self.logger.info(f"Loading model from {self.model_path}")
            
            try:
                # Configure precision based on device
                use_fp16 = self.device.startswith("cuda")
                dtype = torch.float16 if use_fp16 else torch.float32
                self.logger.info(f"Using precision: {dtype}")
                
                # Try loading the model
                self.model = StableDiffusionPipeline.from_single_file(
                    self.model_path,
                    torch_dtype=dtype,
                    use_safetensors=True,
                    local_files_only=True
                )
                
                # Move to device and optimize
                self.model = self.model.to(self.device)
                
                # Set scheduler for better quality/speed
                self.model.scheduler = EulerAncestralDiscreteScheduler.from_config(self.model.scheduler.config)
                self.logger.info("Using EulerAncestralDiscreteScheduler (Euler a)")
                
                # Optimize if on CUDA
                if self.device.startswith("cuda"):
                    self.model.enable_attention_slicing()
                    # Try to enable xformers if available
                    # try:
                    #     import xformers
                    #     self.model.enable_xformers_memory_efficient_attention()
                    #     self.logger.info("Xformers optimization enabled")
                    # except ImportError:
                    #     self.logger.info("Xformers not available")
                        
                self.logger.info("Model loaded successfully")
                self.model_initialized = True
                return True
                
            except Exception as e:
                self.logger.error(f"Error loading model from file: {e}")
                # Fall back to pretrained model
                self.logger.info("Falling back to pretrained model")
                
                try:
                    self.model = StableDiffusionPipeline.from_pretrained(
                        "runwayml/stable-diffusion-v1-5",
                        torch_dtype=torch.float16 if self.device.startswith("cuda") else torch.float32,
                    )
                    self.model = self.model.to(self.device)
                    self.model.scheduler = EulerAncestralDiscreteScheduler.from_config(self.model.scheduler.config)
                    self.logger.info("Using EulerAncestralDiscreteScheduler (Euler a) for fallback model")
                    
                    if self.device.startswith("cuda"):
                        self.model.enable_attention_slicing()
                        
                    self.logger.info("Fallback model loaded successfully")
                    self.model_initialized = True
                    return True
                except Exception as e:
                    self.logger.error(f"Error loading fallback model: {e}")
                    return False
                
        except ImportError as e:
            self.logger.error(f"Diffusers library not found. Install with 'pip install diffusers'. Error: {e}")
            return False
    
    def _initialize_font(self):
        """Initialize font for placeholder images."""
        try:
            # Try a common font path
            self.font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            try:
                # Try Windows font path
                self.font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", 15)
            except IOError:
                # Fallback to default font
                self.logger.warning("Arial font not found. Using Pillow's default font.")
                self.font = ImageFont.load_default()

    def generate_image(self, prompt: str = None, 
                      preset: str = "default", 
                      environment: str = None,
                      activity: str = None,
                      negative_prompt: str = None,
                      size: Tuple[int, int] = None) -> Optional[Image.Image]:
        """
        Generate an image using Stable Diffusion based on the prompt and presets.
        
        Args:
            prompt: Custom text prompt (overrides presets if provided)
            preset: Character preset to use (e.g., "happy", "sad")
            environment: Environment preset to add (e.g., "garden", "beach")
            activity: Activity preset to add (e.g., "reading", "cooking")
            negative_prompt: Custom negative prompt (overrides default if provided)
            size: Custom size as (width, height)
            
        Returns:
            A PIL Image or None if generation failed
        """
        # Handle sized
        if size is None:
            size = (self.width, self.height)
        else:
            # Limit size to reasonable values
            w, h = size
            w = min(max(w, 256), 1536)  # Min 256, Max 1536
            h = min(max(h, 256), 1536)  # Min 256, Max 1536
            size = (w, h)
        
        # Build the final prompt
        final_prompt = self._build_prompt(prompt, preset, environment, activity)
        
        # Set negative prompt
        if negative_prompt is None:
            negative_prompt = self.default_negative
            
        # Log generation request
        self.logger.info(f"Generating image for prompt: '{final_prompt}'")
        self.logger.info(f"Size: {size}, Negative prompt: '{negative_prompt}'")
        
        # Try to initialize and use the model
        if self._initialize_model() and self.model is not None:
            return self._generate_with_model(final_prompt, negative_prompt, size)
        else:
            # Fallback to placeholder
            self.logger.warning("Using placeholder image generation.")
            return self._generate_placeholder(final_prompt, size)
            
    def _build_prompt(self, custom_prompt: str = None, 
                     preset: str = "default", 
                     environment: str = None, 
                     activity: str = None) -> str:
        """Build a complete prompt from components."""
        # Start with character preset
        if preset in self.character_presets:
            base_prompt = self.character_presets[preset]
        else:
            base_prompt = self.character_presets["default"]
            
        # Add environment if specified
        if environment and environment in self.environment_presets:
            base_prompt += f", {self.environment_presets[environment]}"
            
        # Add activity if specified
        if activity and activity in self.activity_presets:
            base_prompt += f", {self.activity_presets[activity]}"
            
        # Override with custom prompt if provided
        if custom_prompt:
            if "1girl" in base_prompt and "1girl" not in custom_prompt.lower():
                # Preserve character definition
                final_prompt = f"{base_prompt}, {custom_prompt}"
            else:
                final_prompt = custom_prompt
        else:
            final_prompt = base_prompt
            
        # Add high quality tags
        if "masterpiece" not in final_prompt:
            final_prompt = f"masterpiece, best quality, {final_prompt}"
            
        return final_prompt
    
    def _generate_with_model(self, prompt: str, negative_prompt: str, 
                           size: Tuple[int, int]) -> Optional[Image.Image]:
        """Generate image using the loaded Stable Diffusion model."""
        if not self.model_initialized or self.model is None:
            self.logger.error("Model not initialized")
            return None
            
        try:
            width, height = size
            
            # Add extra quality improvements to the prompt
            if "masterpiece" in prompt and "best quality" in prompt:
                # Already has quality tags
                enhanced_prompt = prompt
            else:
                # Add quality enhancement tags
                enhanced_prompt = f"masterpiece, best quality, high detail, sharp focus, {prompt}"
            
            # Generate the image
            self.logger.info(f"Generating with model on {self.device}...")
            
            # Perform direct image generation and convert to PIL
            with torch.no_grad():
                # If hires fix is enabled, first generate a lower resolution image, then upscale it
                if self.use_hires_fix:
                    self.logger.info(f"Using high-resolution fix with scale={self.upscale_factor}, denoising={self.denoising_strength}")
                    
                    # Calculate initial resolution (ensuring it's divisible by 8)
                    init_width = int(width / self.upscale_factor)
                    init_height = int(height / self.upscale_factor)
                    
                    # Adjust to make divisible by 8
                    init_width = (init_width // 8) * 8
                    init_height = (init_height // 8) * 8
                    
                    # Make sure we have valid dimensions
                    if init_width < 256:
                        init_width = 256
                    if init_height < 256:
                        init_height = 256
                    
                    # First pass - generate lower resolution image
                    self.logger.info(f"First pass at {init_width}x{init_height} with {self.steps} steps")
                    
                    # Standard settings for first pass
                    first_pass_params = {
                        "prompt": enhanced_prompt,
                        "negative_prompt": negative_prompt,
                        "width": init_width,
                        "height": init_height,
                        "num_inference_steps": self.steps,
                        "guidance_scale": self.guidance_scale
                    }
                    
                    # Generate base image
                    base_image = self.model(**first_pass_params).images[0]
                    
                    # Save the first pass image for reference
                    first_pass_path = os.path.join(self.output_dir, "first_pass_temp.png")
                    base_image.save(first_pass_path)
                    self.logger.info(f"First pass image saved to {first_pass_path}")
                    
                    # Upscale the image using a simple resize
                    # Make sure target dimensions are also divisible by 8
                    target_width = (width // 8) * 8
                    target_height = (height // 8) * 8
                    
                    self.logger.info(f"Second pass at {target_width}x{target_height} with {self.hires_steps} steps")
                    
                    # Standard settings for second pass
                    second_pass_params = {
                        "prompt": enhanced_prompt,
                        "negative_prompt": negative_prompt + ", blurry, low quality, low resolution",  # Enhanced negative prompt
                        "width": target_width,
                        "height": target_height,
                        "num_inference_steps": self.hires_steps,
                        "guidance_scale": self.guidance_scale + 1.0  # Slightly higher guidance for detail
                    }
                    
                    # Generate final image with higher quality settings
                    final_image = self.model(**second_pass_params).images[0]
                    self.logger.info("High-resolution image generation successful")
                    
                    # If the original size is different from the adjusted size, resize it
                    if (target_width, target_height) != (width, height):
                        final_image = final_image.resize((width, height), Image.LANCZOS)
                        
                    return final_image
                else:
                    # Standard single-pass generation
                    # Ensure width/height are divisible by 8
                    adjusted_width = (width // 8) * 8
                    adjusted_height = (height // 8) * 8
                    
                    self.logger.info(f"Standard generation at {adjusted_width}x{adjusted_height} with {self.steps} steps")
                    params = {
                        "prompt": enhanced_prompt,
                        "negative_prompt": negative_prompt,
                        "width": adjusted_width,
                        "height": adjusted_height,
                        "num_inference_steps": self.steps,
                        "guidance_scale": self.guidance_scale
                    }
                    
                    image = self.model(**params).images[0]
                    
                    # If the original size is different from the adjusted size, resize it
                    if (adjusted_width, adjusted_height) != (width, height):
                        image = image.resize((width, height), Image.LANCZOS)
                    
                    self.logger.info("Image generation successful")
                    return image
                
        except Exception as e:
            self.logger.error(f"Error generating image with model: {e}")
            
            # Try alternative approach with simplified settings
            try:
                self.logger.info("Trying alternative generation method...")
                
                # Enhanced prompt for better quality
                enhanced_prompt = f"masterpiece, best quality, highly detailed, {prompt}"
                
                # Simpler generation with standard settings
                adjusted_width = (width // 8) * 8
                adjusted_height = (height // 8) * 8
                
                params = {
                    "prompt": enhanced_prompt,
                    "negative_prompt": negative_prompt,
                    "width": adjusted_width,
                    "height": adjusted_height,
                    "num_inference_steps": 30,  # Fixed number of steps
                    "guidance_scale": 7.0       # Fixed guidance scale
                }
                
                image = self.model(**params).images[0]
                
                # If the original size is different from the adjusted size, resize it
                if (adjusted_width, adjusted_height) != (width, height):
                    image = image.resize((width, height), Image.LANCZOS)
                
                self.logger.info("Alternative image generation successful")
                return image
                
            except Exception as e2:
                self.logger.error(f"Alternative generation also failed: {e2}")
                
                # Last resort - try generating a simple image with placeholder
                return self._generate_placeholder(prompt, size)
                
    def _generate_placeholder(self, prompt: str, size: Tuple[int, int]) -> Image.Image:
        """
        Generate a placeholder image when Stable Diffusion is not available.
        """
        self.logger.info(f"Generating placeholder image for prompt: {prompt}")

        # Create a simple placeholder image
        img_width, img_height = size

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

            # Calculate text bounding box
            bbox = draw.textbbox((0, 0), test_line, font=self.font)
            line_width = bbox[2] - bbox[0]

            if line_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)  # Add the last line

        # Draw the text line by line
        text_color = (255, 255, 255)
        
        # Get line height
        try:
            line_height = draw.textbbox((0, 0), "Tg", font=self.font)[3] + 5  # Add padding
        except AttributeError:
            line_height = 15 + 5  # Fallback

        # Center the text block vertically
        total_text_height = len(lines) * line_height
        start_y = (img_height - total_text_height) // 2
        if start_y < 20:  # Ensure text doesn't start too close to the top
            start_y = 20

        for i, line in enumerate(lines):
            # Calculate text width for centering
            bbox = draw.textbbox((0, 0), line, font=self.font)
            line_width = bbox[2] - bbox[0]
            x_text = (img_width - line_width) // 2

            draw.text((x_text, start_y + i * line_height), line, font=self.font, fill=text_color)

        # Add a placeholder shape (e.g., a circle) below the text
        shape_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
        shape_y = start_y + total_text_height + 50
        if shape_y > img_height - 60:
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
            
    def parse_image_request(self, text: str) -> Dict[str, Any]:
        """
        Parse an image request from natural language.
        
        Args:
            text: The user's text request
            
        Returns:
            Dictionary with parameters for generate_image
        """
        params = {}
        text = text.lower()
        
        # Check for selfie/picture of yourself
        if "selfie" in text or "picture of yourself" in text or "pic of yourself" in text:
            params["preset"] = "selfie"
        
        # Check for emotions
        if "happy" in text or "smiling" in text or "smile" in text:
            params["preset"] = "happy"
        elif "sad" in text or "crying" in text or "unhappy" in text:
            params["preset"] = "sad"
        elif "surprised" in text or "shocked" in text:
            params["preset"] = "surprised"
            
        # Check for pose type
        if "close up" in text or "close-up" in text:
            params["preset"] = "close_up"
        elif "full body" in text:
            params["preset"] = "full_body"
        elif "sitting" in text:
            params["preset"] = "sitting"
            
        # Check for clothing style
        if "elegant" in text or "dress" in text or "formal" in text:
            params["preset"] = "elegant"
        elif "casual" in text:
            params["preset"] = "casual"
            
        # Check for environments
        for env in self.environment_presets:
            if env in text:
                params["environment"] = env
                break
                
        # Check for activities
        for act in self.activity_presets:
            if act in text:
                params["activity"] = act
                break
                
        # If nothing matched, use the text as a custom prompt
        if not params:
            params["prompt"] = text
            
        return params
