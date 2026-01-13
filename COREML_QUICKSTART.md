# 🚀 Quick Start: RCAN to CoreML

Convert RCAN_BIX3.pt to CoreML in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements_coreml.txt
```

## Step 2: Download Model

```bash
python download_model.py
```

This downloads all RCAN models including **RCAN_BIX3.pt** (3x super-resolution).

## Step 3: Convert to CoreML

```bash
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --output models/RCAN_BIX3.mlmodel \
  --scale 3 \
  --quantize
```

**Done!** 🎉

Your CoreML models are in the `models/` directory:
- `RCAN_BIX3.mlmodel` (~62 MB)
- `RCAN_BIX3_quantized.mlmodel` (~31 MB)

## 🤖 Or Use GitHub Actions

1. Go to **Actions** tab
2. Run **"Convert RCAN to CoreML"** workflow
3. Select scale: **3**
4. Enable quantization: **✓**
5. Download from **Artifacts**

## 📱 Use in iOS App

```swift
import CoreML

let model = try RCAN_BIX3()
let output = try model.prediction(input_image: pixelBuffer)
```

See [CONVERSION_README.md](CONVERSION_README.md) for full documentation.

---

**Model Info:**
- Input: 180×180 RGB image
- Output: 540×540 RGB image (3x upscaled)
- Runs on: iPhone/iPad Neural Engine + GPU
