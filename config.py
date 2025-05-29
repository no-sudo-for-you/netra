import os
import yaml
from pathlib import Path


def get_default_config():
    """Get default configuration"""
    return {
        "database": {
            "path": os.path.expanduser("~/.nart/nart.db"),
            "backup_dir": os.path.expanduser("~/.nart/backups"),
        },
        "llm": {
            "model_path": os.path.expanduser("~/.nart/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
            "context_size": 4096,
            "gpu_layers": 35,
            "threads": 4,
        },
        "cve": {
            "database_path": os.path.expanduser("~/.nart/cve.db"),
            "update_interval_days": 7,
        },
        "reporting": {
            "templates_dir": os.path.expanduser("~/.nart/templates"),
            "output_dir": os.path.expanduser("~/Documents/NART Reports"),
            "company_name": "RedBlue Labs",
            "company_logo": "",
        },
        "ui": {
            "theme": "system",  # light, dark, system
            "font_size": 12,
            "dashboard_refresh_interval": 300,  # seconds
        },
        "debug": False,
    }


def load_config(config_path):
    """Load configuration from file"""
    # Get default configuration
    config = get_default_config()
    
    # Load configuration from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                loaded_config = yaml.safe_load(f)
                if loaded_config:
                    # Recursively update default config with loaded config
                    _update_config(config, loaded_config)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    # Create any missing directories
    _ensure_config_dirs(config)
    
    return config


def save_config(config, config_path):
    """Save configuration to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Save configuration
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def _update_config(config, update):
    """Recursively update configuration"""
    for key, value in update.items():
        if key in config and isinstance(config[key], dict) and isinstance(value, dict):
            _update_config(config[key], value)
        else:
            config[key] = value


def _ensure_config_dirs(config):
    """Ensure all required directories exist"""
    # Database directory
    os.makedirs(os.path.dirname(config["database"]["path"]), exist_ok=True)
    os.makedirs(config["database"]["backup_dir"], exist_ok=True)
    
    # Model directory
    os.makedirs(os.path.dirname(config["llm"]["model_path"]), exist_ok=True)
    
    # CVE database directory
    os.makedirs(os.path.dirname(config["cve"]["database_path"]), exist_ok=True)
    
    # Templates directory
    os.makedirs(config["reporting"]["templates_dir"], exist_ok=True)
    
    # Output directory
    os.makedirs(config["reporting"]["output_dir"], exist_ok=True)