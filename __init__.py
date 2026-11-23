from .iclight_fal_node import IcLightV2Node

NODE_CLASS_MAPPINGS = {
    "ICLightV2": IcLightV2Node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ICLightV2": "AB IC-Light V2 (fal.ai)"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
