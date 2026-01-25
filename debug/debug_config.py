"""
Debug script for inspecting configuration loading and asset file paths.

This script initializes the Flask application and examines the configuration
loader to verify that TOML files are being read correctly and that asset
paths are properly resolved.

Usage:
    python debug/debug_config.py
    or
    cd debug && python debug_config.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import the app module
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Change working directory to project root to ensure config files are found there
os.chdir(parent_dir)

from flask import Flask

from app import create_app, get_config_loader


def main() -> None:
    """
    Main debug function to inspect configuration and file paths.

    Creates the Flask app, examines the links configuration, and validates
    file existence for debugging purposes.
    """
    app: Flask = create_app()
    with app.app_context():
        config_loader = get_config_loader(app)
        print("Links config:")
        print(config_loader.links_config)

        print("\nChecking ex_text link:")
        links = config_loader.links_config.get("links", {})
        ex_text = links.get("ex_text")
        print(f"ex_text link data: {ex_text}")

        if ex_text:
            path = ex_text.get("path")
            asset_folder = app.config["ASSET_FOLDER"]
            full_path = os.path.join(asset_folder, path)
            print(f"File path: {full_path}")
            print(f"File exists: {os.path.exists(full_path)}")


if __name__ == "__main__":
    main()
