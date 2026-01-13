# GitHub Workflow Fixes

## Issues Found and Fixed

### Issue 1: Wrong Requirements File ✅ FIXED

**Problem:**
Workflow was using old `requirements.txt` (PyTorch 0.4.1 from 2018) instead of `requirements_coreml.txt`.

**Error:**
```
ModuleNotFoundError: No module named 'skbuild'
ERROR: Failed to build 'cmake' when getting requirements to build wheel
```

**Fix:**
Changed `.github/workflows/convert_to_coreml.yml`:
```yaml
# Before
pip install -r requirements.txt

# After  
pip install -r requirements_coreml.txt
```

---

### Issue 2: Models Extracted to Subdirectory ✅ FIXED

**Problem:**
The downloaded zip file `models_ECCV2018RCAN.zip` contains a subdirectory structure:
```
models_ECCV2018RCAN.zip
└── models_ECCV2018RCAN/
    ├── RCAN_BIX2.pt
    ├── RCAN_BIX3.pt
    ├── RCAN_BIX4.pt
    ├── RCAN_BIX8.pt
    └── RCAN_BDX3.pt
```

Models were extracted to `models/models_ECCV2018RCAN/` but workflow expected them at `models/`.

**Error:**
```
Error: RCAN_BIX3.pt not found!
drwxr-xr-x   7 runner  staff  224 Jan 13 10:38 models_ECCV2018RCAN
```

**Fix Applied:**

1. **Updated `download_model.py`:**
   - Extract zip to temporary directory
   - Recursively find all `.pt` files
   - Move them directly to `models/` directory
   - Clean up temporary directory

2. **Updated `.github/workflows/convert_to_coreml.yml`:**
   - Added fallback to move models from subdirectory if needed
   - Better error reporting with `find` command
   - Display downloaded models after extraction

**Code Changes:**

`download_model.py`:
```python
# Extract to temporary location first
temp_extract_dir = os.path.join(output_dir, 'temp_extract')
zip_ref.extractall(temp_extract_dir)

# Find all .pt files (they might be in subdirectories)
extracted_models = glob.glob(os.path.join(temp_extract_dir, '**', '*.pt'), recursive=True)

# Move .pt files to output_dir root
for model_path in extracted_models:
    model_name = os.path.basename(model_path)
    dest_path = os.path.join(output_dir, model_name)
    shutil.move(model_path, dest_path)
    print(f"  Moved: {model_name}")

# Clean up
shutil.rmtree(temp_extract_dir)
```

`.github/workflows/convert_to_coreml.yml`:
```bash
# Check if models were extracted to subdirectory (fallback)
if [ -d "models/models_ECCV2018RCAN" ]; then
  echo "Moving models from subdirectory..."
  mv models/models_ECCV2018RCAN/*.pt models/ || true
  rmdir models/models_ECCV2018RCAN || true
fi

# Better verification
if [ ! -f "models/RCAN_BIX${SCALE}.pt" ]; then
  echo "Error: RCAN_BIX${SCALE}.pt not found!"
  echo "Looking for .pt files recursively:"
  find models/ -name "*.pt" -type f
  exit 1
fi

# Show what was downloaded
ls -lh models/*.pt
```

---

## Testing

### Local Test
```bash
# Test download script
python download_model.py --output_dir models

# Or use test script
chmod +x test_download.sh
./test_download.sh
```

### GitHub Actions Test
```bash
# Commit and push
git add .
git commit -m "Fix model download and dependencies in workflow"
git push origin main

# Run workflow manually
# Go to Actions tab → "Convert RCAN to CoreML" → Run workflow
```

---

## Expected Workflow Output

After fixes, the workflow should:

1. ✅ Install dependencies from `requirements_coreml.txt`
2. ✅ Download models from Google Drive (290 MB)
3. ✅ Extract models to `models/` directory directly
4. ✅ Verify `RCAN_BIX3.pt` exists
5. ✅ Convert to CoreML
6. ✅ Create quantized version
7. ✅ Upload artifacts

**Sample Success Output:**
```
Downloading RCAN models...
100%|██████████| 290M/290M [00:05<00:00, 56.0MB/s]
✓ Download complete!
Extracting models...
  Moved: RCAN_BIX2.pt
  Moved: RCAN_BIX3.pt
  Moved: RCAN_BIX4.pt
  Moved: RCAN_BIX8.pt
  Moved: RCAN_BDX3.pt
✓ Extraction complete!

✅ Downloaded models:
  - RCAN_BDX3.pt (62.5 MB)
  - RCAN_BIX2.pt (62.5 MB)
  - RCAN_BIX3.pt (62.5 MB)
  - RCAN_BIX4.pt (62.5 MB)
  - RCAN_BIX8.pt (62.5 MB)

✓ Model downloaded successfully
-rw-r--r-- 1 runner staff 62M Jan 13 10:40 models/RCAN_BIX3.pt
```

---

## Files Modified

- ✅ `.github/workflows/convert_to_coreml.yml` - Use correct requirements, handle subdirectory
- ✅ `download_model.py` - Extract models to correct location
- ✅ `test_download.sh` - New test script (optional)

---

## Ready to Deploy! 🚀

The workflow should now work end-to-end. Push the changes and run it!
