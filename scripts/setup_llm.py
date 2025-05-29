# scripts/setup_llm.py
#!/usr/bin/env python3
"""
Setup script for the local LLM used by NART.
This script helps download and configure the LLM model.
"""

import os
import sys
import argparse
import requests
import hashlib
import gzip
import tarfile
import zipfile
from pathlib import Path
from tqdm import tqdm


# Available models with direct links
AVAILABLE_MODELS = {
    "mistral-7b": {
        "name": "Mistral 7B Instruct v0.2 (4-bit Quantized)",
        "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "size": 4602393600,  # ~4.3GB
        "sha256": "121d5eb6b6586b8443aebf7d2a1ff5c5bd0a5831a331834467e742293692ad2f",
        "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    },
    "llama-7b": {
        "name": "Llama 2 7B Chat (4-bit Quantized)",
        "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "size": 3806408704,  # ~3.5GB
        "sha256": "a169e694674947a9cd591ce4b08d5ae0c85b5b3cf40c4c62fc5a12d6a8b79415",
        "filename": "llama-2-7b-chat.Q4_K_M.gguf"
    }
}


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Setup LLM model for NART")
    
    parser.add_argument("--model", choices=list(AVAILABLE_MODELS.keys()), default="mistral-7b",
                      help="Model to download")
    
    parser.add_argument("--output-dir", default=None,
                      help="Directory to save the model (default: ~/.nart/models)")
    
    parser.add_argument("--force", action="store_true",
                      help="Force download even if model already exists")
    
    parser.add_argument("--check", action="store_true",
                      help="Only check if model exists, don't download")
    
    parser.add_argument("--list", action="store_true",
                      help="List available models and exit")
    
    return parser.parse_args()


def list_models():
    """List available models with details"""
    print("\nAvailable Models:")
    print("-" * 80)
    for key, model in AVAILABLE_MODELS.items():
        size_gb = model["size"] / (1024 ** 3)
        print(f"{key}:")
        print(f"  - Name: {model['name']}")
        print(f"  - Size: {size_gb:.2f} GB")
        print(f"  - Filename: {model['filename']}")
        print()


def download_file(url, output_path, expected_size=None):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    
    # Check if expected size matches
    if expected_size and total_size > 0 and total_size != expected_size:
        print(f"Warning: Expected file size ({expected_size} bytes) differs from server reported size ({total_size} bytes)")
    
    # Use the larger of the two sizes for the progress bar
    if expected_size and total_size:
        total_size = max(expected_size, total_size)
    elif expected_size:
        total_size = expected_size
    
    # Create progress bar
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading")
    
    # Download the file
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))
    
    progress_bar.close()


def verify_file(file_path, expected_hash):
    """Verify file integrity using SHA-256 hash"""
    print("Verifying file integrity...")
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    actual_hash = sha256_hash.hexdigest()
    
    if actual_hash == expected_hash:
        print("File integrity verified.")
        return True
    else:
        print(f"Hash verification failed!")
        print(f"Expected: {expected_hash}")
        print(f"Actual:   {actual_hash}")
        return False


def update_config(model_path):
    """Update NART configuration with the model path"""
    config_path = os.path.expanduser("~/.nart/config.yaml")
    
    # Check if config file exists
    if not os.path.exists(config_path):
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Create default config
        with open(config_path, "w") as f:
             f.write(f"""llm:
  model_path: "{model_path}"
  context_size: 4096
  gpu_layers: 35
  threads: 4
""")
        print(f"Created config file at {config_path}")
    else:
        # Read existing config
        with open(config_path, "r") as f:
            config = f.read()
        
        # Check if llm section exists
        if "llm:" not in config:
            # Add llm section
            with open(config_path, "a") as f:
                f.write(f"""
llm:
  model_path: "{model_path}"
  context_size: 4096
  gpu_layers: 35
  threads: 4
""")
        else:
            # Update existing llm section
            lines = config.split("\n")
            new_lines = []
            in_llm_section = False
            model_path_updated = False
            
            for line in lines:
                if line.strip() == "llm:":
                    in_llm_section = True
                    new_lines.append(line)
                elif in_llm_section and line.strip().startswith("model_path:"):
                    new_lines.append(f'  model_path: "{model_path}"')
                    model_path_updated = True
                elif in_llm_section and not line.strip() and not model_path_updated:
                    new_lines.append(f'  model_path: "{model_path}"')
                    new_lines.append(line)
                    model_path_updated = True
                elif not line.strip():
                    in_llm_section = False
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            
            with open(config_path, "w") as f:
                f.write("\n".join(new_lines))
        
        print(f"Updated config file at {config_path}")


def main():
    """Main function"""
    args = parse_args()
    
    # List models and exit if requested
    if args.list:
        list_models()
        return 0
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.expanduser("~/.nart/models")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get model info
    model_info = AVAILABLE_MODELS.get(args.model)
    if not model_info:
        print(f"Error: Unknown model '{args.model}'")
        return 1
    
    model_path = os.path.join(output_dir, model_info["filename"])
    
    # Check if model already exists
    if os.path.exists(model_path) and not args.force:
        print(f"Model already exists at {model_path}")
        if args.check:
            print("Check mode: not verifying file integrity")
            return 0
        
        # Verify existing file
        if verify_file(model_path, model_info["sha256"]):
            print("Existing model file is valid")
        else:
            print("Existing model file is invalid or corrupted")
            if input("Do you want to redownload it? (y/n): ").lower() != 'y':
                return 1
            args.force = True
    
    # Don't download in check mode
    if args.check:
        print(f"Model does not exist at {model_path}")
        return 1
    
    # Download model
    if not os.path.exists(model_path) or args.force:
        print(f"Downloading {model_info['name']}...")
        print(f"Size: {model_info['size'] / (1024 ** 3):.2f} GB")
        print(f"URL: {model_info['url']}")
        print(f"Output: {model_path}")
        
        try:
            download_file(model_info["url"], model_path, model_info["size"])
        except Exception as e:
            print(f"Error downloading model: {e}")
            if os.path.exists(model_path):
                os.remove(model_path)
            return 1
        
        # Verify downloaded file
        if not verify_file(model_path, model_info["sha256"]):
            print("Downloaded file is corrupted")
            return 1
    
    # Update configuration
    try:
        update_config(model_path)
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return 1
    
    print("\nSetup complete!")
    print(f"Model path: {model_path}")
    print("You can now use the LLM features in NART")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())