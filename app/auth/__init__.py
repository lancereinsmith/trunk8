"""
Authentication module for the Trunk8 application.

This package provides authentication functionality including login/logout
routes and authentication decorators for protected routes.
"""

from .routes import auth_bp

__all__ = ["auth_bp"]
