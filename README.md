# ComfyUI-IC-Light-v2-fal

Custom node for ComfyUI to integrate the fal.ai IClightV2 API.

## Features

* Text-to-image generation using fal.ai's IClightV2 model
* Customizable generation parameters (image size, guidance scale, etc.)
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

After installation, you'll find the "IClightV2 (fal.ai)" node in the ComfyUI interface. Connect it to your workflow to generate images using the IClightV2 model via fal.ai.

### Parameters

- **prompt**: Text prompt for image generation
- **negative_prompt**: Negative prompt to guide the model away from certain concepts
- **image_size**: Output image size (square, portrait, landscape variants)
- **guidance_scale**: Higher values enforce the prompt more strictly
- **num_inference_steps**: Number of denoising steps (impacts generation time and quality)
- **seed**: Random seed for reproducible results
- **num_images**: Number of images to generate

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

* fal.ai for providing the IClightV2 API
* ComfyUI for the extensible UI framework 