import os
import sys
import folder_paths

# Add the directory to the system path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the node class
from iclight_fal_node import IcLightV2Node

# Register as a ComfyUI Node with proper categorization
NODE_CLASS_MAPPINGS = {
    "ICLightV2": IcLightV2Node
}

# Provide category info for UI with proper naming convention
NODE_DISPLAY_NAME_MAPPINGS = {
    "ICLightV2": "IC-Light V2 (fal.ai)"
}

# Optional icons for the node
WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']