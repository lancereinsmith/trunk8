"""
Pytest configuration and fixtures for Trunk8 application testing.

This module provides shared fixtures and configuration for all tests,
including test app creation, client setup, temporary file handling,
and test data generation.
"""

import os
import tempfile
from datetime import datetime
from typing import Any, Dict, Generator

import pytest
import toml
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.utils.config_loader import ConfigLoader


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def test_config_files(temp_dir: str) -> Dict[str, str]:
    """Create temporary config files for testing."""
    # Create config directory
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir, exist_ok=True)

    # Create users directory structure
    users_dir = os.path.join(temp_dir, "users")
    admin_dir = os.path.join(users_dir, "admin")
    admin_assets_dir = os.path.join(admin_dir, "assets")
    os.makedirs(admin_assets_dir, exist_ok=True)

    # Create config/config.toml
    config_path = os.path.join(config_dir, "config.toml")
    config_data = {
        "app": {
            "theme": "cosmo",
            "markdown_theme": "cerulean",
        },
        "session": {
            "permanent_lifetime_days": 30,
        },
    }
    with open(config_path, "w") as f:
        toml.dump(config_data, f)

    # Create users/users.toml
    users_path = os.path.join(users_dir, "users.toml")
    users_data = {
        "users": {
            "admin": {
                "password_hash": "test_password",  # Will be hashed by UserManager
                "is_admin": True,
                "display_name": "Test Administrator",
                "created_at": "2024-01-01T00:00:00",
            },
            "testuser": {
                "password_hash": "user_password",  # Will be hashed by UserManager
                "is_admin": False,
                "display_name": "Test User",
                "created_at": "2024-01-01T00:00:00",
            },
        }
    }
    with open(users_path, "w") as f:
        toml.dump(users_data, f)

    # Create admin links.toml
    admin_links_path = os.path.join(admin_dir, "links.toml")
    admin_links_data = {"links": {}}
    with open(admin_links_path, "w") as f:
        toml.dump(admin_links_data, f)

    # Create testuser directory and links.toml
    testuser_dir = os.path.join(users_dir, "testuser")
    testuser_assets_dir = os.path.join(testuser_dir, "assets")
    os.makedirs(testuser_assets_dir, exist_ok=True)

    testuser_links_path = os.path.join(testuser_dir, "links.toml")
    testuser_links_data = {"links": {}}
    with open(testuser_links_path, "w") as f:
        toml.dump(testuser_links_data, f)

    # Create config/themes.toml - copy from real themes file
    themes_path = os.path.join(config_dir, "themes.toml")
    try:
        # Try to copy the real themes file
        import shutil

        shutil.copy("config/themes.toml", themes_path)
    except FileNotFoundError:
        # Fallback to minimal themes if real file doesn't exist
        themes_data = {
            "themes": {
                "cosmo": {"name": "Cosmo", "description": "An ode to Metro"},
                "cerulean": {"name": "Cerulean", "description": "A calm blue sky"},
                "darkly": {"name": "Darkly", "description": "Dark theme"},
            }
        }
        with open(themes_path, "w") as f:
            toml.dump(themes_data, f)

    return {
        "config": config_path,
        "users": users_path,
        "admin_links": admin_links_path,
        "testuser_links": testuser_links_path,
        "themes": themes_path,
        "admin_assets": admin_assets_dir,
        "testuser_assets": testuser_assets_dir,
        "temp_dir": temp_dir,
    }


@pytest.fixture
def app(test_config_files: Dict[str, str], monkeypatch: pytest.MonkeyPatch) -> Flask:
    """Create and configure a test Flask application."""
    # Change to temp directory to use test config files
    monkeypatch.chdir(test_config_files["temp_dir"])

    # Set test environment variables
    monkeypatch.setenv("TRUNK8_SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("TRUNK8_ADMIN_PASSWORD", "test_password")

    # Create app
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client: FlaskClient) -> FlaskClient:
    """Create an authenticated test client."""
    # Login the client with admin credentials
    client.post("/auth/login", data={"username": "admin", "password": "test_password"})
    return client


@pytest.fixture
def sample_links() -> Dict[str, Any]:
    """Provide sample link data for testing."""
    return {
        "test_file": {
            "type": "file",
            "path": "test.txt",
        },
        "test_redirect": {
            "type": "redirect",
            "url": "https://example.com",
        },
        "test_markdown": {
            "type": "markdown",
            "path": "test.md",
        },
        "expired_link": {
            "type": "redirect",
            "url": "https://expired.com",
            "expiration_date": "2023-12-31T12:00:00",  # Always expired relative to mock date
        },
        "future_link": {
            "type": "redirect",
            "url": "https://future.com",
            "expiration_date": "2024-01-02T12:00:00",  # Future relative to mock date
        },
    }


@pytest.fixture
def config_loader(
    test_config_files: Dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> ConfigLoader:
    """Create a test config loader."""
    monkeypatch.chdir(test_config_files["temp_dir"])
    loader = ConfigLoader()
    loader.set_user_context("admin")  # Set admin context for testing
    loader.load_all_configs()
    return loader


@pytest.fixture
def populated_links(
    config_loader: ConfigLoader,
    sample_links: Dict[str, Any],
    test_config_files: Dict[str, str],
) -> ConfigLoader:
    """Create a config loader with pre-populated links."""
    # Add sample links to the config
    config_loader.links_config["links"] = sample_links.copy()

    # Create test files for file-based links in admin assets directory
    assets_dir = test_config_files["admin_assets"]

    # Create test.txt
    with open(os.path.join(assets_dir, "test.txt"), "w") as f:
        f.write("This is a test file.")

    # Create test.md
    with open(os.path.join(assets_dir, "test.md"), "w") as f:
        f.write("# Test Markdown\n\nThis is a test markdown file.")

    # Save the config
    config_loader.save_links_config()

    return config_loader


@pytest.fixture
def mock_datetime(monkeypatch: pytest.MonkeyPatch) -> type:
    """Mock datetime for consistent testing."""

    class MockDateTime:
        @classmethod
        def now(cls):
            return datetime(2024, 1, 1, 12, 0, 0)

        @classmethod
        def fromisoformat(cls, date_string):
            return datetime.fromisoformat(date_string)

    # Mock datetime in all relevant modules
    monkeypatch.setattr("app.links.utils.datetime", MockDateTime)
    monkeypatch.setattr("app.links.models.datetime", MockDateTime)
    monkeypatch.setattr("app.links.routes.datetime", MockDateTime)
    monkeypatch.setattr("datetime.datetime", MockDateTime)

    return MockDateTime
