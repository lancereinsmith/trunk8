"""
User management utilities for multi-user Trunk8 system.

This module provides functionality for user authentication, creation,
and management in a multi-user environment with admin privileges.
"""

import hashlib
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import toml

from .logging_config import get_logger

logger = get_logger(__name__)


class UserManager:
    """
    Manages user accounts, authentication, and user-specific data access.

    Handles user creation, authentication, password management, and provides
    admin functionality to manage all users and their data.
    """

    def __init__(self, users_file: str = "users/users.toml") -> None:
        """
        Initialize the UserManager.

        Args:
            users_file: Path to the users configuration file.
        """
        self.users_file = users_file
        self.users_config: Dict[str, Any] = {}
        self._last_mod_time: Optional[float] = None
        self._load_users_config()

    def _load_users_config(self) -> None:
        """Load users configuration from file."""
        try:
            current_mod_time = os.path.getmtime(self.users_file)
            if current_mod_time != self._last_mod_time:
                with open(self.users_file, "r") as f:
                    self.users_config = toml.load(f)
                self._last_mod_time = current_mod_time
        except FileNotFoundError:
            # Create default users file with admin user
            self._create_default_users_file()
        except Exception as e:
            print(f"Error loading users config: {e}")
            self.users_config = {"users": {}}

    def _create_default_users_file(self) -> None:
        """Create default users file with admin user."""
        logger.info("Creating default users configuration file")

        # Admin password is never stored - only checked against environment variable
        default_config = {
            "users": {
                "admin": {
                    "is_admin": True,
                    "display_name": "Administrator",
                    "created_at": datetime.now().isoformat(),
                }
            }
        }

        # Ensure users directory exists
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)

        with open(self.users_file, "w") as f:
            toml.dump(default_config, f)

        self.users_config = default_config
        self._last_mod_time = os.path.getmtime(self.users_file)

        # Create admin user directory
        self._create_user_directory("admin")
        logger.info("Default users configuration created with admin user")

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.

        Args:
            password: Plain text password.

        Returns:
            Hashed password string.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def _create_user_directory(self, username: str) -> None:
        """
        Create user directory structure.

        Args:
            username: Username to create directory for.
        """
        # Use the correct base directory from users_file path
        base_dir = os.path.dirname(self.users_file)
        user_dir = os.path.join(base_dir, username)
        assets_dir = os.path.join(user_dir, "assets")

        os.makedirs(user_dir, exist_ok=True)
        os.makedirs(assets_dir, exist_ok=True)

        # Create empty links.toml for user
        links_file = os.path.join(user_dir, "links.toml")
        if not os.path.exists(links_file):
            with open(links_file, "w") as f:
                toml.dump({"links": {}}, f)

        # Create empty config.toml for regular users (not admin)
        # Admin uses global config/config.toml directly
        if username != "admin":
            config_file = os.path.join(user_dir, "config.toml")
            if not os.path.exists(config_file):
                with open(config_file, "w") as f:
                    toml.dump({"app": {}}, f)

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.

        For admin user: password is checked against TRUNK8_ADMIN_PASSWORD environment variable.
        For other users: password is checked against stored hash.

        Args:
            username: Username to authenticate.
            password: Plain text password.

        Returns:
            User data dict if authenticated, None otherwise.
        """
        self._load_users_config()  # Reload to get latest data

        users = self.users_config.get("users", {})
        user_data = users.get(username)

        if user_data:
            # Special handling for admin user - never use stored hash
            if username == "admin":
                admin_password = os.environ.get("TRUNK8_ADMIN_PASSWORD", "admin")
                if password == admin_password:
                    return user_data
                else:
                    return None

            # For regular users, check against stored hash
            stored_hash = user_data.get("password_hash")
            if not stored_hash:
                # User has no password hash set, cannot authenticate
                return None

            if stored_hash == password:  # For dealing with plain text passwords
                # Update to hashed password
                user_data["password_hash"] = self._hash_password(password)
                self.save_users_config()
                return user_data
            elif stored_hash == self._hash_password(password):
                return user_data

        return None

    def create_user(
        self, username: str, password: str, display_name: str, is_admin: bool = False
    ) -> bool:
        """
        Create a new user.

        Args:
            username: Unique username.
            password: Plain text password.
            display_name: Display name for the user.
            is_admin: Whether user has admin privileges.

        Returns:
            True if user created successfully, False otherwise.
        """
        logger.info(f"Creating new user: {username} (admin: {is_admin})")
        self._load_users_config()

        users = self.users_config.get("users", {})

        if username in users:
            logger.warning(
                f"User creation failed: username '{username}' already exists"
            )
            return False  # User already exists

        # Create user data
        user_data = {
            "password_hash": self._hash_password(password),
            "is_admin": is_admin,
            "display_name": display_name,
            "created_at": datetime.now().isoformat(),
        }

        users[username] = user_data
        self.users_config["users"] = users

        # Save config and create directory
        if self.save_users_config():
            self._create_user_directory(username)
            logger.info(f"User created successfully: {username} ({display_name})")
            return True

        logger.error(f"Failed to create user: {username}")
        return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by username.

        Args:
            username: Username to retrieve.

        Returns:
            User data dict if found, None otherwise.
        """
        self._load_users_config()
        return self.users_config.get("users", {}).get(username)

    def list_users(self) -> List[str]:
        """
        Get list of all usernames.

        Returns:
            List of usernames.
        """
        self._load_users_config()
        return list(self.users_config.get("users", {}).keys())

    def is_admin(self, username: str) -> bool:
        """
        Check if user has admin privileges.

        Args:
            username: Username to check.

        Returns:
            True if user is admin, False otherwise.
        """
        user_data = self.get_user(username)
        return user_data.get("is_admin", False) if user_data else False

    def get_user_links_file(self, username: str) -> str:
        """
        Get path to user's links.toml file.

        Args:
            username: Username.

        Returns:
            Path to user's links file.
        """
        # Use the correct base directory from users_file path
        base_dir = os.path.dirname(self.users_file)
        return os.path.join(base_dir, username, "links.toml")

    def get_user_assets_dir(self, username: str) -> str:
        """
        Get path to user's assets directory.

        Args:
            username: Username.

        Returns:
            Path to user's assets directory.
        """
        # Use the correct base directory from users_file path
        base_dir = os.path.dirname(self.users_file)
        return os.path.join(base_dir, username, "assets")

    def save_users_config(self) -> bool:
        """
        Save users configuration to file.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            # Ensure users directory exists
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)

            with open(self.users_file, "w") as f:
                toml.dump(self.users_config, f)
            self._last_mod_time = os.path.getmtime(self.users_file)
            return True
        except Exception as e:
            print(f"Error saving users config: {e}")
            return False

    def change_password(self, username: str, new_password: str) -> bool:
        """
        Change user password.

        Args:
            username: Username.
            new_password: New plain text password.

        Returns:
            True if changed successfully, False otherwise.
        """
        self._load_users_config()

        users = self.users_config.get("users", {})
        if username not in users:
            return False

        users[username]["password_hash"] = self._hash_password(new_password)
        return self.save_users_config()

    def _cleanup_user_data(self, username: str) -> Tuple[bool, str, Dict[str, int]]:
        """
        Clean up all user data including links and assets.

        Args:
            username: Username to clean up data for.

        Returns:
            Tuple of (success, message, cleanup_stats).
            cleanup_stats contains counts of deleted items.
        """
        stats = {
            "links_deleted": 0,
            "files_deleted": 0,
            "directories_deleted": 0,
            "total_size_freed": 0,
        }

        try:
            # Use the correct base directory from users_file path
            base_dir = os.path.dirname(self.users_file)
            user_dir = os.path.join(base_dir, username)

            if not os.path.exists(user_dir):
                return True, "User directory not found (already cleaned)", stats

            # First, count and delete individual files to get stats
            links_file = os.path.join(user_dir, "links.toml")
            assets_dir = os.path.join(user_dir, "assets")

            # Load and count user's links
            if os.path.exists(links_file):
                try:
                    with open(links_file, "r") as f:
                        links_data = toml.load(f)
                        stats["links_deleted"] = len(links_data.get("links", {}))
                except Exception as e:
                    print(f"Warning: Could not read links file for {username}: {e}")

            # Count and calculate size of assets
            if os.path.exists(assets_dir):
                try:
                    for root, dirs, files in os.walk(assets_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                stats["total_size_freed"] += os.path.getsize(file_path)
                                stats["files_deleted"] += 1
                            except OSError:
                                pass  # File might have been deleted or is inaccessible
                except Exception as e:
                    print(
                        f"Warning: Could not scan assets directory for {username}: {e}"
                    )

            # Now delete the entire user directory
            shutil.rmtree(user_dir)
            stats["directories_deleted"] = 1

            return True, f"Successfully deleted all data for user '{username}'", stats

        except PermissionError as e:
            return False, f"Permission denied while deleting user data: {e}", stats
        except FileNotFoundError:
            # Directory doesn't exist, consider it cleaned
            return True, "User directory not found (already cleaned)", stats
        except Exception as e:
            return False, f"Error deleting user data: {e}", stats

    def delete_user(self, username: str, requesting_user: str) -> bool:
        """
        Delete a user and all associated data (admin only).

        This method performs a cascading deletion that removes:
        - User account from the configuration
        - All user's links
        - All user's uploaded files and assets
        - User's entire directory structure

        Args:
            username: Username to delete.
            requesting_user: Username making the request (must be admin).

        Returns:
            True if deleted successfully, False otherwise.
        """
        logger.info(f"User deletion requested: {username} by {requesting_user}")

        if not self.is_admin(requesting_user):
            logger.warning(f"Delete user denied: {requesting_user} is not admin")
            return False

        if username == "admin":
            logger.warning("Delete user denied: Cannot delete admin user")
            return False

        self._load_users_config()

        users = self.users_config.get("users", {})
        if username not in users:
            logger.warning(f"Delete user failed: User '{username}' not found")
            return False

        # First, clean up all user data (links, assets, files)
        cleanup_success, cleanup_message, cleanup_stats = self._cleanup_user_data(
            username
        )

        if cleanup_success:
            logger.info(f"User data cleanup completed: {cleanup_message}")
            logger.info(
                f"Cleanup statistics: {cleanup_stats['links_deleted']} links, "
                f"{cleanup_stats['files_deleted']} files, "
                f"{cleanup_stats['total_size_freed']} bytes freed"
            )
        else:
            logger.warning(f"User data cleanup had issues: {cleanup_message}")
            # Continue with user deletion even if cleanup had issues

        # Remove user from configuration
        del users[username]

        # Save updated config
        if self.save_users_config():
            logger.info(f"User '{username}' successfully deleted by {requesting_user}")
            return True
        else:
            logger.error(f"Failed to save config after deleting user '{username}'")
            return False

    def get_user_deletion_preview(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a preview of what will be deleted when a user is removed.

        This method provides information about what data will be lost
        without actually performing the deletion.

        Args:
            username: Username to preview deletion for.

        Returns:
            Dictionary with deletion preview information, or None if user not found.
        """
        if not self.get_user(username):
            return None

        preview = {
            "username": username,
            "links_count": 0,
            "files_count": 0,
            "total_size": 0,
            "directories": [],
        }

        try:
            # Use the correct base directory from users_file path
            base_dir = os.path.dirname(self.users_file)
            user_dir = os.path.join(base_dir, username)

            if not os.path.exists(user_dir):
                return preview

            # Count links
            links_file = os.path.join(user_dir, "links.toml")
            if os.path.exists(links_file):
                try:
                    with open(links_file, "r") as f:
                        links_data = toml.load(f)
                        preview["links_count"] = len(links_data.get("links", {}))
                except Exception:
                    pass

            # Count files and calculate size
            assets_dir = os.path.join(user_dir, "assets")
            if os.path.exists(assets_dir):
                try:
                    for root, dirs, files in os.walk(assets_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                preview["total_size"] += os.path.getsize(file_path)
                                preview["files_count"] += 1
                            except OSError:
                                pass
                except Exception:
                    pass

            # List directories that will be deleted
            if os.path.exists(user_dir):
                preview["directories"].append(user_dir)

        except Exception as e:
            print(f"Error generating deletion preview for {username}: {e}")

        return preview
