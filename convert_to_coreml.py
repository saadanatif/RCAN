#!/usr/bin/env python3
"""
Convert RCAN PyTorch model to CoreML format
Supports RCAN_BIX3.pt model (3x super-resolution)
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
import coremltools as ct
from coremltools.models.neural_network import quantization_utils
import urllib.request
from pathlib import Path

# Add RCAN code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RCAN_TestCode', 'code'))

from model import rcan, common

class Args:
    """Arguments for RCAN model initialization"""
    def __init__(self, scale=3):
        self.scale = [scale]
        self.n_resgroups = 10
        self.n_resblocks = 20
        self.n_feats = 64
        self.reduction = 16
        self.n_colors = 3
        self.rgb_range = 255
        self.res_scale = 1
        self.data_train = 'DIV2K'  # Use DIV2K mean

def download_model(output_path='models/RCAN_BIX3.pt'):
    """Download RCAN_BIX3.pt model from Google Drive"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if os.path.exists(output_path):
        print(f"Model already exists at {output_path}")
        return output_path
    
    print("Downloading RCAN_BIX3.pt model...")
    print("Note: You need to manually download the model from:")
    print("  - Dropbox: https://www.dropbox.com/s/qm9vc0p0w9i4s0n/models_ECCV2018RCAN.zip?dl=0")
    print("  - BaiduYun: https://pan.baidu.com/s/1bkoJKmdOcvLhOFXHVkFlKA")
    print("  - Google Drive: https://drive.google.com/file/d/1U0RmWkkacyw0HNC7CBts2LcX1ewAulCn/view?usp=sharing")
    print(f"\nPlease download and extract RCAN_BIX3.pt to: {output_path}")
    sys.exit(1)

def load_rcan_model(model_path, scale=3):
    """Load RCAN PyTorch model"""
    print(f"Loading RCAN model from {model_path}...")
    
    # Create model
    args = Args(scale=scale)
    model = rcan.make_model(args)
    
    # Load weights
    state_dict = torch.load(model_path, map_location='cpu')
    model.load_state_dict(state_dict, strict=False)
    
    # Set to evaluation mode
    model.eval()
    
    print(f"Model loaded successfully!")
    print(f"  - Scale: {scale}x")
    print(f"  - Residual Groups: {args.n_resgroups}")
    print(f"  - Residual Blocks per Group: {args.n_resblocks}")
    print(f"  - Feature Maps: {args.n_feats}")
    
    return model

def convert_to_coreml(model, output_path, input_shape=(1, 3, 180, 180)):
    """
    Convert PyTorch RCAN model to CoreML
    
    Args:
        model: PyTorch RCAN model
        output_path: Path to save CoreML model
        input_shape: Input tensor shape (batch, channels, height, width)
    """
    print(f"\nConverting to CoreML...")
    print(f"  Input shape: {input_shape}")
    
    # Create example input
    example_input = torch.randn(*input_shape)
    
    # Trace the model
    print("  Tracing model...")
    traced_model = torch.jit.trace(model, example_input)
    
    # Convert to CoreML
    print("  Converting to CoreML format...")
    
    # Define input
    batch, channels, height, width = input_shape
    
    mlmodel = ct.convert(
        traced_model,
        inputs=[ct.ImageType(
            name="input_image",
            shape=(1, 3, height, width),
            scale=1.0/255.0,  # Normalize to [0, 1]
            bias=[0, 0, 0],
            color_layout=ct.colorlayout.RGB
        )],
        outputs=[ct.ImageType(
            name="output_image",
            scale=1.0/255.0,
            bias=[0, 0, 0]
        )],
        compute_units=ct.ComputeUnit.ALL,
        minimum_deployment_target=ct.target.iOS15
    )
    
    # Set model metadata
    mlmodel.author = 'RCAN - Yulun Zhang et al.'
    mlmodel.license = 'Apache License 2.0'
    mlmodel.short_description = 'RCAN (Residual Channel Attention Network) for 3x image super-resolution'
    mlmodel.version = '1.0'
    
    # Save the model
    print(f"  Saving CoreML model to {output_path}...")
    mlmodel.save(output_path)
    
    print(f"✓ CoreML model saved successfully!")
    
    # Get model size
    model_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Model size: {model_size:.2f} MB")
    
    return mlmodel

def quantize_model(model_path, output_path):
    """Quantize CoreML model to reduce size"""
    print(f"\nQuantizing model...")
    
    # Load model
    model = ct.models.MLModel(model_path)
    
    # Quantize to 16-bit
    quantized_model = quantization_utils.quantize_weights(model, nbits=16)
    
    # Save quantized model
    quantized_model.save(output_path)
    
    original_size = os.path.getsize(model_path) / (1024 * 1024)
    quantized_size = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"✓ Quantized model saved!")
    print(f"  Original size: {original_size:.2f} MB")
    print(f"  Quantized size: {quantized_size:.2f} MB")
    print(f"  Reduction: {(1 - quantized_size/original_size)*100:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Convert RCAN PyTorch model to CoreML')
    parser.add_argument('--model_path', type=str, default='models/RCAN_BIX3.pt',
                        help='Path to RCAN PyTorch model')
    parser.add_argument('--output', type=str, default='models/RCAN_BIX3.mlmodel',
                        help='Output path for CoreML model')
    parser.add_argument('--scale', type=int, default=3,
                        help='Super-resolution scale factor')
    parser.add_argument('--input_height', type=int, default=180,
                        help='Input image height (must be divisible by scale)')
    parser.add_argument('--input_width', type=int, default=180,
                        help='Input image width (must be divisible by scale)')
    parser.add_argument('--quantize', action='store_true',
                        help='Quantize model to 16-bit for smaller size')
    parser.add_argument('--download', action='store_true',
                        help='Download model (shows download instructions)')
    
    args = parser.parse_args()
    
    # Check if model needs to be downloaded
    if args.download or not os.path.exists(args.model_path):
        download_model(args.model_path)
        return
    
    # Validate input dimensions
    if args.input_height % args.scale != 0 or args.input_width % args.scale != 0:
        print(f"Error: Input dimensions ({args.input_height}x{args.input_width}) must be divisible by scale ({args.scale})")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    
    try:
        # Load PyTorch model
        model = load_rcan_model(args.model_path, scale=args.scale)
        
        # Convert to CoreML
        input_shape = (1, 3, args.input_height, args.input_width)
        mlmodel = convert_to_coreml(model, args.output, input_shape)
        
        # Optionally quantize
        if args.quantize:
            quantized_path = args.output.replace('.mlmodel', '_quantized.mlmodel')
            quantize_model(args.output, quantized_path)
        
        print(f"\n✅ Conversion complete!")
        print(f"\nOutput files:")
        print(f"  - {args.output}")
        if args.quantize:
            print(f"  - {quantized_path}")
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
