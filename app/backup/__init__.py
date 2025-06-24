"""
Backup and restore functionality for the Trunk8 application.

This module provides backup and restore capabilities for user data,
including links configuration and associated files.
"""

from flask import Blueprint

# Create backup blueprint
backup_bp = Blueprint("backup", __name__, url_prefix="/backup")

# Import routes to register them
from . import routes  # noqa: E402, F401
