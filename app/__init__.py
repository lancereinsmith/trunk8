"""
Flask application factory for the Trunk8 application.

This module provides the create_app function to initialize and configure
the Flask application with all necessary blueprints, configuration,
and multi-user support.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Optional, cast

from flask import Flask, g, redirect, session
from flask.templating import render_template
from flask.wrappers import Response

from .utils.config_loader import ConfigLoader
from .utils.logging_config import get_logger, setup_logging
from .utils.user_manager import UserManager


class Trunk8Flask(Flask):
    """Flask app with config_loader and user_manager."""

    config_loader: ConfigLoader
    user_manager: UserManager


def get_config_loader(app: Flask) -> ConfigLoader:
    """Return the config_loader from a Flask app (Trunk8Flask)."""
    return cast(ConfigLoader, getattr(app, "config_loader"))  # noqa: B009


def get_user_manager(app: Flask) -> UserManager:
    """Return the user_manager from a Flask app (Trunk8Flask)."""
    return cast(UserManager, getattr(app, "user_manager"))  # noqa: B009


def _redirect(location: str, code: int = 302) -> Response:
    """Redirect to location; returns Response for type consistency with flask/werkzeug."""
    return cast(Response, redirect(location, code=code))


def create_app(config_name: str | None = None) -> Trunk8Flask:
    """
    Create Flask application instance with configuration.

    Args:
        config_name: Configuration name (not used currently, reserved for future).

    Returns:
        Trunk8Flask: Configured Flask application instance.
    """
    app = Trunk8Flask(__name__)

    # Initialize logging
    logger = setup_logging()
    logger.info("Starting Trunk8 application initialization")

    # Initialize configuration loader and user manager
    config_loader = ConfigLoader()
    user_manager = UserManager()

    logger.info("Configuration loader and user manager initialized")

    # Load configurations
    config_loader.load_all_configs()
    logger.info("Configuration files loaded")

    # Configure Flask app
    _configure_app(app, config_loader.app_config)
    logger.info("Flask application configured")

    # Make config loader and user manager available to the app
    app.config_loader = config_loader
    app.user_manager = user_manager

    # Register blueprints
    _register_blueprints(app)
    logger.info("Blueprints registered")

    # Set up request context processors
    _setup_context_processors(app)
    logger.info("Context processors configured")

    # Set up before request handlers
    _setup_before_request_handlers(app)
    logger.info("Before request handlers configured")

    # Set up Jinja2 filters
    _setup_jinja_filters(app)
    logger.info("Jinja2 filters configured")

    logger.info("Trunk8 application initialization completed successfully")
    return app


def _configure_app(app: Flask, app_config: dict[str, Any]) -> None:
    """
    Configure Flask app with settings from TOML config.

    Args:
        app: Flask application instance to configure.
        app_config: Dictionary containing application configuration data.
    """
    # Set secret key for sessions
    app.secret_key = os.environ.get("TRUNK8_SECRET_KEY", "your-secret-key-change-in-production")

    # Load app configuration
    app.config["APP_CONFIG_FILE"] = "config/config.toml"

    # Set session lifetime from config
    session_config = app_config.get("session", {})
    permanent_lifetime_days = session_config.get("permanent_lifetime_days", 30)
    app.permanent_session_lifetime = timedelta(days=permanent_lifetime_days)

    # Set maximum content length for file uploads
    max_file_size_mb = app_config.get("app", {}).get("max_file_size_mb", 100)
    app.config["MAX_CONTENT_LENGTH"] = max_file_size_mb * 1024 * 1024

    # NOTE: All assets are stored in users/{username}/assets/ directories


def _register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Args:
        app: Flask application instance.
    """
    # Import blueprints
    from .auth import auth_bp
    from .backup import backup_bp
    from .links import links_bp
    from .main import main_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(main_bp)


def _setup_context_processors(app: Flask) -> None:
    """
    Set up template context processors.

    Args:
        app: Flask application instance.
    """

    @app.context_processor
    def inject_user_context():
        """Inject user context into all templates."""
        from .auth.decorators import get_user_context

        return get_user_context()

    @app.context_processor
    def inject_theme_context():
        """Inject theme information into templates."""
        config_loader = getattr(app, "config_loader", None)
        if config_loader:
            themes_config = config_loader.themes_config

            return {
                "current_theme": config_loader.get_effective_theme(),
                "current_markdown_theme": config_loader.get_effective_markdown_theme(),
                "available_themes": themes_config.get("themes", {}),
            }
        return {}


def _setup_before_request_handlers(app: Flask) -> None:
    """
    Set up before request handlers.

    Args:
        app: Flask application instance.
    """

    @app.before_request
    def load_user_context():
        """Load user context before each request."""
        config_loader = getattr(app, "config_loader", None)
        if config_loader:
            # Set user context in config loader
            from .auth.decorators import get_current_user

            current_user = get_current_user()
            config_loader.set_user_context(current_user)

            # Reload configs for current user
            config_loader.load_all_configs()

    @app.before_request
    def cleanup_expired_links():
        """Clean up expired links before each request."""
        from .auth.decorators import get_current_user
        from .links.utils import check_expired_links

        config_loader = getattr(app, "config_loader", None)
        if config_loader and get_current_user():
            check_expired_links(config_loader)


def _setup_jinja_filters(app: Flask) -> None:
    """
    Set up custom Jinja2 filters.

    Args:
        app: Flask application instance.
    """

    @app.template_filter("to_datetime")
    def to_datetime_filter(date_string):
        """Convert datetime string to datetime object."""
        if not date_string:
            return None
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    @app.template_filter("datetime_local")
    def datetime_local_filter(dt):
        """Format datetime object for datetime-local input."""
        if not dt:
            return ""
        try:
            return dt.strftime("%Y-%m-%dT%H:%M")
        except (ValueError, AttributeError):
            return ""
