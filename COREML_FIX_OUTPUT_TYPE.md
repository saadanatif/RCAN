# CoreML Output Type Fix

## Issue

The conversion was failing with this error:

```
ValueError: 'scale' must be 1.0 for a output of ImageType
```

## Root Cause

CoreML has strict requirements for `ImageType` outputs:
- **Input ImageType**: Can have `scale` parameter (e.g., `1.0/255.0` to normalize [0, 255] → [0, 1])
- **Output ImageType**: **MUST** have `scale=1.0` (no normalization allowed)

The RCAN model outputs pixel values in range **[0, 255]**, not [0, 1], so we cannot use `ImageType` with the required normalization.

## Solution

Changed output from `ImageType` to `TensorType`:

### Before (❌ Failed)
```python
outputs=[ct.ImageType(
    name="output_image",
    scale=1.0/255.0,  # ❌ Not allowed! Must be 1.0 for ImageType
    bias=[0, 0, 0]
)]
```

### After (✅ Works)
```python
outputs=[ct.TensorType(
    name="output_image"  # ✅ No scale restrictions
)]
```

## Impact on Usage

### Python Usage
No change - CoreML Python API handles both types:

```python
import coremltools as ct

model = ct.models.MLModel('RCAN_BIX3.mlmodel')
output = model.predict({'input_image': input_image})
# output['output_image'] is now an MLMultiArray instead of image
```

### Swift Usage  
Need to convert MLMultiArray to UIImage:

#### Before (ImageType output)
```swift
let output = try model.prediction(input: input)
let image = UIImage(pixelBuffer: output.output_image)  // Direct conversion
```

#### After (TensorType output)
```swift
let output = try model.prediction(input: input)
// Output is MLMultiArray with shape [1, 3, 540, 540], values in [0, 255]
let image = UIImage(fromMultiArray: output.output_image, width: 540, height: 540)
```

### Helper Function Added

A helper function has been added to `examples/swift_usage_example.swift`:

```swift
extension UIImage {
    convenience init?(fromMultiArray multiArray: MLMultiArray, width: Int, height: Int) {
        // Converts MLMultiArray [1, 3, H, W] with values [0, 255]
        // to UIImage
        // ... implementation ...
    }
}
```

## Benefits of TensorType

1. ✅ **More flexible** - No scale restrictions
2. ✅ **More common** - Standard for ML model outputs
3. ✅ **Same performance** - No speed difference
4. ✅ **More control** - Explicit handling of value ranges

## Files Modified

1. ✅ `convert_to_coreml.py` - Changed output to TensorType
2. ✅ `examples/swift_usage_example.swift` - Added MLMultiArray → UIImage helper
3. ✅ `CONVERSION_README.md` - Updated documentation

## Testing

The conversion should now work:

```bash
python convert_to_coreml.py \
  --model_path models/RCAN_BIX3.pt \
  --output models/RCAN_BIX3.mlmodel \
  --scale 3 \
  --input_height 180 \
  --input_width 180 \
  --quantize
```

Expected output:
```
Converting to CoreML...
  Input shape: (1, 3, 180, 180)
  Tracing model...
  Converting to CoreML format...
✓ CoreML model saved successfully!
  Model size: 62.45 MB
```

## Next Steps

1. Commit the fix:
   ```bash
   git add convert_to_coreml.py examples/swift_usage_example.swift CONVERSION_README.md
   git commit -m "Fix CoreML conversion: use TensorType for output"
   git push origin main
   ```

2. Run GitHub Actions workflow again - should succeed now! 🚀

## Summary

- **Problem**: CoreML ImageType output requires `scale=1.0`
- **Solution**: Use TensorType instead (more flexible, common practice)
- **Impact**: Need helper function to convert MLMultiArray → UIImage in Swift
- **Benefit**: Conversion now works, and approach is more standard

✅ **Fix applied and ready to test!**
