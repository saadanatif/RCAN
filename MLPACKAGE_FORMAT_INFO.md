# CoreML Format: .mlpackage (ML Program)

## What Changed

The conversion now produces `.mlpackage` files instead of `.mlmodel` files.

## Why the Change?

CoreML has two formats:

### 1. Neural Network (.mlmodel) - Legacy Format
- ❌ Older format from iOS 11
- ❌ Limited operators
- ❌ Single file
- ❌ Less flexible

### 2. ML Program (.mlpackage) - Modern Format ⭐
- ✅ Modern format from iOS 15+
- ✅ Full operator support
- ✅ Better optimization
- ✅ Directory bundle (like .app)
- ✅ **Required by coremltools for TensorType outputs**

## What is .mlpackage?

`.mlpackage` is a **directory bundle** (like iOS `.app` files):

```
RCAN_BIX3.mlpackage/
├── Data/
│   └── com.apple.CoreML/
│       ├── model.mlmodel
│       └── weights/
│           └── weight.bin
└── Manifest.json
```

## How to Use

### In Xcode (iOS/macOS Development)

**Drag the entire `.mlpackage` folder into Xcode:**

```
1. Download and unzip from GitHub Actions artifacts
2. Drag RCAN_BIX3.mlpackage into your Xcode project
3. Use it like any CoreML model
```

Xcode treats `.mlpackage` the same as `.mlmodel` - no code changes needed!

```swift
// Works exactly the same
let model = try RCAN_BIX3()
```

### For Distribution

**Option 1: Zip the .mlpackage**
```bash
zip -r RCAN_BIX3.mlpackage.zip RCAN_BIX3.mlpackage
```

**Option 2: Create a .tar.gz**
```bash
tar -czf RCAN_BIX3.mlpackage.tar.gz RCAN_BIX3.mlpackage
```

The GitHub Actions workflow automatically zips `.mlpackage` files for download.

## Compatibility

| iOS Version | .mlmodel Support | .mlpackage Support |
|-------------|------------------|-------------------|
| iOS 11-14 | ✅ Yes | ❌ No |
| iOS 15+ | ✅ Yes | ✅ Yes |
| iOS 16+ | ✅ Yes | ✅ Yes (Recommended) |

**Minimum deployment target:** iOS 15 (set in conversion script)

## File Sizes

Both formats have similar sizes:

| Model | .mlmodel | .mlpackage | Notes |
|-------|----------|------------|-------|
| RCAN_BIX3 (full) | ~62 MB | ~62 MB | Same size |
| RCAN_BIX3 (quantized) | ~31 MB | ~31 MB | Same size |

The size is the same because weights are stored the same way.

## Converting Back to .mlmodel (If Needed)

If you need the old format for iOS 11-14 support:

```python
import coremltools as ct

# Load mlpackage
model = ct.models.MLModel('RCAN_BIX3.mlpackage')

# Convert to neuralnetwork (older format)
spec = model.get_spec()

# Re-convert with neuralnetwork backend
import torch
traced_model = torch.jit.load('model_traced.pt')

mlmodel = ct.convert(
    traced_model,
    inputs=[...],
    outputs=[...],
    convert_to='neuralnetwork',  # Force old format
    minimum_deployment_target=ct.target.iOS13
)

mlmodel.save('RCAN_BIX3.mlmodel')  # Now it's .mlmodel
```

**Note:** This may not work for models with TensorType outputs!

## GitHub Actions Changes

The workflow now:

1. ✅ Converts to `.mlpackage` format
2. ✅ Zips `.mlpackage` files for upload
3. ✅ Uploads `.zip` files as artifacts
4. ✅ Includes both full and quantized versions

**To use:**
1. Download artifact from GitHub Actions
2. Unzip to get `.mlpackage` folder
3. Drag into Xcode project
4. Use normally!

## Summary

**What you get:**
- `RCAN_BIX3.mlpackage.zip` (full precision, ~62 MB)
- `RCAN_BIX3_quantized.mlpackage.zip` (16-bit, ~31 MB)

**How to use:**
1. Download and unzip
2. Drag `.mlpackage` folder into Xcode
3. No code changes needed!

**Requirements:**
- iOS 15+ / macOS 12+
- Xcode 13+

**Benefits:**
- ✅ Modern, optimized format
- ✅ Better performance
- ✅ Required for TensorType outputs
- ✅ Same ease of use as .mlmodel

🎉 **Everything else stays the same in your Swift code!**
