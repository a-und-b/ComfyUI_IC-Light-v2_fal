import os
import json
import time
import tempfile
import configparser
import uuid
import requests
import numpy as np
from io import BytesIO
from PIL import Image

import folder_paths
from comfy.model_management import get_torch_device

# FAL.AI API INTEGRATION
try:
    import fal_client
except ImportError:
    print("Warning: fal_client not installed, IcLightV2Node will not work")
    print("Please install with: pip install fal-client")

# Model ID for IClightV2 on fal.ai
IC_LIGHT_V2_MODEL_ID = "fal-ai/iclight-v2"

class IcLightV2Node:
    """
    ComfyUI node for generating images using fal.ai's IClightV2 model
    """
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.config = self._load_config()
        self.api_key = self._get_api_key()
        self.temp_files = []
        
        # Configure the FAL client if API key is present
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key
    
    def _load_config(self):
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
        
        if os.path.exists(config_path):
            config.read(config_path)
            return config
        else:
            # Create a default config
            config["falai"] = {"api_key": ""}
            return config
    
    def _get_api_key(self):
        """Get API key from config or environment variable"""
        # Check environment variable first
        api_key = os.environ.get("FAL_KEY", None)
        
        # If not in environment, try config
        if not api_key and "falai" in self.config and "api_key" in self.config["falai"]:
            api_key = self.config["falai"]["api_key"]
            
        return api_key
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define the input parameters for the node"""
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "image_size": (["square_hd", "portrait_hd", "landscape_hd", "square", "portrait", "landscape"], {"default": "square_hd"}),
                "guidance_scale": ("FLOAT", {"default": 7.5, "min": 1.0, "max": 20.0, "step": 0.1}),
                "num_inference_steps": ("INT", {"default": 50, "min": 1, "max": 100, "step": 1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
            },
            "optional": {}
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    CATEGORY = "image generation"
    
    def generate(self, prompt, negative_prompt, image_size, guidance_scale, num_inference_steps, seed, num_images):
        """Generate images using fal.ai's IClightV2 model"""
        
        if not self.api_key:
            raise ValueError("No FAL API key found. Please set it in config.ini or as FAL_KEY environment variable.")
        
        # Set up API request parameters
        request_params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image_size": image_size,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "num_images": num_images
        }
        
        # Add seed if provided (not -1)
        if seed != -1:
            request_params["seed"] = seed
        
        try:
            # Make API request
            print(f"Sending request to fal.ai IClightV2 API with params: {request_params}")
            
            handler = fal_client.submit(
                IC_LIGHT_V2_MODEL_ID,
                arguments=request_params,
            )
            
            # Get results
            result = handler.get()
            print(f"Received response from fal.ai")
            
            # Process images
            images = []
            
            for img_data in result.get("images", []):
                # Get image URL
                img_url = img_data.get("url")
                if not img_url:
                    continue
                
                # Download image
                response = requests.get(img_url)
                if response.status_code != 200:
                    print(f"Failed to download image: {response.status_code}")
                    continue
                
                # Load image
                img = Image.open(BytesIO(response.content))
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save locally
                filename = f"iclight_v2_{uuid.uuid4()}.png"
                save_path = os.path.join(self.output_dir, filename)
                img.save(save_path)
                
                # Convert to ComfyUI format (numpy array)
                img_tensor = np.array(img).astype(np.float32) / 255.0
                images.append(img_tensor)
            
            # Stack images for ComfyUI output format
            if images:
                output_images = np.stack(images)
                return (output_images,)
            else:
                raise ValueError("No images were generated or could be processed")
                
        except Exception as e:
            print(f"Error generating images with IClightV2: {str(e)}")
            raise
    
    def __del__(self):
        """Clean up any temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass 