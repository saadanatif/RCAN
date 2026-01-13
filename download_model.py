#!/usr/bin/env python3
"""
Download RCAN_BIX3.pt model from Google Drive
"""

import os
import sys
import requests
from pathlib import Path
import zipfile
import io

def download_file_from_google_drive(file_id, destination):
    """Download file from Google Drive"""
    URL = "https://docs.google.com/uc?export=download&confirm=1"
    
    session = requests.Session()
    
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    
    save_response_content(response, destination)

def get_confirm_token(response):
    """Get confirmation token for large files"""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    """Save response content to file"""
    CHUNK_SIZE = 32768
    
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

def download_and_extract_models(output_dir='models'):
    """Download and extract RCAN models"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Google Drive file ID for models_ECCV2018RCAN.zip
    # Note: This is extracted from the share link
    file_id = '1U0RmWkkacyw0HNC7CBts2LcX1ewAulCn'
    
    zip_path = os.path.join(output_dir, 'models_ECCV2018RCAN.zip')
    
    print("Downloading RCAN models from Google Drive...")
    print("This may take a few minutes...")
    
    try:
        # Download using gdown (more reliable for Google Drive)
        import gdown
        url = f'https://drive.google.com/uc?id={file_id}'
        gdown.download(url, zip_path, quiet=False)
        
        print(f"\n✓ Download complete!")
        print(f"Extracting models...")
        
        # Extract zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        print(f"✓ Extraction complete!")
        
        # Clean up zip file
        os.remove(zip_path)
        
        # List extracted models
        model_files = [f for f in os.listdir(output_dir) if f.endswith('.pt')]
        print(f"\n✅ Downloaded models:")
        for model in sorted(model_files):
            model_path = os.path.join(output_dir, model)
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"  - {model} ({size_mb:.1f} MB)")
        
        return True
        
    except ImportError:
        print("\n❌ Error: 'gdown' package not found.")
        print("Please install it with: pip install gdown")
        print("\nOr manually download from:")
        print("  Google Drive: https://drive.google.com/file/d/1U0RmWkkacyw0HNC7CBts2LcX1ewAulCn/view?usp=sharing")
        print("  Dropbox: https://www.dropbox.com/s/qm9vc0p0w9i4s0n/models_ECCV2018RCAN.zip?dl=0")
        print("  BaiduYun: https://pan.baidu.com/s/1bkoJKmdOcvLhOFXHVkFlKA")
        print(f"\nExtract the zip file and place models in: {output_dir}/")
        return False
        
    except Exception as e:
        print(f"\n❌ Error downloading models: {str(e)}")
        print("\nPlease manually download from:")
        print("  Google Drive: https://drive.google.com/file/d/1U0RmWkkacyw0HNC7CBts2LcX1ewAulCn/view?usp=sharing")
        print("  Dropbox: https://www.dropbox.com/s/qm9vc0p0w9i4s0n/models_ECCV2018RCAN.zip?dl=0")
        print("  BaiduYun: https://pan.baidu.com/s/1bkoJKmdOcvLhOFXHVkFlKA")
        print(f"\nExtract the zip file and place models in: {output_dir}/")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download RCAN pre-trained models')
    parser.add_argument('--output_dir', type=str, default='models',
                        help='Output directory for models')
    
    args = parser.parse_args()
    
    success = download_and_extract_models(args.output_dir)
    
    if success:
        print(f"\n✅ All done! Models are ready in '{args.output_dir}/' directory.")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
