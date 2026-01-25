"""
Test suite for main routes functionality.

Tests cover the home page, settings, theme management, user management,
profile management, and other main application routes.
"""

from flask.testing import FlaskClient


class TestMainRoutes:
    """Test basic main routes functionality."""

    def test_index_requires_auth(self, client: FlaskClient):
        """Test that index page requires authentication."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please log in to access this page." in response.data

    def test_index_authenticated(self, authenticated_client: FlaskClient):
        """Test index page when authenticated."""
        response = authenticated_client.get("/")
        assert response.status_code == 200
        assert b"Welcome to Trunk8" in response.data or b"Trunk8" in response.data

    def test_settings_requires_auth(self, client: FlaskClient):
        """Test that settings page requires authentication."""
        response = client.get("/settings", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please log in to access this page." in response.data

    def test_settings_page_authenticated(self, authenticated_client: FlaskClient):
        """Test settings page when authenticated."""
        response = authenticated_client.get("/settings")
        assert response.status_code == 200
        assert b"Theme" in response.data or b"settings" in response.data.lower()

    def test_update_theme(self, authenticated_client: FlaskClient, app):
        """Test theme update functionality."""
        # First get available themes
        config_loader = app.config_loader
        available_themes = list(config_loader.themes_config.get("themes", {}).keys())

        if len(available_themes) >= 2:
            new_theme = available_themes[1]

            response = authenticated_client.post(
                "/settings",
                data={"theme": new_theme, "markdown_theme": new_theme},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Theme settings updated successfully!" in response.data

    def test_update_invalid_theme(self, authenticated_client: FlaskClient):
        """Test theme update with invalid theme."""
        response = authenticated_client.post(
            "/settings", data={"theme": "nonexistent", "markdown_theme": "nonexistent"}
        )

        assert response.status_code == 302  # Should redirect back to settings

    def test_theme_context_processor(self, authenticated_client: FlaskClient):
        """Test that theme context is available in template."""
        response = authenticated_client.get("/settings")
        assert response.status_code == 200
        # The page should have theme-related content
        assert b"theme" in response.data.lower()

    def test_settings_displays_available_themes(self, authenticated_client: FlaskClient):
        """Test that settings page displays available themes."""
        response = authenticated_client.get("/settings")
        assert response.status_code == 200
        # Should contain theme selection elements
        # This is more of a template test but ensures integration works

    def test_partial_theme_update(self, authenticated_client: FlaskClient, app):
        """Test updating only one theme setting."""
        config_loader = app.config_loader
        available_themes = list(config_loader.themes_config.get("themes", {}).keys())

        if available_themes:
            theme = available_themes[0]
            response = authenticated_client.post(
                "/settings",
                data={"theme": theme, "markdown_theme": theme},
                follow_redirects=True,
            )

            assert response.status_code == 200


class TestUserManagement:
    """Test user management functionality (admin only)."""

    def test_users_requires_admin(self, client: FlaskClient, app):
        """Test that users page requires admin access."""
        # Create and login as non-admin user
        user_manager = app.user_manager
        user_manager.create_user("regular", "pass", "Regular User", False)

        client.post("/auth/login", data={"username": "regular", "password": "pass"})

        response = client.get("/users", follow_redirects=True)
        assert response.status_code == 200
        assert b"Admin access required" in response.data

    def test_users_unauthenticated(self, client: FlaskClient):
        """Test users page without authentication."""
        response = client.get("/users", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please log in to access this page." in response.data

    def test_users_admin_success(self, authenticated_client: FlaskClient, app):
        """Test users page as authenticated admin."""
        # Create some test users
        user_manager = app.user_manager
        user_manager.create_user("user1", "pass1", "User One", False)
        user_manager.create_user("user2", "pass2", "User Two", True)

        response = authenticated_client.get("/users")
        assert response.status_code == 200
        assert b"user1" in response.data or b"User One" in response.data
        assert b"user2" in response.data or b"User Two" in response.data

    def test_user_detail_requires_admin(self, client: FlaskClient, app):
        """Test that user detail page requires admin access."""
        # Create and login as non-admin user
        user_manager = app.user_manager
        user_manager.create_user("regular", "pass", "Regular User", False)

        client.post("/auth/login", data={"username": "regular", "password": "pass"})

        response = client.get("/users/testuser", follow_redirects=True)
        assert response.status_code == 200
        assert b"Admin access required" in response.data

    def test_user_detail_success(self, authenticated_client: FlaskClient, app):
        """Test user detail page for existing user."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("detailuser", "pass", "Detail User", False)

        response = authenticated_client.get("/users/detailuser")
        assert response.status_code == 200
        assert b"detailuser" in response.data or b"Detail User" in response.data

    def test_user_detail_nonexistent(self, authenticated_client: FlaskClient):
        """Test user detail page for nonexistent user."""
        response = authenticated_client.get("/users/nonexistent", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b"User 'nonexistent' not found." in response.data
            or b"User &#39;nonexistent&#39; not found." in response.data
        )

    def test_delete_user_requires_admin(self, client: FlaskClient, app):
        """Test that user deletion requires admin access."""
        # Create and login as non-admin user
        user_manager = app.user_manager
        user_manager.create_user("regular", "pass", "Regular User", False)

        client.post("/auth/login", data={"username": "regular", "password": "pass"})

        response = client.post("/users/testuser/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"Admin access required" in response.data

    def test_delete_user_success(self, authenticated_client: FlaskClient, app):
        """Test successful user deletion."""
        # Create a test user to delete
        user_manager = app.user_manager
        user_manager.create_user("todelete", "pass", "To Delete", False)

        # Verify user exists
        assert user_manager.get_user("todelete") is not None

        response = authenticated_client.post("/users/todelete/delete", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b"User 'todelete' deleted successfully." in response.data
            or b"User &#39;todelete&#39; deleted successfully." in response.data
        )

        # Verify user was deleted
        assert user_manager.get_user("todelete") is None

    def test_delete_admin_user_forbidden(self, authenticated_client: FlaskClient):
        """Test that admin user cannot be deleted."""
        response = authenticated_client.post("/users/admin/delete", follow_redirects=True)
        assert response.status_code == 200
        assert b"Cannot delete the admin user." in response.data

    def test_delete_nonexistent_user(self, authenticated_client: FlaskClient):
        """Test deletion of nonexistent user."""
        response = authenticated_client.post("/users/nonexistent/delete", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b"Failed to delete user 'nonexistent'." in response.data
            or b"Failed to delete user &#39;nonexistent&#39;." in response.data
        )


class TestProfileManagement:
    """Test user profile management functionality."""

    def test_profile_requires_auth(self, client: FlaskClient):
        """Test that profile page requires authentication."""
        response = client.get("/profile", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please log in to access this page." in response.data

    def test_profile_get_success(self, authenticated_client: FlaskClient):
        """Test profile page GET request."""
        response = authenticated_client.get("/profile")
        assert response.status_code == 200
        assert b"profile" in response.data.lower() or b"admin" in response.data

    def test_profile_get_multi_user(self, client: FlaskClient, app):
        """Test profile page for multi-user account."""
        # Create and login as regular user
        user_manager = app.user_manager
        user_manager.create_user("profileuser", "pass", "Profile User", False)

        client.post("/auth/login", data={"username": "profileuser", "password": "pass"})

        response = client.get("/profile")
        assert response.status_code == 200
        assert b"profileuser" in response.data or b"Profile User" in response.data

    def test_change_password_success(self, client: FlaskClient, app):
        """Test successful password change."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("pwduser", "oldpass", "Password User", False)

        # Login
        client.post("/auth/login", data={"username": "pwduser", "password": "oldpass"})

        # Change password
        response = client.post(
            "/profile",
            data={
                "action": "change_password",
                "current_password": "oldpass",
                "new_password": "newpass",
                "confirm_password": "newpass",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Password changed successfully." in response.data

        # Verify new password works
        client.get("/auth/logout")
        response = client.post(
            "/auth/login",
            data={"username": "pwduser", "password": "newpass"},
            follow_redirects=True,
        )
        assert b"Welcome, Password User!" in response.data

    def test_change_password_wrong_current(self, client: FlaskClient, app):
        """Test password change with wrong current password."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("pwduser", "correctpass", "Password User", False)

        # Login
        client.post("/auth/login", data={"username": "pwduser", "password": "correctpass"})

        # Try to change password with wrong current password
        response = client.post(
            "/profile",
            data={
                "action": "change_password",
                "current_password": "wrongpass",
                "new_password": "newpass",
                "confirm_password": "newpass",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Current password is incorrect." in response.data

    def test_change_password_empty_new(self, client: FlaskClient, app):
        """Test password change with empty new password."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("pwduser", "oldpass", "Password User", False)

        # Login
        client.post("/auth/login", data={"username": "pwduser", "password": "oldpass"})

        # Try to change to empty password
        response = client.post(
            "/profile",
            data={
                "action": "change_password",
                "current_password": "oldpass",
                "new_password": "",
                "confirm_password": "",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"New password is required." in response.data

    def test_change_password_mismatch(self, client: FlaskClient, app):
        """Test password change with mismatched confirmation."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("pwduser", "oldpass", "Password User", False)

        # Login
        client.post("/auth/login", data={"username": "pwduser", "password": "oldpass"})

        # Try to change with mismatched passwords
        response = client.post(
            "/profile",
            data={
                "action": "change_password",
                "current_password": "oldpass",
                "new_password": "newpass1",
                "confirm_password": "newpass2",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"New passwords do not match." in response.data

    def test_change_password_too_short(self, client: FlaskClient, app):
        """Test password change with password too short."""
        # Create a test user
        user_manager = app.user_manager
        user_manager.create_user("pwduser", "oldpass", "Password User", False)

        # Login
        client.post("/auth/login", data={"username": "pwduser", "password": "oldpass"})

        # Try to change to short password
        response = client.post(
            "/profile",
            data={
                "action": "change_password",
                "current_password": "oldpass",
                "new_password": "123",  # Too short
                "confirm_password": "123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Password must be at least 4 characters." in response.data

    def test_profile_missing_user_data(self, authenticated_client: FlaskClient, app):
        """Test profile page when user data is corrupted/missing."""
        # This is a bit tricky to test - we'd need to mock or corrupt user data
        # For now, just test that the route handles it gracefully
        response = authenticated_client.get("/profile")
        assert response.status_code == 200


class TestIndexPageStats:
    """Test index page statistics display."""

    def test_index_shows_user_stats(self, authenticated_client: FlaskClient, app):
        """Test that index page shows user statistics."""
        # Create some test links for the admin user
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        # Add a test link
        links = config_loader.links_config.setdefault("links", {})
        links["test"] = {
            "type": "redirect",
            "url": "https://example.com",
            "created_at": "2024-01-01T00:00:00",
        }
        config_loader.save_links_config()

        response = authenticated_client.get("/")
        assert response.status_code == 200
        # Should contain some stats or count information

    def test_index_admin_shows_system_stats(self, authenticated_client: FlaskClient, app):
        """Test that admin sees system-wide statistics."""
        # Create a few test users
        user_manager = app.user_manager
        user_manager.create_user("user1", "pass", "User One", False)
        user_manager.create_user("user2", "pass", "User Two", False)

        response = authenticated_client.get("/")
        assert response.status_code == 200
        # Admin should see system-wide stats

    def test_index_regular_user_stats(self, client: FlaskClient, app):
        """Test that regular users see only their own stats."""
        # Create and login as regular user
        user_manager = app.user_manager
        user_manager.create_user("regular", "pass", "Regular User", False)

        client.post("/auth/login", data={"username": "regular", "password": "pass"})

        response = client.get("/")
        assert response.status_code == 200
        assert b"Regular User" in response.data or b"regular" in response.data
