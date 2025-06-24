"""
Test suite for link utility functions.

Tests cover expired link cleanup, user statistics, short code validation,
file size formatting, and other utility functions in app/links/utils.py.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import patch

from flask.testing import FlaskClient

from app.links.utils import (
    check_all_users_expired_links,
    check_expired_links,
    format_file_size,
    get_user_stats,
    validate_short_code,
)


class TestExpiredLinkCleanup:
    """Test expired link cleanup functionality."""

    def test_check_expired_links_no_current_user(self, app):
        """Test expired link cleanup when no current user is set."""
        config_loader = app.config_loader
        config_loader.current_user = None

        # Should not raise error and return gracefully
        check_expired_links(config_loader)

    def test_check_expired_links_no_expiration(
        self, app, authenticated_client: FlaskClient
    ):
        """Test expired link cleanup with links that have no expiration."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add links without expiration
        links = config_loader.links_config.setdefault("links", {})
        links["permanent"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
        }
        config_loader.save_links_config()

        # Run cleanup
        check_expired_links(config_loader)

        # Link should still exist
        config_loader.load_all_configs()
        assert "permanent" in config_loader.links_config.get("links", {})

    def test_check_expired_links_future_expiration(
        self, app, authenticated_client: FlaskClient
    ):
        """Test expired link cleanup with future expiration dates."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add link with future expiration
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        links = config_loader.links_config.setdefault("links", {})
        links["future"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": future_date,
        }
        config_loader.save_links_config()

        # Run cleanup
        check_expired_links(config_loader)

        # Link should still exist
        config_loader.load_all_configs()
        assert "future" in config_loader.links_config.get("links", {})

    def test_check_expired_links_past_expiration(
        self, app, authenticated_client: FlaskClient
    ):
        """Test expired link cleanup with past expiration dates."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add link with past expiration
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        links = config_loader.links_config.setdefault("links", {})
        links["expired"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": past_date,
        }
        config_loader.save_links_config()

        # Run cleanup
        with patch("builtins.print"):  # Suppress print statements
            check_expired_links(config_loader)

        # Link should be removed
        config_loader.load_all_configs()
        assert "expired" not in config_loader.links_config.get("links", {})

    def test_check_expired_links_invalid_date_format(
        self, app, authenticated_client: FlaskClient
    ):
        """Test expired link cleanup with invalid date format."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add link with invalid expiration date
        links = config_loader.links_config.setdefault("links", {})
        links["invalid_date"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": "not-a-date",
        }
        config_loader.save_links_config()

        # Run cleanup
        check_expired_links(config_loader)

        # Link should still exist (invalid date ignored)
        config_loader.load_all_configs()
        assert "invalid_date" in config_loader.links_config.get("links", {})

    def test_check_expired_links_file_cleanup(
        self, app, authenticated_client: FlaskClient
    ):
        """Test that expired file links have their files deleted."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Create temporary file
        assets_dir = config_loader.get_user_assets_dir("admin")
        os.makedirs(assets_dir, exist_ok=True)
        test_file = os.path.join(assets_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Add expired file link
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        links = config_loader.links_config.setdefault("links", {})
        links["expired_file"] = {
            "type": "file",
            "path": "test_file.txt",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": past_date,
        }
        config_loader.save_links_config()

        # Verify file exists
        assert os.path.exists(test_file)

        # Run cleanup
        with patch("builtins.print"):  # Suppress print statements
            check_expired_links(config_loader)

        # File should be deleted
        assert not os.path.exists(test_file)

        # Link should be removed
        config_loader.load_all_configs()
        assert "expired_file" not in config_loader.links_config.get("links", {})

    def test_check_expired_links_markdown_cleanup(
        self, app, authenticated_client: FlaskClient
    ):
        """Test that expired markdown links have their files deleted."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Create temporary markdown file
        assets_dir = config_loader.get_user_assets_dir("admin")
        os.makedirs(assets_dir, exist_ok=True)
        test_file = os.path.join(assets_dir, "test.md")
        with open(test_file, "w") as f:
            f.write("# Test Markdown")

        # Add expired markdown link
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        links = config_loader.links_config.setdefault("links", {})
        links["expired_md"] = {
            "type": "markdown",
            "path": "test.md",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": past_date,
        }
        config_loader.save_links_config()

        # Run cleanup
        with patch("builtins.print"):  # Suppress print statements
            check_expired_links(config_loader)

        # File should be deleted
        assert not os.path.exists(test_file)

    def test_check_expired_links_file_not_found(
        self, app, authenticated_client: FlaskClient
    ):
        """Test expired link cleanup when associated file doesn't exist."""
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add expired file link pointing to non-existent file
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        links = config_loader.links_config.setdefault("links", {})
        links["missing_file"] = {
            "type": "file",
            "path": "nonexistent.txt",
            "created_at": "2024-01-01T00:00:00",
            "expiration_date": past_date,
        }
        config_loader.save_links_config()

        # Run cleanup (should not raise error)
        with patch("builtins.print"):
            check_expired_links(config_loader)

        # Link should still be removed
        config_loader.load_all_configs()
        assert "missing_file" not in config_loader.links_config.get("links", {})

    def test_check_all_users_expired_links(
        self, app, authenticated_client: FlaskClient
    ):
        """Test system-wide expired link cleanup across all users."""
        config_loader = app.config_loader
        user_manager = app.user_manager

        # Create test users
        user_manager.create_user("user1", "pass", "User One", False)
        user_manager.create_user("user2", "pass", "User Two", False)

        # Add expired links for each user
        past_date = (datetime.now() - timedelta(days=1)).isoformat()

        for username in ["admin", "user1", "user2"]:
            config_loader.set_user_context(username)
            config_loader.load_all_configs()

            links = config_loader.links_config.setdefault("links", {})
            links[f"expired_{username}"] = {
                "type": "redirect",
                "url": "https://example.com",
                "created_at": "2024-01-01T00:00:00",
                "expiration_date": past_date,
            }
            config_loader.save_links_config()

        # Run system-wide cleanup
        with patch("builtins.print"):
            check_all_users_expired_links(config_loader, user_manager)

        # Check that all expired links were removed
        for username in ["admin", "user1", "user2"]:
            config_loader.set_user_context(username)
            config_loader.load_all_configs()
            assert f"expired_{username}" not in config_loader.links_config.get(
                "links", {}
            )

    def test_check_all_users_expired_links_error_handling(
        self, app, authenticated_client: FlaskClient
    ):
        """Test error handling in system-wide expired link cleanup."""
        config_loader = app.config_loader
        user_manager = app.user_manager

        # Create a user
        user_manager.create_user("erroruser", "pass", "Error User", False)

        # Mock an error during processing
        original_set_context = config_loader.set_user_context

        def error_set_context(username):
            if username == "erroruser":
                raise Exception("Test error")
            return original_set_context(username)

        with patch.object(
            config_loader, "set_user_context", side_effect=error_set_context
        ):
            with patch("builtins.print"):
                # Should not raise error, just continue with other users
                check_all_users_expired_links(config_loader, user_manager)


class TestUserStats:
    """Test user statistics functionality."""

    def test_get_user_stats_basic(self, app, authenticated_client: FlaskClient):
        """Test basic user statistics retrieval."""
        config_loader = app.config_loader
        user_manager = app.user_manager

        # Create test user
        user_manager.create_user("statuser", "pass", "Stats User", False)

        # Add some test links
        config_loader.set_user_context("statuser")
        config_loader.load_all_configs()

        links = config_loader.links_config.setdefault("links", {})
        links["redirect1"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
        }
        links["file1"] = {
            "type": "file",
            "path": "test.txt",
            "created_at": "2024-01-01T00:00:00",
        }
        links["markdown1"] = {
            "type": "markdown",
            "path": "test.md",
            "created_at": "2024-01-01T00:00:00",
        }
        config_loader.save_links_config()

        # Get stats
        stats = get_user_stats(config_loader, "statuser")

        assert stats["total_links"] == 3
        assert stats["redirect_links"] == 1
        assert stats["file_links"] == 1
        assert stats["markdown_links"] == 1
        assert stats["expired_links"] == 0

    def test_get_user_stats_with_expired(self, app, authenticated_client: FlaskClient):
        """Test user statistics with expired links."""
        config_loader = app.config_loader
        user_manager = app.user_manager

        # Create test user
        user_manager.create_user("expireduser", "pass", "Expired User", False)

        # Add links with expiration
        config_loader.set_user_context("expireduser")
        config_loader.load_all_configs()

        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        future_date = (datetime.now() + timedelta(days=1)).isoformat()

        links = config_loader.links_config.setdefault("links", {})
        links["expired"] = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": past_date,
        }
        links["active"] = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": future_date,
        }
        config_loader.save_links_config()

        # Get stats
        stats = get_user_stats(config_loader, "expireduser")

        assert stats["total_links"] == 2
        assert stats["expired_links"] == 1

    def test_get_user_stats_with_files(self, app, authenticated_client: FlaskClient):
        """Test user statistics with actual files."""
        config_loader = app.config_loader
        user_manager = app.user_manager

        # Create test user
        user_manager.create_user("fileuser", "pass", "File User", False)

        # Create test files
        assets_dir = config_loader.get_user_assets_dir("fileuser")
        os.makedirs(assets_dir, exist_ok=True)

        test_files = ["file1.txt", "file2.txt", "image.png"]
        file_contents = ["small content", "larger content here", "binary data" * 100]

        for filename, content in zip(test_files, file_contents):
            with open(os.path.join(assets_dir, filename), "w") as f:
                f.write(content)

        # Get stats
        stats = get_user_stats(config_loader, "fileuser")

        assert stats["total_files"] == 3
        assert stats["total_file_size"] > 0

    def test_get_user_stats_nonexistent_user(
        self, app, authenticated_client: FlaskClient
    ):
        """Test user statistics for nonexistent user."""
        config_loader = app.config_loader

        # Get stats for nonexistent user
        stats = get_user_stats(config_loader, "nonexistent")

        # Should return zero stats
        assert stats["total_links"] == 0
        assert stats["file_links"] == 0
        assert stats["redirect_links"] == 0
        assert stats["markdown_links"] == 0
        assert stats["expired_links"] == 0
        assert stats["total_files"] == 0
        assert stats["total_file_size"] == 0

    def test_get_user_stats_error_handling(
        self, app, authenticated_client: FlaskClient
    ):
        """Test error handling in user statistics."""
        config_loader = app.config_loader

        # Mock an error during context setting
        with patch.object(
            config_loader, "set_user_context", side_effect=Exception("Test error")
        ):
            with patch("builtins.print"):
                stats = get_user_stats(config_loader, "erroruser")

                # Should return zero stats on error
                assert stats["total_links"] == 0


class TestShortCodeValidation:
    """Test short code validation functionality."""

    def test_validate_short_code_valid_basic(self):
        """Test validation of basic valid short codes."""
        valid_codes = ["abc", "123", "test", "my-link", "my_link", "a1b2c3", "ABC"]

        for code in valid_codes:
            is_valid, error = validate_short_code(code)
            assert is_valid, f"Code '{code}' should be valid, got error: {error}"
            assert error == ""

    def test_validate_short_code_empty(self):
        """Test validation of empty short code."""
        is_valid, error = validate_short_code("")
        assert not is_valid
        assert "cannot be empty" in error

    def test_validate_short_code_none(self):
        """Test validation of None short code."""
        is_valid, error = validate_short_code(None)
        assert not is_valid
        assert "cannot be empty" in error

    def test_validate_short_code_too_long(self):
        """Test validation of overly long short code."""
        long_code = "a" * 51  # 51 characters
        is_valid, error = validate_short_code(long_code)
        assert not is_valid
        assert "50 characters or less" in error

    def test_validate_short_code_invalid_characters(self):
        """Test validation of short codes with invalid characters."""
        invalid_codes = [
            "hello world",  # space
            "test@code",  # @
            "code!",  # !
            "hash#tag",  # #
            "dollar$",  # $
            "percent%",  # %
            "caret^",  # ^
            "ampersand&",  # &
            "asterisk*",  # *
            "plus+",  # +
            "equals=",  # =
            "question?",  # ?
            "pipe|",  # |
            "backslash\\",  # \
            "forward/",  # /
            "colon:",  # :
            "semicolon;",  # ;
            "quote'",  # '
            'doublequote"',  # "
            "less<",  # <
            "greater>",  # >
            "comma,",  # ,
            "period.",  # .
            "brackets[]",  # []
            "braces{}",  # {}
            "parentheses()",  # ()
        ]

        for code in invalid_codes:
            is_valid, error = validate_short_code(code)
            assert not is_valid, f"Code '{code}' should be invalid"
            assert "letters, numbers, hyphens, and underscores" in error

    def test_validate_short_code_reserved_words(self):
        """Test validation of reserved words."""
        # Test reserved words that contain only valid characters
        reserved_words = [
            "settings",
            "users",
            "profile",
            "add",
            "links",
            "edit_link",
            "delete_link",
            "delete",
            "auth",
            "login",
            "logout",
            "register",
            "admin",
            "api",
            "static",
            "assets",
            "edit",
            "new",
            "create",
            "update",
            "remove",
            "list",
            "index",
            "home",
            "dashboard",
            "config",
            "system",
        ]

        for word in reserved_words:
            is_valid, error = validate_short_code(word)
            assert not is_valid, f"Reserved word '{word}' should be invalid"
            assert "reserved word" in error

        # Test case insensitive
        for word in ["ADMIN", "Settings", "LOGIN"]:
            is_valid, error = validate_short_code(word)
            assert not is_valid, (
                f"Reserved word '{word}' should be invalid (case insensitive)"
            )
            assert "reserved word" in error

        # Test reserved words with invalid characters (should fail on character validation first)
        invalid_char_reserved = ["favicon.ico", "robots.txt"]
        for word in invalid_char_reserved:
            is_valid, error = validate_short_code(word)
            assert not is_valid, f"Reserved word '{word}' should be invalid"
            assert "letters, numbers, hyphens, and underscores" in error

    def test_validate_short_code_edge_cases(self):
        """Test validation edge cases."""
        # Minimum length (1 character)
        is_valid, error = validate_short_code("a")
        assert is_valid

        # Maximum length (50 characters)
        max_code = "a" * 50
        is_valid, error = validate_short_code(max_code)
        assert is_valid

        # Only hyphens and underscores
        is_valid, error = validate_short_code("_-_-_")
        assert is_valid

        # Mixed case
        is_valid, error = validate_short_code("MyTest-Link_123")
        assert is_valid


class TestFileSizeFormatting:
    """Test file size formatting utility."""

    def test_format_file_size_zero(self):
        """Test formatting of zero bytes."""
        assert format_file_size(0) == "0 B"

    def test_format_file_size_bytes(self):
        """Test formatting of byte sizes."""
        assert format_file_size(1) == "1 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_file_size_kilobytes(self):
        """Test formatting of kilobyte sizes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"  # 1.5 KB
        assert format_file_size(102400) == "100.0 KB"

    def test_format_file_size_megabytes(self):
        """Test formatting of megabyte sizes."""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        assert format_file_size(1024 * 1024 * 100) == "100.0 MB"

    def test_format_file_size_gigabytes(self):
        """Test formatting of gigabyte sizes."""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1536 * 1024 * 1024) == "1.5 GB"

    def test_format_file_size_terabytes(self):
        """Test formatting of terabyte sizes."""
        assert format_file_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        assert format_file_size(1536 * 1024 * 1024 * 1024) == "1.5 TB"

    def test_format_file_size_very_large(self):
        """Test formatting of very large sizes."""
        # Larger than TB should still be formatted as TB
        very_large = 1024 * 1024 * 1024 * 1024 * 1024  # 1 PB
        result = format_file_size(very_large)
        assert result.endswith(" TB")
        assert "1024.0" in result
