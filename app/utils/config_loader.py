"""
Configuration loader for TOML files used in the Trunk8 application.

This module provides the ConfigLoader class which handles loading, reloading,
and saving TOML configuration files with automatic file modification tracking.
Now supports multi-user functionality with per-user data isolation and
per-user theme configuration.
"""

import os
from datetime import datetime
from typing import Any

import toml


class ConfigLoader:
    """
    Handles loading and reloading of TOML configuration files.

    This class provides functionality to load both application and links
    configuration from TOML files, with automatic reloading when files
    are modified. It tracks file modification times to avoid unnecessary
    reloads and provides save functionality.

    Now supports multi-user functionality with per-user data isolation
    and per-user theme configuration.

    Attributes:
        app_config (Dict[str, Any]): Loaded application configuration data.
        user_config (Dict[str, Any]): Loaded per-user configuration data.
        links_config (Dict[str, Any]): Loaded links configuration data.
        themes_config (Dict[str, Any]): Loaded themes configuration data.
        current_user (Optional[str]): Currently active user context.
    """

    def __init__(self) -> None:
        """
        Initialize the ConfigLoader.

        Sets up empty configuration dictionaries and modification time tracking.
        """
        self.app_config: dict[str, Any] = {}
        self.user_config: dict[str, Any] = {}
        self.links_config: dict[str, Any] = {}
        self.themes_config: dict[str, Any] = {}
        self._last_app_config_mod_time: float | None = None
        self._last_user_config_mod_time: float | None = None
        self._last_links_config_mod_time: float | None = None
        self._last_themes_config_mod_time: float | None = None
        self._current_links_path: str | None = None
        self._current_user_config_path: str | None = None

        # Multi-user support
        self.current_user: str | None = None
        self._user_mod_times: dict[str, float] = {}

    def set_user_context(self, username: str | None) -> None:
        """
        Set the current user context for data access.

        Args:
            username: Username to set as current context, None for global.
        """
        if self.current_user != username:
            self.current_user = username
            # Reset config to force reload for new user
            self._last_links_config_mod_time = None
            self._last_user_config_mod_time = None
            self._current_links_path = None
            self._current_user_config_path = None

    def get_user_links_file(self, username: str | None = None) -> str:
        """
        Get the links file path for a specific user.

        Args:
            username: Username, defaults to current_user, fallback to admin.

        Returns:
            Path to the user's links file (absolute path).
        """
        user = username or self.current_user or "admin"  # Always default to admin user
        relative_path = os.path.join("users", user, "links.toml")
        return os.path.abspath(relative_path)

    def get_user_config_file(self, username: str | None = None) -> str:
        """
        Get the config file path for a specific user.

        Args:
            username: Username, defaults to current_user, fallback to admin.

        Returns:
            Path to the user's config file (absolute path).
        """
        user = username or self.current_user or "admin"  # Always default to admin user
        relative_path = os.path.join("users", user, "config.toml")
        return os.path.abspath(relative_path)

    def get_user_assets_dir(self, username: str | None = None) -> str:
        """
        Get the assets directory path for a specific user.

        Args:
            username: Username, defaults to current_user, fallback to admin.

        Returns:
            Path to the user's assets directory (absolute path).
        """
        user = username or self.current_user or "admin"  # Always default to admin user
        relative_path = os.path.join("users", user, "assets")
        return os.path.abspath(relative_path)

    def load_all_configs(self) -> None:
        """
        Load all configuration files.

        Loads app config, themes config, user config, and links config.
        Links and user configs load per-user files based on current context.
        """
        self._load_app_config()
        self._load_themes_config()
        self._load_user_config()
        self._load_links_config()

    def _load_app_config(self) -> None:
        """
        Load application configuration from config/config.toml.

        This now contains only admin-level settings including session
        configuration and default theme settings.

        Checks file modification time and reloads if necessary.
        Creates default configuration file if none exists.
        """
        app_config_path = "config/config.toml"

        try:
            current_mod_time = os.path.getmtime(app_config_path)
            if current_mod_time != self._last_app_config_mod_time:
                with open(app_config_path) as f:
                    self.app_config = toml.load(f)

                self._last_app_config_mod_time = current_mod_time
                print(f"App config reloaded at {datetime.now()}")
        except FileNotFoundError:
            # Create default config directory and file
            os.makedirs("config", exist_ok=True)
            default_config = {
                "app": {
                    "theme": "cerulean",  # Default theme for new users
                    "markdown_theme": "cerulean",  # Default markdown theme for new users
                    "max_file_size_mb": 100,  # Maximum file size for uploads in MB
                },
                "session": {"permanent_lifetime_days": 30},
            }
            with open(app_config_path, "w") as f:
                toml.dump(default_config, f)
            self.app_config = default_config
            self._last_app_config_mod_time = os.path.getmtime(app_config_path)
        except Exception as e:
            print(f"Error loading app config file: {e}")

    def _load_user_config(self) -> None:
        """
        Load per-user configuration from users/{username}/config.toml.

        Contains user-specific theme overrides. Falls back to admin-level
        defaults if user config doesn't exist or is missing values.

        Admin user doesn't have a personal config file and uses global
        config/config.toml directly.

        Checks file modification time and reloads if necessary.
        Creates empty user config file if none exists (except for admin).
        """
        # Admin uses global config directly, no personal config file
        if self.current_user == "admin":
            self.user_config = {"app": {}}
            self._last_user_config_mod_time = None
            return

        user_config_path = self.get_user_config_file()

        # Check if user config file path has changed, reset mod time if so
        if self._current_user_config_path != user_config_path:
            self._current_user_config_path = user_config_path
            self._last_user_config_mod_time = None

        try:
            current_mod_time = os.path.getmtime(user_config_path)
            if current_mod_time != self._last_user_config_mod_time:
                with open(user_config_path) as f:
                    self.user_config = toml.load(f)
                self._last_user_config_mod_time = current_mod_time
                print(f"User config reloaded for user '{self.current_user}' at {datetime.now()}")
        except FileNotFoundError:
            # Only create config files for non-admin users
            # Admin uses global config/config.toml directly
            user = self.current_user or "admin"  # Default logic matches get_user_config_file
            if user == "admin":
                # Admin users don't have personal config files
                self.user_config = {"app": {}}
                self._last_user_config_mod_time = None
                return

            # Create directory structure and empty user config file for regular users
            user_config_dir = os.path.dirname(user_config_path)
            if user_config_dir:
                os.makedirs(user_config_dir, exist_ok=True)

            # Create empty user config - user inherits from admin defaults
            with open(user_config_path, "w") as f:
                toml.dump({"app": {}}, f)
            self.user_config = {"app": {}}
            self._last_user_config_mod_time = os.path.getmtime(user_config_path)
        except Exception as e:
            print(f"Error loading user config file: {e}")

    def get_effective_theme(self) -> str:
        """
        Get the effective theme for the current user.

        Admin users get themes directly from global config.
        Regular users get user-specific theme if set, otherwise admin default.

        Returns:
            str: Theme name.
        """
        # Admin uses global config directly
        if self.current_user == "admin":
            return self.app_config.get("app", {}).get("theme", "cerulean")

        # Regular users: user override or admin default
        user_theme = self.user_config.get("app", {}).get("theme")
        if user_theme:
            return user_theme
        return self.app_config.get("app", {}).get("theme", "cerulean")

    def get_effective_markdown_theme(self) -> str:
        """
        Get the effective markdown theme for the current user.

        Admin users get themes directly from global config.
        Regular users get user-specific markdown theme if set, otherwise admin default.

        Returns:
            str: Markdown theme name.
        """
        # Admin uses global config directly
        if self.current_user == "admin":
            return self.app_config.get("app", {}).get("markdown_theme", "cerulean")

        # Regular users: user override or admin default
        user_theme = self.user_config.get("app", {}).get("markdown_theme")
        if user_theme:
            return user_theme
        return self.app_config.get("app", {}).get("markdown_theme", "cerulean")

    def get_max_file_size_bytes(self) -> int:
        """
        Get the maximum file size limit in bytes.

        Returns the configured max_file_size_mb from app config,
        converted to bytes. Defaults to 100MB if not configured.

        Returns:
            int: Maximum file size in bytes.
        """
        max_size_mb = self.app_config.get("app", {}).get("max_file_size_mb", 100)
        return max_size_mb * 1024 * 1024

    def _load_links_config(self) -> None:
        """
        Load links configuration from user-specific or global links.toml.

        Uses the current user context to determine which links file to load.
        Checks file modification time and reloads if necessary. Creates
        an empty links file if none exists.
        """
        links_config_path = self.get_user_links_file()

        # Check if links file path has changed, reset mod time if so
        if self._current_links_path != links_config_path:
            self._current_links_path = links_config_path
            self._last_links_config_mod_time = None

        try:
            current_mod_time = os.path.getmtime(links_config_path)
            if current_mod_time != self._last_links_config_mod_time:
                with open(links_config_path) as f:
                    self.links_config = toml.load(f)
                self._last_links_config_mod_time = current_mod_time
                print(f"Links config reloaded for user '{self.current_user}' at {datetime.now()}")
        except FileNotFoundError:
            # Create directory structure and empty links config file
            links_dir = os.path.dirname(links_config_path)
            if links_dir:
                os.makedirs(links_dir, exist_ok=True)

            with open(links_config_path, "w") as f:
                toml.dump({"links": {}}, f)
            self.links_config = {"links": {}}
            self._last_links_config_mod_time = os.path.getmtime(links_config_path)
        except Exception as e:
            print(f"Error loading links config file: {e}")

    def _load_themes_config(self) -> None:
        """
        Load themes configuration from config/themes.toml.

        Checks file modification time and reloads if necessary.
        Falls back to built-in themes if file doesn't exist.
        """
        themes_config_path = "config/themes.toml"

        try:
            current_mod_time = os.path.getmtime(themes_config_path)
            if current_mod_time != self._last_themes_config_mod_time:
                with open(themes_config_path) as f:
                    self.themes_config = toml.load(f)
                self._last_themes_config_mod_time = current_mod_time
        except FileNotFoundError:
            # Create default themes.toml file
            os.makedirs("config", exist_ok=True)
            default_themes = self._get_default_themes()
            with open(themes_config_path, "w") as f:
                toml.dump(default_themes, f)
            self.themes_config = default_themes
            self._last_themes_config_mod_time = os.path.getmtime(themes_config_path)

    def _get_default_themes(self) -> dict[str, Any]:
        """
        Get default themes configuration.

        Returns:
            Dict[str, Any]: Default themes configuration.
        """
        return {
            "themes": {
                "brite": {"name": "Brite", "description": "Clean and bright design"},
                "cerulean": {"name": "Cerulean", "description": "A calm blue sky"},
                "cosmo": {"name": "Cosmo", "description": "An ode to Metro"},
                "cyborg": {
                    "name": "Cyborg",
                    "description": "Jet black and electric blue",
                },
                "darkly": {"name": "Darkly", "description": "Flatly in night mode"},
                "flatly": {"name": "Flatly", "description": "Flat and modern"},
                "journal": {
                    "name": "Journal",
                    "description": "Crisp like a new sheet of paper",
                },
                "litera": {
                    "name": "Litera",
                    "description": "The medium is the message",
                },
                "lumen": {"name": "Lumen", "description": "Light and shadow"},
                "lux": {"name": "Lux", "description": "A touch of class"},
                "materia": {
                    "name": "Materia",
                    "description": "Material is the metaphor",
                },
                "minty": {"name": "Minty", "description": "A fresh feel"},
                "morph": {"name": "Morph", "description": "A modern take"},
                "pulse": {"name": "Pulse", "description": "A trace of purple"},
                "quartz": {"name": "Quartz", "description": "A gem of a theme"},
                "sandstone": {"name": "Sandstone", "description": "A touch of warmth"},
                "simplex": {"name": "Simplex", "description": "Mini and minimalist"},
                "sketchy": {"name": "Sketchy", "description": "A hand-drawn look"},
                "slate": {"name": "Slate", "description": "Shades of gunmetal gray"},
                "solar": {"name": "Solar", "description": "A spin on Solarized"},
                "spacelab": {"name": "Spacelab", "description": "Silvery and sleek"},
                "superhero": {
                    "name": "Superhero",
                    "description": "The brave and the blue",
                },
                "united": {
                    "name": "United",
                    "description": "Ubuntu orange and unique font",
                },
                "vapor": {"name": "Vapor", "description": "A subtle theme"},
                "yeti": {"name": "Yeti", "description": "A friendly foundation"},
                "zephyr": {"name": "Zephyr", "description": "Breezy and beautiful"},
            }
        }

    def save_app_config(self) -> bool:
        """
        Save the current application configuration to file.

        Writes the current app_config dictionary to the configured app
        config file and updates the modification time tracking.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        app_config_path = "config/config.toml"
        try:
            with open(app_config_path, "w") as f:
                toml.dump(self.app_config, f)
            self._last_app_config_mod_time = os.path.getmtime(app_config_path)
            return True
        except Exception as e:
            print(f"Error saving app config: {e}")
            return False

    def save_user_config(self, username: str | None = None) -> bool:
        """
        Save the current user configuration to file.

        Writes the current user_config dictionary to the user-specific
        config file and updates the modification time tracking.

        Admin users don't have personal config files - they use global config.

        Args:
            username: Username to save for, defaults to current_user.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        user = username or self.current_user

        # Admin users don't have personal config files
        if user == "admin":
            # For admin, changes should be saved to global config instead
            return self.save_app_config()

        user_config_path = self.get_user_config_file(username)
        try:
            # Ensure directory exists
            user_config_dir = os.path.dirname(user_config_path)
            if user_config_dir:
                os.makedirs(user_config_dir, exist_ok=True)

            with open(user_config_path, "w") as f:
                toml.dump(self.user_config, f)
            self._last_user_config_mod_time = os.path.getmtime(user_config_path)
            return True
        except Exception as e:
            print(f"Error saving user config: {e}")
            return False

    def save_links_config(self, username: str | None = None) -> bool:
        """
        Save the current links configuration to file.

        Writes the current links_config dictionary to the user-specific
        links file and updates the modification time tracking.

        Args:
            username: Username to save for, defaults to current_user.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        links_config_path = self.get_user_links_file(username)
        try:
            # Ensure directory exists
            links_dir = os.path.dirname(links_config_path)
            if links_dir:
                os.makedirs(links_dir, exist_ok=True)

            with open(links_config_path, "w") as f:
                toml.dump(self.links_config, f)
            self._last_links_config_mod_time = os.path.getmtime(links_config_path)
            return True
        except Exception as e:
            print(f"Error saving links config: {e}")
            return False

    def get_all_user_links(self, admin_username: str) -> dict[str, dict[str, Any]]:
        """
        Get all links from all users (admin only).

        Args:
            admin_username: Username of admin requesting data.

        Returns:
            Dictionary with usernames as keys and their links as values.
        """
        from .user_manager import UserManager

        user_manager = UserManager()
        if not user_manager.is_admin(admin_username):
            return {}

        all_links = {}
        for username in user_manager.list_users():
            user_links_file = self.get_user_links_file(username)
            try:
                with open(user_links_file) as f:
                    user_links = toml.load(f)
                    all_links[username] = user_links.get("links", {})
            except FileNotFoundError:
                all_links[username] = {}
            except Exception as e:
                print(f"Error loading links for user {username}: {e}")
                all_links[username] = {}

        return all_links

    @property
    def available_themes(self) -> list[str]:
        """
        Get list of available theme names.

        Returns:
            List[str]: List of available theme names.
        """
        return list(self.themes_config.get("themes", {}).keys())

    @property
    def themes_for_template(self) -> list[dict[str, str]]:
        """
        Get themes formatted for template rendering.

        Returns:
            List[Dict[str, str]]: List of theme dictionaries with name, value, description.
        """
        themes = []
        themes_data = self.themes_config.get("themes", {})

        for theme_key, theme_info in themes_data.items():
            if isinstance(theme_info, str):
                # Simple string description format
                theme_data = {
                    "value": theme_key,
                    "name": theme_key.title(),
                    "description": theme_info,
                }
            elif isinstance(theme_info, dict):
                # Dictionary format with name and description
                theme_data = {
                    "value": theme_key,
                    "name": theme_info.get("name", theme_key.title()),
                    "description": theme_info.get("description", ""),
                }
            else:
                # Fallback format
                theme_data = {
                    "value": theme_key,
                    "name": theme_key.title(),
                    "description": "",
                }
            themes.append(theme_data)

        return themes
