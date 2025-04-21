#!/usr/bin/env python3
"""
Simple test script to validate the IcLightV2Node class
"""

import os
import sys

# Add the current directory to path if not already
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the node class
from iclight_fal_node import IcLightV2Node

def test_node_input_validation():
    """Test that the node's inputs are valid"""
    # Get the node's inputs
    inputs = IcLightV2Node.INPUT_TYPES()
    
    # Validate required inputs
    required = inputs["required"]
    assert "prompt" in required, "Node should have a 'prompt' input"
    assert "negative_prompt" in required, "Node should have a 'negative_prompt' input"
    assert "image_size" in required, "Node should have an 'image_size' input"
    assert "guidance_scale" in required, "Node should have a 'guidance_scale' input"
    assert "num_inference_steps" in required, "Node should have a 'num_inference_steps' input"
    assert "seed" in required, "Node should have a 'seed' input"
    assert "num_images" in required, "Node should have a 'num_images' input"
    
    print("✅ Input validation passed")

def test_node_output_validation():
    """Test that the node's outputs are valid"""
    # Check return types
    assert IcLightV2Node.RETURN_TYPES == ("IMAGE",), "Node should return an IMAGE"
    assert IcLightV2Node.RETURN_NAMES == ("images",), "Node should name its output 'images'"
    
    print("✅ Output validation passed")

def test_node_instantiation():
    """Test that the node can be instantiated"""
    try:
        node = IcLightV2Node()
        print("✅ Node instantiation passed")
    except Exception as e:
        print(f"❌ Node instantiation failed: {str(e)}")
        raise

def main():
    """Run the tests"""
    print("Testing IcLightV2Node...")
    test_node_input_validation()
    test_node_output_validation()
    test_node_instantiation()
    print("All tests passed! ✅")

if __name__ == "__main__":
    main() 