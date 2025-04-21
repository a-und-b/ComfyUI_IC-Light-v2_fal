import os
import json
import time
import tempfile
import configparser
import uuid
import requests
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import torch

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
    ComfyUI node for relighting images using fal.ai's IClightV2 model
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
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "num_inference_steps": ("INT", {"default": 28, "min": 1, "max": 100, "step": 1}),
                "guidance_scale": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "initial_latent": (["None", "Left", "Right", "Top", "Bottom"], {"default": "None"}),
                "enable_hr_fix": ("BOOLEAN", {"default": False}),
                "lowres_denoise": ("FLOAT", {"default": 0.98, "min": 0.0, "max": 1.0, "step": 0.01}),
                "highres_denoise": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.01}),
                "hr_downscale": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 0.9, "step": 0.01}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4, "step": 1}),
                "cfg": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "relight"
    CATEGORY = "image effects/lighting"
    
    def _pil_to_base64(self, pil_image, format="JPEG", quality=95):
        """Convert PIL image to base64 data URI"""
        buffered = BytesIO()
        pil_image.save(buffered, format=format, quality=quality)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_str}"
    
    def _create_temp_image(self, image_array, format="JPEG"):
        """Create a temporary image file from a numpy array or torch tensor"""
        # Convert tensor to numpy array if it's a tensor
        if isinstance(image_array, torch.Tensor):
            image_array = image_array.cpu().numpy()
        
        # Convert array to PIL Image
        img = Image.fromarray((image_array * 255).astype(np.uint8))
        
        # Convert to RGB if saving as JPEG (JPEG doesn't support alpha channel)
        if format.upper() == "JPEG" and img.mode == "RGBA":
            img = img.convert("RGB")
        
        # Create temp file
        fd, file_path = tempfile.mkstemp(suffix=f".{format.lower()}")
        os.close(fd)
        self.temp_files.append(file_path)  # For cleanup later
        
        # Save image
        img.save(file_path, format=format, quality=95)
        return file_path
    
    def relight(self, image, prompt, negative_prompt, num_inference_steps, guidance_scale, seed, 
                initial_latent, enable_hr_fix, lowres_denoise, highres_denoise, hr_downscale, 
                num_images, cfg, output_format, mask=None):
        """Relight images using fal.ai's IClightV2 model"""
        
        if not self.api_key:
            raise ValueError("No FAL API key found. Please set it in config.ini or as FAL_KEY environment variable.")
        
        # Convert the input image from ComfyUI's format (numpy array) to a file or data URI
        input_img_format = "PNG" if output_format.lower() == "png" else "JPEG"
        input_image_path = self._create_temp_image(image[0], format=input_img_format)
        
        # Set up API request parameters
        request_params = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "initial_latent": initial_latent,
            "enable_hr_fix": enable_hr_fix,
            "lowres_denoise": lowres_denoise,
            "highres_denoise": highres_denoise,
            "hr_downscale": hr_downscale,
            "num_images": num_images,
            "cfg": cfg,
            "output_format": output_format,
        }
        
        # Add seed if provided (not -1)
        if seed != -1:
            request_params["seed"] = seed
        
        # Upload the input image to fal.ai
        try:
            input_image_url = fal_client.upload_file(input_image_path)
            request_params["image_url"] = input_image_url
            
            # If mask is provided, create and upload it too
            if mask is not None:
                mask_image_path = self._create_temp_image(mask, format=input_img_format)
                mask_image_url = fal_client.upload_file(mask_image_path)
                request_params["mask_image_url"] = mask_image_url
            
            # Make API request
            print(f"Sending request to fal.ai IClightV2 API with params: {request_params}")
            
            # Define callback for logs
            def on_queue_update(update):
                if hasattr(update, 'logs'):
                    for log in update.logs:
                        print(f"IClightV2 API: {log.get('message', '')}")
            
            # Submit request with logs
            result = fal_client.subscribe(
                IC_LIGHT_V2_MODEL_ID,
                arguments=request_params,
                with_logs=True,
                on_queue_update=on_queue_update,
            )
            
            print(f"Received response from fal.ai IClightV2")
            
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
                if img.mode == "RGBA" and output_format.lower() == "jpeg":
                    img = img.convert("RGB")
                elif img.mode not in ["RGB", "RGBA"]:
                    img = img.convert("RGB")
                
                # Save locally
                filename = f"iclight_v2_{uuid.uuid4()}.{output_format}"
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
        finally:
            # Clean up temporary files
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file}: {str(e)}")
            self.temp_files = []
    
    def __del__(self):
        """Clean up any temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass 