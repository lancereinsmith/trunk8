"""
Tests for user deletion functionality including cascading deletion of links and assets.

This module tests the enhanced user deletion features that ensure all user data
is properly cleaned up when a user is deleted, including links, assets, and files.
"""

import os
import shutil
import tempfile
from unittest.mock import patch

import pytest
import toml

from app.utils.user_manager import UserManager


class TestUserDeletion:
    """Test cases for user deletion with cascading cleanup."""

    def setup_method(self):
        """Set up test environment with temporary directories."""
        self.test_dir = tempfile.mkdtemp()
        self.users_file = os.path.join(self.test_dir, "users", "users.toml")
        self.user_manager = UserManager(self.users_file)

        # Create test users
        self.user_manager.create_user("admin", "admin123", "Administrator", True)
        self.user_manager.create_user("testuser", "password123", "Test User", False)
        self.user_manager.create_user("testuser2", "password456", "Test User 2", False)

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_links_and_assets(self, username: str) -> dict:
        """Create test links and assets for a user."""
        user_dir = os.path.join(self.test_dir, "users", username)
        assets_dir = os.path.join(user_dir, "assets")
        links_file = os.path.join(user_dir, "links.toml")

        # Create some test assets
        os.makedirs(assets_dir, exist_ok=True)

        test_files = {
            "test1.txt": "This is test file 1",
            "test2.md": "# Test Markdown\nThis is a test markdown file",
            "image.png": b"\x89PNG\r\n\x1a\n" + b"fake_png_data" * 10,  # Fake binary data
        }

        for filename, content in test_files.items():
            file_path = os.path.join(assets_dir, filename)
            if isinstance(content, str):
                with open(file_path, "w") as f:
                    f.write(content)
            else:
                with open(file_path, "wb") as f:
                    f.write(content)

        # Create test links
        links_data = {
            "links": {
                "test-redirect": {"type": "redirect", "url": "https://example.com"},
                "test-file": {"type": "file", "path": "test1.txt"},
                "test-markdown": {"type": "markdown", "path": "test2.md"},
            }
        }

        with open(links_file, "w") as f:
            toml.dump(links_data, f)

        return {
            "files_created": len(test_files),
            "links_created": len(links_data["links"]),
            "total_size": sum(
                len(content.encode() if isinstance(content, str) else content)
                for content in test_files.values()
            ),
        }

    def test_successful_user_deletion_with_data(self):
        """Test successful deletion of user with links and assets."""
        username = "testuser"
        admin_user = "admin"

        # Create test data
        test_data = self._create_test_links_and_assets(username)

        # Verify data exists before deletion
        user_dir = os.path.join(self.test_dir, "users", username)
        assert os.path.exists(user_dir)
        assert os.path.exists(os.path.join(user_dir, "links.toml"))
        assert os.path.exists(os.path.join(user_dir, "assets"))

        # Get deletion preview
        preview = self.user_manager.get_user_deletion_preview(username)
        assert preview is not None
        assert preview["username"] == username
        assert preview["links_count"] == test_data["links_created"]
        assert preview["files_count"] == test_data["files_created"]
        assert preview["total_size"] > 0

        # Delete user
        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(username, admin_user)

        # Verify deletion was successful
        assert result is True

        # Verify user is removed from config
        assert self.user_manager.get_user(username) is None
        assert username not in self.user_manager.list_users()

        # Verify all user data is deleted
        assert not os.path.exists(user_dir)

        # Verify proper logging occurred
        mock_logger.info.assert_any_call(
            f"User data cleanup completed: Successfully deleted all data for user '{username}'"
        )
        mock_logger.info.assert_any_call(f"User '{username}' successfully deleted by {admin_user}")

    def test_delete_user_without_admin_privileges(self):
        """Test that non-admin users cannot delete users."""
        username = "testuser"
        non_admin_user = "testuser2"

        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(username, non_admin_user)

        assert result is False
        assert self.user_manager.get_user(username) is not None
        mock_logger.warning.assert_called_with(f"Delete user denied: {non_admin_user} is not admin")

    def test_cannot_delete_admin_user(self):
        """Test that admin user cannot be deleted."""
        admin_user = "admin"

        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(admin_user, admin_user)

        assert result is False
        assert self.user_manager.get_user(admin_user) is not None
        mock_logger.warning.assert_called_with("Delete user denied: Cannot delete admin user")

    def test_delete_nonexistent_user(self):
        """Test deletion of non-existent user."""
        username = "nonexistent"
        admin_user = "admin"

        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(username, admin_user)

        assert result is False
        mock_logger.warning.assert_called_with(f"Delete user failed: User '{username}' not found")

    def test_delete_user_without_data(self):
        """Test deletion of user with no links or assets."""
        username = "testuser"
        admin_user = "admin"

        # Delete user without creating any data
        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(username, admin_user)

        assert result is True
        assert self.user_manager.get_user(username) is None

        # Should still log successful cleanup even with no data
        mock_logger.info.assert_any_call(f"User '{username}' successfully deleted by {admin_user}")

    def test_deletion_preview_for_user_with_data(self):
        """Test getting deletion preview for user with data."""
        username = "testuser"
        test_data = self._create_test_links_and_assets(username)

        preview = self.user_manager.get_user_deletion_preview(username)

        assert preview is not None
        assert preview["username"] == username
        assert preview["links_count"] == test_data["links_created"]
        assert preview["files_count"] == test_data["files_created"]
        assert preview["total_size"] == test_data["total_size"]
        assert len(preview["directories"]) == 1

    def test_deletion_preview_for_user_without_data(self):
        """Test getting deletion preview for user without data."""
        username = "testuser"

        preview = self.user_manager.get_user_deletion_preview(username)

        assert preview is not None
        assert preview["username"] == username
        assert preview["links_count"] == 0
        assert preview["files_count"] == 0
        assert preview["total_size"] == 0

    def test_deletion_preview_for_nonexistent_user(self):
        """Test getting deletion preview for non-existent user."""
        username = "nonexistent"

        preview = self.user_manager.get_user_deletion_preview(username)

        assert preview is None

    def test_cleanup_with_permission_error(self):
        """Test cleanup handling when permission errors occur."""
        username = "testuser"
        admin_user = "admin"

        # Create test data
        self._create_test_links_and_assets(username)

        # Mock shutil.rmtree to raise PermissionError
        with (
            patch("shutil.rmtree", side_effect=PermissionError("Access denied")),
            patch("app.utils.user_manager.logger") as mock_logger,
        ):
            result = self.user_manager.delete_user(username, admin_user)

        # Should still succeed in removing user from config even if cleanup failed
        assert result is True  # User should be deleted from config even if file cleanup fails

        # Verify user is removed from config
        assert self.user_manager.get_user(username) is None

        # Should log the permission error
        mock_logger.warning.assert_any_call(
            "User data cleanup had issues: Permission denied while deleting user data: Access denied"
        )

    def test_cleanup_stats_accuracy(self):
        """Test that cleanup statistics are accurate."""
        username = "testuser"
        admin_user = "admin"

        # Create known test data
        test_data = self._create_test_links_and_assets(username)

        with patch("app.utils.user_manager.logger") as mock_logger:
            result = self.user_manager.delete_user(username, admin_user)

        assert result is True

        # Check that stats were logged correctly
        expected_stats_call = (
            f"Cleanup statistics: {test_data['links_created']} links, "
            f"{test_data['files_created']} files, "
            f"{test_data['total_size']} bytes freed"
        )
        mock_logger.info.assert_any_call(expected_stats_call)

    def test_deletion_with_corrupted_links_file(self):
        """Test deletion when links file is corrupted."""
        username = "testuser"
        admin_user = "admin"

        # Create user directory and corrupt links file
        user_dir = os.path.join(self.test_dir, "users", username)
        links_file = os.path.join(user_dir, "links.toml")

        with open(links_file, "w") as f:
            f.write("invalid toml content [[[")

        with patch("app.utils.user_manager.logger"):
            result = self.user_manager.delete_user(username, admin_user)

        # Should still succeed in deleting user
        assert result is True
        assert not os.path.exists(user_dir)

    @patch("os.path.getsize")
    def test_cleanup_with_inaccessible_files(self, mock_getsize):
        """Test cleanup when some files are inaccessible."""
        username = "testuser"
        admin_user = "admin"

        # Create test data
        self._create_test_links_and_assets(username)

        # Mock getsize to raise OSError for some files
        mock_getsize.side_effect = OSError("File not accessible")

        with patch("app.utils.user_manager.logger"):
            result = self.user_manager.delete_user(username, admin_user)

        # Should still succeed
        assert result is True

        # User directory should be deleted
        user_dir = os.path.join(self.test_dir, "users", username)
        assert not os.path.exists(user_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
