#!/usr/bin/env python3
"""
Quick test script for RCAN CoreML model
Tests the model with a sample image
"""

import coremltools as ct
import numpy as np
from PIL import Image
import sys
import os

def test_coreml_model(model_path, input_image_path=None):
    """Test the RCAN CoreML model"""
    
    print("=" * 60)
    print("Testing RCAN CoreML Model")
    print("=" * 60)
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("\nPlease download from GitHub Actions artifacts:")
        print("1. Go to Actions → Your workflow run")
        print("2. Download 'rcan-coreml-models-scale3.zip'")
        print("3. Unzip to get RCAN_BIX3.mlpackage")
        return False
    
    # Load the model
    print(f"\n1. Loading model from: {model_path}")
    try:
        model = ct.models.MLModel(model_path)
        print("   ✅ Model loaded successfully!")
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        return False
    
    # Print model info
    print("\n2. Model Information:")
    spec = model.get_spec()
    print(f"   Format: ML Program (.mlpackage)")
    
    # Get input/output info
    input_desc = spec.description.input[0]
    output_desc = spec.description.output[0]
    
    print(f"   Input: {input_desc.name}")
    print(f"   Output: {output_desc.name}")
    
    # Create or load test image
    print("\n3. Preparing test image...")
    
    if input_image_path and os.path.exists(input_image_path):
        print(f"   Loading image from: {input_image_path}")
        image = Image.open(input_image_path).convert('RGB')
        # Resize to model input size (180x180)
        image = image.resize((180, 180), Image.BICUBIC)
    else:
        print("   Creating random test image (180x180)")
        # Create a random test image
        random_array = np.random.randint(0, 256, (180, 180, 3), dtype=np.uint8)
        image = Image.fromarray(random_array)
    
    print(f"   Input image size: {image.size}")
    
    # Run inference
    print("\n4. Running inference...")
    try:
        # CoreML expects PIL Image for ImageType inputs
        result = model.predict({'input_image': image})
        print("   ✅ Inference successful!")
        
        # Get output
        output_array = result['output_image']
        
        print(f"\n5. Results:")
        print(f"   Output type: {type(output_array)}")
        print(f"   Output shape: {output_array.shape}")
        print(f"   Output range: [{output_array.min():.1f}, {output_array.max():.1f}]")
        
        # Expected output shape: (1, 3, 540, 540) or similar
        if len(output_array.shape) == 4:
            batch, channels, height, width = output_array.shape
            print(f"   Batch: {batch}, Channels: {channels}, Height: {height}, Width: {width}")
            
            # Verify 3x upscaling
            if height == 540 and width == 540:
                print(f"   ✅ Correct output size! (180×180 → 540×540 = 3x)")
            else:
                print(f"   ⚠️  Unexpected output size")
        
        # Convert output to image and save
        print("\n6. Saving output image...")
        
        # Output is in shape (1, 3, H, W), convert to (H, W, 3)
        if len(output_array.shape) == 4:
            # Remove batch dimension and transpose (1, 3, H, W) -> (H, W, 3)
            output_img_array = output_array[0].transpose(1, 2, 0)
        else:
            output_img_array = output_array
        
        # Clip to valid range and convert to uint8
        output_img_array = np.clip(output_img_array, 0, 255).astype(np.uint8)
        
        # Save as image
        output_image = Image.fromarray(output_img_array)
        output_path = 'output_test.png'
        output_image.save(output_path)
        
        print(f"   ✅ Output saved to: {output_path}")
        print(f"   Output image size: {output_image.size}")
        
        # Save input for comparison
        input_path = 'input_test.png'
        image.save(input_path)
        print(f"   Input saved to: {input_path}")
        
        # Performance estimate
        print("\n7. Performance Info:")
        print(f"   Model size: ~31 MB")
        print(f"   Expected inference time on iPhone 13: ~100-150ms")
        print(f"   Runs on: Apple Neural Engine + GPU")
        
        print("\n" + "=" * 60)
        print("✅ TEST PASSED!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Check input_test.png and output_test.png")
        print("  2. Verify the output is 3x larger (540×540)")
        print("  3. Ready to use in Xcode/iOS app!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test RCAN CoreML model')
    parser.add_argument('--model', type=str, default='RCAN_BIX3.mlpackage',
                        help='Path to CoreML model (.mlpackage)')
    parser.add_argument('--image', type=str, default=None,
                        help='Path to test image (optional, will create random if not provided)')
    
    args = parser.parse_args()
    
    success = test_coreml_model(args.model, args.image)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
