"""
Debug script for inspecting registered Flask routes.

This script creates the Flask application and prints all registered routes
with their endpoints and allowed HTTP methods for debugging purposes.

Usage:
    python debug/debug_routes.py
    or
    cd debug && python debug_routes.py
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

from app import create_app


def main() -> None:
    """
    Main debug function to display all registered Flask routes.

    Creates the Flask app and iterates through all registered URL rules,
    printing the route pattern, endpoint name, and allowed HTTP methods.
    """
    app: Flask = create_app()
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.endpoint} ({rule.methods})")


if __name__ == "__main__":
    main()
