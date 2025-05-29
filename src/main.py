import sys
import os
import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from .ui.main_window import MainWindow
from .core.database import initialize_database
from .config import load_config, save_config


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Network Assessment Reporting Tool")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--db", help="Path to database file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


def setup_app_environment():
    """Set up application environment"""
    # Set application information
    QCoreApplication.setApplicationName("NART")
    QCoreApplication.setApplicationVersion("1.0.0")
    QCoreApplication.setOrganizationName("RedBlue Labs")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"


def main():
    """Main entry point for the application"""
    # Parse command line arguments
    args = parse_args()
    
    # Set up application environment
    setup_app_environment()
    
    # Load configuration
    config_path = args.config or os.environ.get("NART_CONFIG", "config.yaml")
    config = load_config(config_path)
    
    # Update config with command line arguments
    if args.db:
        config["database"]["path"] = args.db
    if args.debug:
        config["debug"] = True
    
    # Initialize database
    db_path = config["database"]["path"]
    try:
        initialize_database(db_path)
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow(config)
    window.show()
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())