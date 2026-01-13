#!/usr/bin/env python3
"""
Example: Using converted RCAN CoreML model in Python
This demonstrates how to test the CoreML model before deploying to iOS/macOS
"""

import numpy as np
from PIL import Image
import coremltools as ct


def load_coreml_model(model_path='models/RCAN_BIX3.mlmodel'):
    """Load CoreML model"""
    print(f"Loading model from {model_path}...")
    model = ct.models.MLModel(model_path)
    print("✅ Model loaded successfully")
    return model


def prepare_image(image_path, target_size=(180, 180)):
    """
    Prepare input image for RCAN model
    
    Args:
        image_path: Path to input image
        target_size: Target size (width, height)
    
    Returns:
        PIL Image ready for model input
    """
    print(f"Loading image: {image_path}")
    image = Image.open(image_path).convert('RGB')
    
    print(f"  Original size: {image.size}")
    
    # Resize to model input size
    image = image.resize(target_size, Image.BICUBIC)
    print(f"  Resized to: {image.size}")
    
    return image


def run_inference(model, input_image):
    """
    Run super-resolution inference
    
    Args:
        model: CoreML model
        input_image: PIL Image
    
    Returns:
        Output PIL Image (upscaled)
    """
    print("\nRunning inference...")
    
    # Convert PIL image to format expected by CoreML
    # The model expects RGB image with values in [0, 255]
    input_dict = {'input_image': input_image}
    
    # Run prediction
    output = model.predict(input_dict)
    
    # Get output image
    output_image = output['output_image']
    
    print(f"✅ Inference complete")
    print(f"  Output size: {output_image.size}")
    
    return output_image


def compare_with_bicubic(input_image, output_image, scale=3):
    """
    Compare RCAN output with simple bicubic upsampling
    
    Args:
        input_image: Input PIL Image
        output_image: RCAN output PIL Image
        scale: Upscaling factor
    """
    print("\n" + "="*60)
    print("Comparison with Bicubic Upsampling")
    print("="*60)
    
    # Create bicubic upsampled version
    bicubic_size = (input_image.size[0] * scale, input_image.size[1] * scale)
    bicubic_output = input_image.resize(bicubic_size, Image.BICUBIC)
    
    print(f"Bicubic output size: {bicubic_output.size}")
    print(f"RCAN output size: {output_image.size}")
    
    # Calculate PSNR (simplified - would need ground truth for real PSNR)
    print("\n💡 Visual comparison:")
    print("  - RCAN should show sharper edges and more details")
    print("  - Bicubic typically shows more blur and artifacts")
    
    return bicubic_output


def save_results(input_image, output_image, bicubic_image, prefix='result'):
    """Save comparison results"""
    print(f"\nSaving results...")
    
    input_image.save(f'{prefix}_input.png')
    output_image.save(f'{prefix}_rcan_output.png')
    bicubic_image.save(f'{prefix}_bicubic_output.png')
    
    print(f"✅ Saved:")
    print(f"  - {prefix}_input.png")
    print(f"  - {prefix}_rcan_output.png")
    print(f"  - {prefix}_bicubic_output.png")


def create_side_by_side_comparison(input_image, bicubic_image, rcan_image, output_path='comparison.png'):
    """Create side-by-side comparison image"""
    print(f"\nCreating comparison image...")
    
    # All images should be same size for comparison
    # Upscale input for visualization
    scale = rcan_image.size[0] // input_image.size[0]
    input_upscaled = input_image.resize(
        (input_image.size[0] * scale, input_image.size[1] * scale),
        Image.NEAREST  # Use nearest to show pixelation
    )
    
    # Create canvas
    width = rcan_image.size[0]
    height = rcan_image.size[1]
    comparison = Image.new('RGB', (width * 3 + 40, height + 60))
    
    # Add labels (simplified - would use PIL.ImageDraw for text)
    comparison.paste(input_upscaled, (10, 40))
    comparison.paste(bicubic_image, (width + 20, 40))
    comparison.paste(rcan_image, (width * 2 + 30, 40))
    
    comparison.save(output_path)
    print(f"✅ Comparison saved to: {output_path}")


def benchmark_model(model, input_size=(180, 180), num_iterations=10):
    """
    Benchmark model performance
    
    Args:
        model: CoreML model
        input_size: Input image size
        num_iterations: Number of iterations for averaging
    """
    print("\n" + "="*60)
    print("Benchmarking Model Performance")
    print("="*60)
    
    import time
    
    # Create dummy input
    dummy_image = Image.new('RGB', input_size)
    
    # Warmup
    print("Warming up...")
    for _ in range(3):
        _ = model.predict({'input_image': dummy_image})
    
    # Benchmark
    print(f"Running {num_iterations} iterations...")
    times = []
    
    for i in range(num_iterations):
        start = time.time()
        _ = model.predict({'input_image': dummy_image})
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed*1000:.1f}ms")
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    
    print(f"\n📊 Results:")
    print(f"  Average: {avg_time*1000:.1f}ms")
    print(f"  Std Dev: {std_time*1000:.1f}ms")
    print(f"  Min: {min(times)*1000:.1f}ms")
    print(f"  Max: {max(times)*1000:.1f}ms")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test RCAN CoreML model')
    parser.add_argument('--model', type=str, default='models/RCAN_BIX3.mlmodel',
                        help='Path to CoreML model')
    parser.add_argument('--input', type=str, required=True,
                        help='Input image path')
    parser.add_argument('--output', type=str, default='output.png',
                        help='Output image path')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run performance benchmark')
    
    args = parser.parse_args()
    
    try:
        # Load model
        model = load_coreml_model(args.model)
        
        # Load and prepare image
        input_image = prepare_image(args.input)
        
        # Run inference
        output_image = run_inference(model, input_image)
        
        # Compare with bicubic
        bicubic_image = compare_with_bicubic(input_image, output_image)
        
        # Save results
        save_results(input_image, output_image, bicubic_image)
        
        # Create comparison
        create_side_by_side_comparison(input_image, bicubic_image, output_image)
        
        # Benchmark if requested
        if args.benchmark:
            benchmark_model(model)
        
        print("\n✅ All done!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())


# Example usage:
# python examples/python_usage_example.py --input test_image.png --benchmark
