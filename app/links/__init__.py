"""
Links module for the Trunk8 application.

This package provides link management functionality including routes for
creating, editing, deleting, and serving shortened links of various types
(file uploads, redirects, and markdown content).
"""

from .routes import links_bp

__all__ = ["links_bp"]
