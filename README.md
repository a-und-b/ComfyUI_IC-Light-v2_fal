# ComfyUI-IC-Light-v2-fal

Custom node for ComfyUI to integrate the fal.ai IClightV2 API - a powerful image relighting and background replacement tool.

## Features

* Image relighting using fal.ai's IClightV2 model
* Change lighting conditions of objects in your images
* Optional mask support for targeted effects
* Customizable generation parameters (lighting direction, denoise strength, etc.)
* Multiple image generation in a single request
* Seed support for reproducible results

## Prerequisites

* ComfyUI installed and set up
* Python 3.7+
* A fal.ai API key with access to the IClightV2 model

## Installation

1. Clone this repository into your ComfyUI's `custom_nodes` directory:
```
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/yourusername/ComfyUI-IC-Light-v2-fal.git
```

2. Navigate to the cloned directory:
```
cd ComfyUI-IC-Light-v2-fal
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Configure your API key:
   - Copy `config.ini.template` to `config.ini`
   - Add your fal.ai API key to the `config.ini` file

5. Restart ComfyUI if it's already running

## Usage

After installation, you'll find the "IClightV2 (fal.ai)" node in the ComfyUI interface under the "image effects/lighting" category. Connect an input image to relight or change its background based on your prompt.

### Parameters

- **image**: Input image to be relit
- **prompt**: Text prompt describing the desired lighting or background
- **negative_prompt**: Negative prompt to guide the model away from certain concepts
- **num_inference_steps**: Number of denoising steps (impacts generation time and quality)
- **guidance_scale**: Higher values enforce the prompt more strictly
- **seed**: Random seed for reproducible results
- **initial_latent**: Lighting direction - None, Left, Right, Top, or Bottom
- **enable_hr_fix**: Enable high-resolution fix for better quality
- **lowres_denoise**: Strength for low-resolution pass
- **highres_denoise**: Strength for high-resolution pass (used with HR fix)
- **hr_downscale**: Downscale factor for high-resolution pass
- **num_images**: Number of variations to generate
- **cfg**: Classifier-Free Guidance scale for generation
- **output_format**: Output image format (JPEG or PNG)
- **mask** (optional): Mask to target specific areas of the image

## Example Workflow

The basic workflow for using the IClightV2 node:

1. Load an image using a ComfyUI image loader node
2. Connect the image to the IClightV2 node
3. Set your prompt and parameters
4. Connect the output to a Preview or Save node

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

* fal.ai for providing the IClightV2 API
* ComfyUI for the extensible UI framework 