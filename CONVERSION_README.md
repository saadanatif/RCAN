# RCAN to CoreML Conversion

This guide explains how to convert RCAN (Residual Channel Attention Networks) PyTorch models to CoreML format for use on Apple platforms (iOS, macOS, iPadOS).

## 🎯 Overview

**RCAN** is a state-of-the-art deep learning model for image super-resolution that uses channel attention mechanisms to achieve high-quality upscaling.

- **Paper**: [Image Super-Resolution Using Very Deep Residual Channel Attention Networks](https://arxiv.org/abs/1807.02758) (ECCV 2018)
- **Authors**: Yulun Zhang, Kunpeng Li, Kai Li, Lichen Wang, Bineng Zhong, Yun Fu
- **Available Scales**: 2x, 3x, 4x, 8x super-resolution

## 📋 Prerequisites

### System Requirements
- **macOS** (required for CoreML Tools to work properly)
- Python 3.8 - 3.10
- 8GB+ RAM
- ~500MB free disk space for models

### Software Requirements
```bash
# Install Python dependencies
pip install -r requirements_coreml.txt
```

## 🚀 Quick Start

### Method 1: Automated Conversion (GitHub Actions)

The easiest way to convert models is using the GitHub Actions workflow:

1. Fork this repository
2. Go to **Actions** tab
3. Select **"Convert RCAN to CoreML"** workflow
4. Click **"Run workflow"**
5. Choose your parameters:
   - Scale: 2, 3, 4, or 8
   - Quantize: Enable 16-bit quantization (recommended)
   - Input Size: Input image dimensions (default: 180)
6. Download the converted models from **Artifacts**

### Method 2: Manual Conversion (Local)

#### Step 1: Download Pre-trained Models

```bash
# Download all RCAN models
python download_model.py --output_dir models
```

This will download models from Google Drive:
- `RCAN_BIX2.pt` (2x scale)
- `RCAN_BIX3.pt` (3x scale) ⭐
- `RCAN_BIX4.pt` (4x scale)
- `RCAN_BIX8.pt` (8x scale)
- `RCAN_BDX3.pt` (3x scale, BD degradation)

**Manual Download**: If automatic download fails, manually download from:
- [Google Drive](https://drive.google.com/file/d/1U0RmWkkacyw0HNC7CBts2LcX1ewAulCn/view?usp=sharing)
- [Dropbox](https://www.dropbox.com/s/qm9vc0p0w9i4s0n/models_ECCV2018RCAN.zip?dl=0)
- [BaiduYun](https://pan.baidu.com/s/1bkoJKmdOcvLhOFXHVkFlKA)

#### Step 2: Convert to CoreML

```bash
# Convert RCAN_BIX3 (3x scale) to CoreML
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --output models/RCAN_BIX3.mlpackage \
  --scale 3 \
  --input_height 180 \
  --input_width 180 \
  --quantize
```

**Note:** Output is `.mlpackage` (ML Program format, iOS 15+). This is a directory bundle, not a single file.

**Parameters**:
- `--model_path`: Path to PyTorch model (.pt file)
- `--output`: Output path for CoreML model
- `--scale`: Super-resolution scale factor (2, 3, 4, or 8)
- `--input_height`: Input image height (must be divisible by scale)
- `--input_width`: Input image width (must be divisible by scale)
- `--quantize`: Enable 16-bit quantization (reduces size by ~50%)

#### Step 3: Verify Conversion

```python
import coremltools as ct

# Load and inspect the model
model = ct.models.MLModel('models/RCAN_BIX3.mlpackage')
print(model.get_spec())
```

## 📊 Model Specifications

### RCAN_BIX3 (3x Super-Resolution)

| Parameter | Value |
|-----------|-------|
| Scale Factor | 3x |
| Format | ML Program (.mlpackage) |
| iOS Version | iOS 15+ |
| Input Size | 180x180 (configurable) |
| Output Size | 540x540 |
| Residual Groups | 10 |
| Residual Blocks per Group | 20 |
| Feature Maps | 64 |
| Parameters | ~15.6M |
| Full Precision Size | ~62 MB |
| Quantized (16-bit) Size | ~31 MB |

### Input/Output Format

**Input**:
- **Type**: RGB Image (ImageType)
- **Shape**: (1, 3, H, W) where H and W are divisible by scale
- **Range**: [0, 255] (automatically normalized to [0, 1] by CoreML)
- **Color Layout**: RGB

**Output**:
- **Type**: Tensor (MLMultiArray / TensorType)
- **Shape**: (1, 3, H×scale, W×scale)
- **Range**: [0, 255]
- **Data Type**: Float32
- **Note**: Output is a tensor, not an image. Use provided Swift helper to convert to UIImage.

## 🔧 Advanced Usage

### Custom Input Sizes

Different input sizes for different use cases:

```bash
# Mobile device (smaller, faster)
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --output models/RCAN_BIX3_mobile.mlmodel \
  --scale 3 \
  --input_height 120 \
  --input_width 120 \
  --quantize

# High quality (larger, slower)
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --output models/RCAN_BIX3_hq.mlmodel \
  --scale 3 \
  --input_height 240 \
  --input_width 240 \
  --quantize
```

### Convert Other Scales

```bash
# 2x scale
python convert_to_coreml.py --model_path models/RCAN_BIX2.pt --scale 2 --input_height 180 --input_width 180

# 4x scale
python convert_to_coreml.py --model_path models/RCAN_BIX4.pt --scale 4 --input_height 180 --input_width 180

# 8x scale
python convert_to_coreml.py --model_path models/RCAN_BIX8.pt --scale 8 --input_height 160 --input_width 160
```

## 🍎 Using CoreML Models on Apple Platforms

### Swift Example

```swift
import CoreML
import Vision

func superResolve(image: UIImage) throws -> UIImage? {
    // Load the model
    let config = MLModelConfiguration()
    config.computeUnits = .all  // Use Neural Engine + GPU
    let model = try RCAN_BIX3(configuration: config)
    
    // Prepare input
    guard let pixelBuffer = image.toPixelBuffer(width: 180, height: 180) else {
        return nil
    }
    
    // Run inference
    let input = RCAN_BIX3Input(input_image: pixelBuffer)
    let output = try model.prediction(input: input)
    
    // Convert output tensor to UIImage
    // Output is MLMultiArray [1, 3, 540, 540], values in [0, 255]
    return UIImage(fromMultiArray: output.output_image, width: 540, height: 540)
}
```

### Performance Tips

1. **Use Neural Engine**: Set `computeUnits = .all` to use Apple's Neural Engine
2. **Batch Processing**: Process multiple tiles for large images
3. **Input Size**: Smaller inputs = faster inference
4. **Quantization**: 16-bit models are almost as accurate but 50% smaller

## 📝 GitHub Actions Workflow

The repository includes a complete CI/CD workflow that:

✅ Automatically downloads RCAN models  
✅ Converts to CoreML format  
✅ Creates both full and quantized versions  
✅ Uploads models as artifacts  
✅ Creates releases on tags  

### Trigger Workflow

```bash
# Push to main branch
git push origin main

# Or manually via GitHub Actions UI
```

### Workflow Inputs

When running manually:
- **scale**: Choose 2, 3, 4, or 8
- **quantize**: Enable/disable 16-bit quantization
- **input_size**: Input image dimension

## 🐛 Troubleshooting

### Issue: `gdown` fails to download

**Solution**: Manually download from Google Drive/Dropbox and place in `models/` folder

### Issue: CoreML conversion fails on Linux/Windows

**Solution**: CoreML Tools requires macOS for full functionality. Use GitHub Actions or a Mac.

### Issue: Input dimensions error

**Solution**: Ensure input height and width are divisible by the scale factor.

```bash
# ✅ Valid for scale=3
--input_height 180 --input_width 180  # 180 ÷ 3 = 60

# ❌ Invalid for scale=3
--input_height 100 --input_width 100  # 100 ÷ 3 = 33.33...
```

### Issue: Model too large for iOS app

**Solution**: Use quantization and smaller input sizes

```bash
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --scale 3 \
  --input_height 120 \
  --input_width 120 \
  --quantize  # This flag is important!
```

## 📚 Additional Resources

- [Original RCAN Paper](https://arxiv.org/abs/1807.02758)
- [RCAN GitHub Repository](https://github.com/yulunzhang/RCAN)
- [Apple CoreML Documentation](https://developer.apple.com/documentation/coreml)
- [CoreML Tools Documentation](https://coremltools.readme.io/)

## 📄 License

The RCAN model is released under the original license from the authors. This conversion code is provided as-is for research and educational purposes.

## 🙏 Acknowledgements

- Original RCAN authors: Yulun Zhang et al.
- Built on [EDSR (PyTorch)](https://github.com/thstkdgus35/EDSR-PyTorch)

## 📧 Support

If you encounter issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [GitHub Issues](../../issues)
3. Create a new issue with:
   - Your Python version
   - Your macOS version (if applicable)
   - Complete error message
   - Steps to reproduce

---

**Happy Super-Resolving! 🚀**
