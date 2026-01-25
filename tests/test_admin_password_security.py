"""
Tests for admin password security to ensure passwords are never stored as hashes.

This module tests that admin passwords are only compared against environment
variables and never stored or accessed as hashes in the user configuration.
"""

import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from app.utils.user_manager import UserManager


class TestAdminPasswordSecurity:
    """Test cases for admin password security."""

    def setup_method(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.test_dir, "users", "users.toml")
        self.user_manager = UserManager(self.users_file)

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_admin_user_created_without_password_hash(self):
        """Test that admin user is created without a stored password hash."""
        # Admin user should be created automatically
        admin_user = self.user_manager.get_user("admin")

        assert admin_user is not None
        assert admin_user["is_admin"] is True
        assert admin_user["display_name"] == "Administrator"

        # Most importantly: no password hash should be stored
        assert "password_hash" not in admin_user

    def test_admin_authentication_uses_environment_variable(self):
        """Test that admin authentication only uses environment variable."""
        with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "test_secure_password"}):
            # Correct password should work
            result = self.user_manager.authenticate_user("admin", "test_secure_password")
            assert result is not None
            assert result["is_admin"] is True

            # Wrong password should fail
            result = self.user_manager.authenticate_user("admin", "wrong_password")
            assert result is None

    def test_admin_authentication_with_default_password(self):
        """Test that admin authentication works with default password when no env var is set."""
        # Ensure no environment variable is set
        with patch.dict(os.environ, {}, clear=True):
            # Default password should work
            result = self.user_manager.authenticate_user("admin", "admin")
            assert result is not None

            # Wrong password should fail
            result = self.user_manager.authenticate_user("admin", "wrong")
            assert result is None

    def test_admin_password_never_stored_after_authentication(self):
        """Test that admin password is never stored even after successful authentication."""
        with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "secure_pass_123"}):
            # Authenticate admin
            result = self.user_manager.authenticate_user("admin", "secure_pass_123")
            assert result is not None

            # Re-load config to ensure no changes were persisted
            self.user_manager._load_users_config()
            admin_user = self.user_manager.get_user("admin")

            # Still no password hash should be stored
            assert "password_hash" not in admin_user

    def test_admin_password_not_accessible_through_user_data(self):
        """Test that admin password cannot be accessed through user data methods."""
        with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "secret_password"}):
            admin_user = self.user_manager.get_user("admin")

            # No password-related fields should be accessible
            assert "password_hash" not in admin_user
            assert "password" not in admin_user
            assert admin_user.get("password_hash") is None

            # Only safe fields should be present
            expected_fields = {"is_admin", "display_name", "created_at"}
            actual_fields = set(admin_user.keys())
            assert actual_fields == expected_fields

    def test_regular_user_still_uses_password_hash(self):
        """Test that regular users still use password hashes (only admin is special)."""
        # Create a regular user
        success = self.user_manager.create_user(
            username="testuser",
            password="user_password",
            display_name="Test User",
            is_admin=False,
        )
        assert success is True

        # Regular user should have password hash
        user_data = self.user_manager.get_user("testuser")
        assert "password_hash" in user_data
        assert user_data["password_hash"] is not None

        # Authentication should work with hash
        result = self.user_manager.authenticate_user("testuser", "user_password")
        assert result is not None

    def test_admin_password_change_requires_environment_update(self):
        """Test that admin password can only be changed via environment variable."""
        # Set initial password
        with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "initial_pass"}):
            result = self.user_manager.authenticate_user("admin", "initial_pass")
            assert result is not None

            # Change environment variable
            with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "new_pass"}):
                # Old password should no longer work
                result = self.user_manager.authenticate_user("admin", "initial_pass")
                assert result is None

                # New password should work
                result = self.user_manager.authenticate_user("admin", "new_pass")
                assert result is not None

    def test_cannot_set_admin_password_hash_manually(self):
        """Test that manually setting admin password hash doesn't work."""
        # Try to manually set a password hash for admin (should be ignored)
        admin_user = self.user_manager.get_user("admin")

        # Even if we somehow modify the user data, authentication should still use env var
        admin_user_modified = admin_user.copy()
        admin_user_modified["password_hash"] = "fake_hash"

        # Save the modified config
        self.user_manager.users_config["users"]["admin"] = admin_user_modified
        self.user_manager.save_users_config()

        # Authentication should still use environment variable, not the fake hash
        with patch.dict(os.environ, {"TRUNK8_ADMIN_PASSWORD": "env_password"}):
            result = self.user_manager.authenticate_user("admin", "env_password")
            assert result is not None  # Should work with env var

            # Even if password matches the fake hash, it shouldn't work without env var
            result = self.user_manager.authenticate_user("admin", "fake_hash")
            assert result is None

    def test_admin_user_config_file_structure(self):
        """Test that admin user config file has correct structure without password fields."""
        # Read the raw config file
        import toml

        with open(self.users_file) as f:
            raw_config = toml.load(f)

        admin_config = raw_config["users"]["admin"]

        # Verify no password-related fields in file
        assert "password_hash" not in admin_config
        assert "password" not in admin_config

        # Verify required fields are present
        assert admin_config["is_admin"] is True
        assert admin_config["display_name"] == "Administrator"
        assert "created_at" in admin_config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
