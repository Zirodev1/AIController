#!/usr/bin/env python
"""
Stable Diffusion Setup Helper

This script helps users set up their Stable Diffusion model for the AI companion.
It automates the process of:
1. Locating existing models on the system
2. Downloading a model if needed (using HuggingFace Hub)
3. Configuring the .env file
"""
import os
import glob
import sys
import logging
import argparse
import json
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_sd_models() -> List[str]:
    """Find Stable Diffusion models on the system in common locations."""
    # Common paths to search
    search_paths = [
        # Current directory
        os.path.join(os.getcwd(), "*.safetensors"),
        os.path.join(os.getcwd(), "*.ckpt"),
        
        # Models directory in the project
        os.path.join(os.getcwd(), "models", "**", "*.safetensors"),
        os.path.join(os.getcwd(), "models", "**", "*.ckpt"),
        
        # Common SD WebUI locations - Windows
        os.path.join("C:", os.sep, "stable-diffusion-webui", "models", "**", "*.safetensors"),
        os.path.join("C:", os.sep, "stable-diffusion-webui-*", "models", "**", "*.safetensors"),
        os.path.join(os.path.expanduser("~"), "Desktop", "stable-diffusion-webui*", "models", "**", "*.safetensors"),
        
        # Common SD WebUI locations - Linux/Mac
        os.path.join(os.path.expanduser("~"), "stable-diffusion-webui", "models", "**", "*.safetensors"),
        os.path.join(os.path.expanduser("~"), "stable-diffusion", "models", "**", "*.safetensors"),
        
        # Additional SD model directories
        os.path.join(os.path.expanduser("~"), "Downloads", "*.safetensors"),
        os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "**", "*.safetensors"),
    ]
    
    # Find all model files
    model_paths = []
    for path in search_paths:
        try:
            found = glob.glob(path, recursive=True)
            model_paths.extend(found)
        except Exception as e:
            logger.warning(f"Error searching path {path}: {e}")
    
    # Remove duplicates and sort
    unique_paths = list(set(model_paths))
    return sorted(unique_paths)

def download_sd_model(model_name: str = "runwayml/stable-diffusion-v1-5", 
                     output_dir: str = None) -> Optional[str]:
    """
    Download a Stable Diffusion model from HuggingFace Hub.
    
    Args:
        model_name: Name of the model on HuggingFace
        output_dir: Directory to save the model (default: ./models/stable-diffusion)
        
    Returns:
        Path to the downloaded model or None if failed
    """
    try:
        # Only import huggingface_hub if needed
        from huggingface_hub import snapshot_download
    except ImportError:
        logger.error("huggingface_hub package not installed. Install with: pip install huggingface_hub")
        return None
        
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "models", "stable-diffusion")
        
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        logger.info(f"Downloading model {model_name}...")
        # Download the model
        model_path = snapshot_download(
            repo_id=model_name,
            local_dir=os.path.join(output_dir, model_name.split("/")[-1]),
            local_dir_use_symlinks=False
        )
        logger.info(f"Model downloaded to {model_path}")
        
        # Find the .safetensors file
        model_files = glob.glob(os.path.join(model_path, "*.safetensors"))
        if model_files:
            return model_files[0]
        else:
            # Try to find any model file
            model_files = glob.glob(os.path.join(model_path, "**", "*.safetensors"), recursive=True)
            if model_files:
                return model_files[0]
            else:
                logger.warning(f"No .safetensors file found in {model_path}")
                return None
    
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return None

def update_env_file(model_path: str) -> bool:
    """
    Update the .env file with the model path.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True if successful, False otherwise
    """
    env_file = os.path.join(os.getcwd(), ".env")
    env_example = os.path.join(os.getcwd(), ".env.example")
    
    # Create from example if it doesn't exist
    if not os.path.exists(env_file) and os.path.exists(env_example):
        with open(env_example, "r") as example:
            with open(env_file, "w") as env:
                env.write(example.read())
    
    # If env file exists, update it
    if os.path.exists(env_file):
        # Read existing content
        with open(env_file, "r") as f:
            lines = f.readlines()
        
        # Update or add the SD_MODEL_PATH
        found = False
        for i, line in enumerate(lines):
            if line.startswith("SD_MODEL_PATH="):
                lines[i] = f"SD_MODEL_PATH={model_path}\n"
                found = True
                break
        
        if not found:
            lines.append(f"\n# Stable Diffusion model path\nSD_MODEL_PATH={model_path}\n")
        
        # Write back
        with open(env_file, "w") as f:
            f.writelines(lines)
        
        logger.info(f"Updated .env file with model path: {model_path}")
        return True
    
    # If no env file, create a new one
    else:
        try:
            with open(env_file, "w") as f:
                f.write(f"# Stable Diffusion model path\nSD_MODEL_PATH={model_path}\n")
            logger.info(f"Created .env file with model path: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating .env file: {e}")
            return False

def update_sd_config(model_path: str) -> bool:
    """
    Update the sd_config.json file with the model path.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True if successful, False otherwise
    """
    config_file = os.path.join(os.getcwd(), "sd_config.json")
    
    # Create default config if it doesn't exist
    if not os.path.exists(config_file):
        default_config = {
            "model_path": model_path,
            "settings": {
                "sampler_name": "Euler a",
                "steps": 30,
                "hires_fix": True,
                "width": 1024,
                "height": 1360,
                "hr_upscaler": "R-ESRGAN 4x+",
                "hr_scale": 1.5,
                "hr_second_pass_steps": 20,
                "denoising_strength": 0.7,
                "cfg_scale": 7,
                "negative_prompt": "bad quality, worst quality, worst detail, sketch, censor"
            },
            "character_presets": {
                "default": "1girl, beautiful, looking at viewer, standing",
                "happy": "1girl, beautiful, looking at viewer, happy, smiling",
                "sad": "1girl, beautiful, looking at viewer, sad, crying",
                "surprised": "1girl, beautiful, looking at viewer, surprised, shocked",
                "casual": "1girl, beautiful, looking at viewer, casual clothes",
                "elegant": "1girl, beautiful, looking at viewer, elegant dress"
            }
        }
        
        try:
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created sd_config.json with model path: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating sd_config.json: {e}")
            return False
    
    # Update existing config
    else:
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            # Update model path
            config["model_path"] = model_path
            
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Updated sd_config.json with model path: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error updating sd_config.json: {e}")
            return False

def test_model_loading(model_path: str) -> bool:
    """
    Test loading the model to verify it works.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Only import if needed
        from diffusers import StableDiffusionPipeline
        import torch
        
        logger.info(f"Testing model loading: {model_path}")
        
        # Set a small portion of GPU memory if CUDA
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if device == "cuda":
            # Limit memory usage for testing
            torch.cuda.set_per_process_memory_fraction(0.2)
        
        # Try loading the model
        pipeline = StableDiffusionPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
            device_map={"": device}
        )
        
        # Release memory
        del pipeline
        if device == "cuda":
            torch.cuda.empty_cache()
        
        logger.info("Model loaded successfully!")
        return True
    
    except ImportError:
        logger.warning("diffusers or torch package not installed. Can't test model loading.")
        return True  # Still return True so setup process continues
    
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def get_dependencies_status() -> Dict[str, bool]:
    """Check if required dependencies are installed."""
    dependencies = {
        "torch": False,
        "diffusers": False,
        "transformers": False,
        "safetensors": False,
        "huggingface_hub": False,
        "accelerate": False,
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies

def print_header():
    """Print a nice header."""
    print("\n" + "=" * 60)
    print("  🖼️  STABLE DIFFUSION SETUP FOR AI COMPANION  🖼️")
    print("=" * 60)
    print("This utility will help you set up a Stable Diffusion model\n")

def main():
    """Main function to run the setup utility."""
    print_header()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Set up Stable Diffusion for AI companion")
    parser.add_argument("--download", action="store_true", help="Force download a new model")
    parser.add_argument("--model", default="runwayml/stable-diffusion-v1-5", help="Model to download from HuggingFace")
    args = parser.parse_args()
    
    # Check dependencies
    deps = get_dependencies_status()
    missing = [dep for dep, installed in deps.items() if not installed]
    
    if missing:
        print("\n⚠️ Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nYou'll need to install these to use Stable Diffusion.")
        print("You can install them with:")
        print("  pip install " + " ".join(missing))
        
        # Continue but warn the user
        install = input("\nInstall missing dependencies now? (y/n): ").lower()
        if install == 'y':
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
                print("Dependencies installed successfully!")
            except Exception as e:
                print(f"Error installing dependencies: {e}")
                print("Please install them manually.")
    
    # If download is forced, do it first
    model_path = None
    if args.download:
        print(f"\nDownloading model '{args.model}'...")
        model_path = download_sd_model(args.model)
        if model_path:
            print(f"Model downloaded successfully to: {model_path}")
        else:
            print("Failed to download model. Will try to find existing models.")
    
    # If we don't have a model path yet, search for models
    if not model_path:
        print("\nSearching for Stable Diffusion models on your system...")
        models = find_sd_models()
        
        if not models:
            print("\nNo models found. Would you like to download one?")
            download = input("Download model? (y/n): ").lower()
            if download == 'y':
                print(f"\nDownloading model '{args.model}'...")
                model_path = download_sd_model(args.model)
                if model_path:
                    print(f"Model downloaded successfully to: {model_path}")
                else:
                    print("Failed to download model. Please download a model manually.")
                    print("See: https://huggingface.co/CompVis/stable-diffusion-v1-4")
                    return
        else:
            # Show found models
            print(f"\nFound {len(models)} model(s):")
            for i, model in enumerate(models):
                print(f"  [{i+1}] {os.path.basename(model)} ({model})")
            
            # Let user choose a model
            choice = input("\nSelect a model (number) or press Enter for the first one: ")
            if choice.strip():
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(models):
                        model_path = models[index]
                    else:
                        print("Invalid selection. Using the first model.")
                        model_path = models[0]
                except ValueError:
                    print("Invalid input. Using the first model.")
                    model_path = models[0]
            else:
                model_path = models[0]
    
    # Test the model
    if model_path:
        print(f"\nSelected model: {model_path}")
        
        # Update configuration files
        update_env_file(model_path)
        update_sd_config(model_path)
        
        # Test model loading if possible
        if all(deps[d] for d in ["torch", "diffusers", "safetensors"]):
            print("\nTesting model loading...")
            if test_model_loading(model_path):
                print("\n✅ Model tested successfully!")
            else:
                print("\n⚠️ Model loading failed. The model might be incompatible.")
        else:
            print("\n⚠️ Can't test model loading due to missing dependencies.")
        
        # Final instructions
        print("\n🎉 Setup complete! You can now use the character image generation system.")
        print("\nTry it out with:")
        print("  python test_character_image.py --preset happy")
        print("  python character_image_demo.py --show")
    else:
        print("\n❌ Setup failed. No model selected.")

if __name__ == "__main__":
    main() 