#!/bin/bash
# Quick test script to verify model download works correctly

echo "Testing model download..."

# Clean up any existing models
rm -rf models/*.pt models/models_ECCV2018RCAN 2>/dev/null

# Run download
python download_model.py --output_dir models

# Check if models are in the right place
echo ""
echo "Checking model locations..."
if [ -f "models/RCAN_BIX3.pt" ]; then
    echo "✅ RCAN_BIX3.pt found in models/"
    ls -lh models/RCAN_BIX3.pt
else
    echo "❌ RCAN_BIX3.pt NOT found in models/"
    echo "Contents of models/:"
    ls -la models/
    exit 1
fi

echo ""
echo "✅ Download test passed!"
