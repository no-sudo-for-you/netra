# scripts/install.py
#!/usr/bin/env python3
"""
Installation script for the Network Assessment Reporting Tool (NART).
This script sets up the required environment and initial configuration.
"""

import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Install Network Assessment Reporting Tool (NART)")
    
    parser.add_argument("--install-dir", default=None,
                      help="Directory to install NART (default: ~/.nart)")
    
    parser.add_argument("--skip-dependencies", action="store_true",
                      help="Skip installing Python dependencies")
    
    parser.add_argument("--skip-model", action="store_true",
                      help="Skip downloading LLM model")
    
    parser.add_argument("--model", default="mistral-7b",
                      help="LLM model to download (default: mistral-7b)")
    
    parser.add_argument("--force", action="store_true",
                      help="Force installation even if already installed")
    
    return parser.parse_args()


def check_python_version():
    """Check if Python version is compatible"""
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 9):
        print("Error: Python 3.9 or higher is required")
        print(f"Current version: {platform.python_version()}")
        return False
    return True


def install_dependencies():
    """Install required Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def setup_directory_structure(install_dir):
    """Set up the directory structure for NART"""
    print(f"\nSetting up directory structure in {install_dir}...")
    try:
        # Create main directories
        os.makedirs(os.path.join(install_dir, "models"), exist_ok=True)
        os.makedirs(os.path.join(install_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(install_dir, "templates"), exist_ok=True)
        os.makedirs(os.path.join(install_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(install_dir, "backups"), exist_ok=True)
        
        print("Directory structure created successfully")
        return True
    except Exception as e:
        print(f"Error setting up directory structure: {e}")
        return False


def create_default_config(install_dir):
    """Create default configuration file"""
    config_path = os.path.join(install_dir, "config.yaml")
    
    # Check if config already exists
    if os.path.exists(config_path) and not args.force:
        print(f"Configuration file already exists at {config_path}")
        return True
    
    print(f"\nCreating default configuration in {config_path}...")
    try:
        with open(config_path, "w") as f:
            f.write("""# NART Configuration File

# Database settings
database:
  path: "{data_dir}/nart.db"
  backup_dir: "{backup_dir}"

# LLM settings
llm:
  model_path: "{model_dir}"
  context_size: 4096
  gpu_layers: 35
  threads: 4

# CVE database settings
cve:
  database_path: "{data_dir}/cve.db"
  update_interval_days: 7

# Reporting settings
reporting:
  templates_dir: "{templates_dir}"
  output_dir: "{output_dir}"
  company_name: "Your Company"
  company_logo: ""

# UI settings
ui:
  theme: "system"  # light, dark, system
  font_size: 12
  dashboard_refresh_interval: 300  # seconds

# Debug settings
debug: false
""".format(
                data_dir=os.path.join(install_dir, "data"),
                backup_dir=os.path.join(install_dir, "backups"),
                model_dir="",  # Will be updated by model download script
                templates_dir=os.path.join(install_dir, "templates"),
                output_dir=os.path.expanduser("~/Documents/NART Reports")
            ))
        
        print("Default configuration created successfully")
        return True
    except Exception as e:
        print(f"Error creating default configuration: {e}")
        return False


def download_model(install_dir, model_name, force=False):
    """Download the specified LLM model"""
    print(f"\nDownloading LLM model '{model_name}'...")
    try:
        # Use the setup_llm.py script to download the model
        cmd = [
            sys.executable, 
            "scripts/setup_llm.py", 
            "--model", model_name, 
            "--output-dir", os.path.join(install_dir, "models")
        ]
        
        if force:
            cmd.append("--force")
        
        subprocess.check_call(cmd)
        print("Model downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading model: {e}")
        return False


def initialize_database(install_dir):
    """Initialize the SQLite database"""
    db_path = os.path.join(install_dir, "data", "nart.db")
    
    # Check if database already exists
    if os.path.exists(db_path) and not args.force:
        print(f"Database already exists at {db_path}")
        return True
    
    print(f"\nInitializing database at {db_path}...")
    try:
        # Run the database initialization script
        subprocess.check_call([
            sys.executable, 
            "scripts/setup_database.py", 
            "--db-path", db_path
        ])
        print("Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        return False


def create_desktop_shortcut():
    """Create desktop shortcut for NART (platform-specific)"""
    if platform.system() == "Windows":
        print("\nCreating desktop shortcut...")
        try:
            # Windows shortcut creation
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "NART.lnk")
            target = sys.executable
            wDir = os.path.dirname(os.path.abspath(__file__))
            icon = os.path.join(wDir, "src", "ui", "assets", "nart.ico")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon if os.path.exists(icon) else target
            shortcut.Arguments = "-m nart"
            shortcut.save()
            
            print("Desktop shortcut created successfully")
            return True
        except Exception as e:
            print(f"Error creating desktop shortcut: {e}")
            print("You can still run NART using 'python -m nart' command")
            return False
    else:
        # For Linux/macOS, just print instructions
        print("\nTo create a launcher on Linux or macOS:")
        print(f"1. Create a shell script that runs: {sys.executable} -m nart")
        print("2. Make it executable: chmod +x nart.sh")
        print("3. Copy it to your applications directory or desktop")
        return True


def print_final_instructions(install_dir):
    """Print final instructions for the user"""
    print("\n" + "=" * 80)
    print("NART Installation Complete!")
    print("=" * 80)
    print(f"\nInstallation directory: {install_dir}")
    print("\nTo start NART, run:")
    print(f"  {sys.executable} -m nart")
    print("\nTo update the CVE database:")
    print(f"  {sys.executable} -m nart.cli cve --update")
    print("\nTo import scan files:")
    print(f"  {sys.executable} -m nart.cli import scan_file.xml")
    print("\nTo generate a report:")
    print(f"  {sys.executable} -m nart.cli report --output report.docx")
    print("\nConfiguration file:")
    print(f"  {os.path.join(install_dir, 'config.yaml')}")
    print("\nFor more information, see the documentation:")
    print("  https://github.com/redbluelabs/nart/docs")
    print("\n" + "=" * 80)


def main():
    """Main function"""
    args = parse_args()
    
    print("Network Assessment Reporting Tool (NART) - Installation")
    print("=" * 80)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Determine installation directory
    if args.install_dir:
        install_dir = args.install_dir
    else:
        install_dir = os.path.expanduser("~/.nart")
    
    # Check if already installed
    if os.path.exists(install_dir) and not args.force:
        print(f"NART appears to be already installed in {install_dir}")
        print("Use --force to reinstall or specify a different directory with --install-dir")
        return 1
    
    # Install dependencies
    if not args.skip_dependencies:
        if not install_dependencies():
            return 1
    
    # Set up directory structure
    if not setup_directory_structure(install_dir):
        return 1
    
    # Create default configuration
    if not create_default_config(install_dir):
        return 1
    
    # Initialize database
    if not initialize_database(install_dir):
        return 1
    
    # Download LLM model
    if not args.skip_model:
        if not download_model(install_dir, args.model, args.force):
            print("Warning: Failed to download LLM model.")
            print("You can download it later using scripts/setup_llm.py")
    
    # Create desktop shortcut
    create_desktop_shortcut()
    
    # Print final instructions
    print_final_instructions(install_dir)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())