#!/usr/bin/env python3
"""
Main entry point for the Trunk8 link shortener application.

This file replaces the original app.py and uses the application factory pattern
for better organization and testing capabilities. It initializes the Flask
application and starts the development server.

Usage:
    python run.py

The server will start on host 0.0.0.0, port from TRUNK8_PORT environment variable (default: 5001) in debug mode.
"""

import os

from dotenv import load_dotenv
from flask import Flask

from app import create_app
from app.utils.logging_config import setup_logging

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize logging
logger = setup_logging()

# Create the Flask application
app: Flask = create_app()

if __name__ == "__main__":
    # Get port from environment variable, default to 5001
    port = int(os.environ.get("TRUNK8_PORT", 5001))

    logger.info(f"Starting Trunk8 development server on host 0.0.0.0, port {port}")
    app.run(
        debug=True, host="0.0.0.0", port=port
    )  # Run on all interfaces, convenient for home server
