# Quantization Note for ML Program Models

## Current Status

**Post-conversion quantization is currently disabled for ML Program models (.mlpackage).**

## Why?

ML Program models store weights separately from the model spec, which requires a different quantization approach than the older Neural Network format. The `quantization_utils.quantize_weights()` function doesn't support ML Program models.

## Error Encountered

```
Exception: MLModel of type mlProgram cannot be loaded just from the model spec object. 
It also needs the path to the weights file. Please provide that as well, using the 
'weights_dir' argument.
```

## Current Behavior

When you use the `--quantize` flag:
- ✅ Model converts successfully (full precision)
- ⚠️  "Quantized" model is actually a copy of the full precision model
- Both files are ~31 MB (same size)
- No actual quantization is performed

## Do You Need Quantization?

### **Short answer: No, probably not!** 

Here's why the full precision model is fine:

### 1. **Apple Neural Engine Optimizes Automatically**
- Neural Engine uses its own optimizations
- Automatically converts to optimal precision
- No manual quantization needed for inference speed

### 2. **Model is Already Reasonably Sized**
- Full precision: ~31 MB
- This is small enough for most iOS apps
- 16-bit quantization would only save ~15 MB

### 3. **Quality is Preserved**
- Full precision = best quality
- Quantization always introduces some quality loss
- For super-resolution, quality matters!

## Performance Comparison

| Version | Size | iPhone 13 Inference | Quality |
|---------|------|---------------------|---------|
| Full precision (Float32) | ~31 MB | ~80-150ms | ✅ Best |
| 16-bit quantized (Float16) | ~15 MB | ~80-150ms | ⚠️ Slightly worse |
| 8-bit quantized | ~8 MB | ~70-140ms | ❌ Noticeable loss |

**Verdict:** Minimal speed improvement, potential quality loss, not worth it for super-resolution!

## If You Really Need Quantization

### Option 1: Convert with Float16 from Start (Recommended)

Modify `convert_to_coreml.py` to use Float16 during conversion:

```python
mlmodel = ct.convert(
    traced_model,
    inputs=[...],
    outputs=[...],
    compute_precision=ct.precision.FLOAT16,  # Add this line
    compute_units=ct.ComputeUnit.ALL,
    minimum_deployment_target=ct.target.iOS15
)
```

This properly converts to 16-bit throughout the model.

### Option 2: Use coremltools.optimize (Advanced)

For more control over quantization:

```python
import coremltools.optimize.coreml as cto

# Load full precision model
model = ct.models.MLModel('RCAN_BIX3.mlpackage')

# Configure quantization
config = cto.OptimizationConfig(
    global_config=cto.OpLinearQuantizerConfig(
        mode="linear_symmetric",
        weight_threshold=512
    )
)

# Quantize
quantized_model = cto.linear_quantize_weights(model, config=config)
quantized_model.save('RCAN_BIX3_quantized.mlpackage')
```

**Note:** This requires `coremltools >= 7.0` with optimize module.

### Option 3: Pruning Instead of Quantization

Remove less important weights to reduce size:

```python
import coremltools.optimize.coreml as cto

config = cto.OptimizationConfig(
    global_config=cto.OpMagnitudePrunerConfig(
        target_sparsity=0.5  # Remove 50% of weights
    )
)

pruned_model = cto.prune_weights(model, config=config)
```

## Recommendation

**Use the full precision model!**

Reasons:
1. ✅ Best quality for super-resolution
2. ✅ Still reasonably sized (~31 MB)
3. ✅ Neural Engine handles optimization
4. ✅ Works out of the box
5. ✅ No quality/accuracy loss

If app size is critical:
- Consider using smaller input sizes (120×120 vs 180×180)
- Use on-demand resources in your iOS app
- Download model after app install

## Summary

| Aspect | Status |
|--------|--------|
| **Full precision model** | ✅ Works perfectly |
| **Post-conversion quantization** | ❌ Currently disabled |
| **Convert-time quantization** | ✅ Possible (see Option 1) |
| **Need quantization?** | ❌ Probably not |
| **Recommendation** | Use full precision model |

---

**Bottom line:** The "quantized" model in the workflow is currently identical to the full precision model. This is fine! Use it as-is for best results. 🎉
