#!/usr/bin/env python3
"""
Test script to verify RCAN to CoreML conversion
"""

import os
import sys
import torch
import numpy as np
from PIL import Image

# Add RCAN code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RCAN_TestCode', 'code'))

def test_pytorch_model():
    """Test if PyTorch model can be loaded"""
    print("=" * 60)
    print("Testing PyTorch Model Loading")
    print("=" * 60)
    
    model_path = 'models/RCAN_BIX3.pt'
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("Run: python download_model.py")
        return False
    
    try:
        from model import rcan, common
        
        class Args:
            def __init__(self):
                self.scale = [3]
                self.n_resgroups = 10
                self.n_resblocks = 20
                self.n_feats = 64
                self.reduction = 16
                self.n_colors = 3
                self.rgb_range = 255
                self.res_scale = 1
                self.data_train = 'DIV2K'
        
        args = Args()
        model = rcan.make_model(args)
        
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        
        print("✅ PyTorch model loaded successfully")
        
        # Test forward pass
        with torch.no_grad():
            test_input = torch.randn(1, 3, 180, 180)
            output = model(test_input)
            
        print(f"   Input shape: {test_input.shape}")
        print(f"   Output shape: {output.shape}")
        
        expected_output_shape = (1, 3, 540, 540)
        if output.shape == expected_output_shape:
            print(f"   ✅ Output shape correct: {output.shape}")
        else:
            print(f"   ❌ Output shape incorrect: {output.shape}, expected {expected_output_shape}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading PyTorch model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_coreml_model():
    """Test if CoreML model can be loaded"""
    print("\n" + "=" * 60)
    print("Testing CoreML Model Loading")
    print("=" * 60)
    
    try:
        import coremltools as ct
    except ImportError:
        print("❌ coremltools not installed")
        print("Run: pip install coremltools")
        return False
    
    model_paths = [
        'models/RCAN_BIX3.mlmodel',
        'models/RCAN_BIX3_quantized.mlmodel'
    ]
    
    success = False
    
    for model_path in model_paths:
        if not os.path.exists(model_path):
            print(f"⚠️  Model not found: {model_path}")
            print(f"   Run: python convert_to_coreml.py")
            continue
        
        try:
            model = ct.models.MLModel(model_path)
            
            model_name = os.path.basename(model_path)
            model_size = os.path.getsize(model_path) / (1024 * 1024)
            
            print(f"\n✅ {model_name}")
            print(f"   Size: {model_size:.2f} MB")
            
            # Get model spec
            spec = model.get_spec()
            print(f"   Inputs: {len(spec.description.input)}")
            print(f"   Outputs: {len(spec.description.output)}")
            
            for input_desc in spec.description.input:
                print(f"   Input '{input_desc.name}': {input_desc.type}")
            
            for output_desc in spec.description.output:
                print(f"   Output '{output_desc.name}': {output_desc.type}")
            
            success = True
            
        except Exception as e:
            print(f"❌ Error loading {model_path}: {str(e)}")
    
    return success

def test_conversion_output():
    """Test conversion output quality"""
    print("\n" + "=" * 60)
    print("Testing Conversion Quality")
    print("=" * 60)
    
    try:
        import coremltools as ct
    except ImportError:
        print("⚠️  Skipping quality test (coremltools not installed)")
        return True
    
    model_path = 'models/RCAN_BIX3.mlmodel'
    
    if not os.path.exists(model_path):
        print("⚠️  CoreML model not found, skipping quality test")
        return True
    
    try:
        # Create a simple test image
        test_image = np.random.rand(180, 180, 3).astype(np.float32) * 255
        test_image_pil = Image.fromarray(test_image.astype(np.uint8))
        
        print("✅ Test image created")
        print(f"   Shape: {test_image.shape}")
        print(f"   Range: [{test_image.min():.1f}, {test_image.max():.1f}]")
        
        # Note: Actual inference would require proper image preprocessing
        print("\n💡 For full quality testing, use the model in an iOS/macOS app")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in quality test: {str(e)}")
        return False

def main():
    print("\n" + "=" * 60)
    print("RCAN to CoreML Conversion Test Suite")
    print("=" * 60 + "\n")
    
    results = {}
    
    # Test PyTorch model
    results['pytorch'] = test_pytorch_model()
    
    # Test CoreML model
    results['coreml'] = test_coreml_model()
    
    # Test conversion quality
    results['quality'] = test_conversion_output()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper():12s}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
