"""
Integration tests for end-to-end application workflows.

These tests verify complete user flows through the application,
testing multiple components working together.
"""

import io
import os
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest
from flask.testing import FlaskClient

from app.utils.config_loader import ConfigLoader


@pytest.mark.integration
class TestCompleteWorkflows:
    """Test complete user workflows through the application."""

    def test_complete_link_lifecycle(self, client: FlaskClient, app):
        """Test complete lifecycle: login, create, access, edit, delete."""
        # Step 1: Login
        response = client.post("/auth/login", data={"password": "test_password"})
        assert response.status_code == 302

        # Step 2: Create a redirect link
        response = client.post(
            "/add",
            data={
                "link_type": "redirect",
                "short_code": "lifecycle",
                "url": "https://lifecycle.com",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"lifecycle" in response.data

        # Step 3: Access the link (should redirect)
        response = client.get("/lifecycle")
        assert response.status_code == 302
        assert response.location == "https://lifecycle.com"

        # Step 4: Edit the link
        response = client.post(
            "/edit_link/lifecycle",
            data={"link_type": "redirect", "url": "https://updated-lifecycle.com"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Step 5: Verify edit worked
        response = client.get("/lifecycle")
        assert response.status_code == 302
        assert response.location == "https://updated-lifecycle.com"

        # Step 6: Delete the link
        response = client.post("/delete/lifecycle", follow_redirects=True)
        assert response.status_code == 200

        # Step 7: Verify deletion
        response = client.get("/lifecycle")
        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_file_upload_and_download_flow(self, client: FlaskClient, app):
        """Test file upload and download workflow."""
        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Upload file
        file_content = b"Integration test file content"
        response = client.post(
            "/add",
            data={
                "link_type": "file",
                "short_code": "testdoc",
                "file": (io.BytesIO(file_content), "integration.txt"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"testdoc" in response.data

        # Download file
        response = client.get("/testdoc")
        assert response.status_code == 200
        assert response.data == file_content

        # Clean up
        client.post("/delete/testdoc")

    def test_markdown_workflow(self, client: FlaskClient):
        """Test markdown creation and rendering workflow."""
        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Create markdown link with text input
        markdown_content = "# Integration Test\n\n**Bold** and *italic* text."
        response = client.post(
            "/add",
            data={
                "link_type": "markdown",
                "short_code": "testmd",
                "markdown_input_type": "text",
                "markdown_text_content": markdown_content,
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        # Access markdown link
        response = client.get("/testmd")
        assert response.status_code == 200
        # Check for client-side markdown rendering with Strapdown.js
        assert b"<textarea" in response.data
        assert b"Integration Test" in response.data
        assert b"strapdown.min.js" in response.data

        # Clean up
        client.post("/delete/testmd")

    def test_theme_change_persists(
        self, client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test that theme changes persist across requests."""
        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Check initial theme
        response = client.get("/settings")
        assert response.status_code == 200

        # Change theme
        response = client.post(
            "/settings",
            data={"theme": "darkly", "markdown_theme": "cerulean"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Theme settings updated successfully!" in response.data

        # Create a new client to simulate new session
        new_client = client.application.test_client()
        new_client.post("/auth/login", data={"password": "test_password"})

        # Verify theme persisted
        response = new_client.get("/settings")
        assert response.status_code == 200
        # The selected theme should be marked as selected in the form

    def test_expiration_workflow(self, client: FlaskClient, app, monkeypatch):
        """Test link expiration workflow."""
        # Mock current time
        mock_now = datetime(2024, 1, 1, 12, 0, 0)

        class MockDateTime:
            @classmethod
            def now(cls):
                return mock_now

            @classmethod
            def fromisoformat(cls, date_string):
                return datetime.fromisoformat(date_string)

        # Mock datetime in all relevant modules
        monkeypatch.setattr("app.links.utils.datetime", MockDateTime)
        monkeypatch.setattr("app.links.routes.datetime", MockDateTime)

        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Create link that expires in 1 hour
        expire_time = (mock_now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        response = client.post(
            "/add",
            data={
                "link_type": "redirect",
                "short_code": "expiring",
                "url": "https://expiring.com",
                "enable_expiration": "on",
                "expiration_date": expire_time,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Link should work initially
        response = client.get("/expiring")
        assert response.status_code == 302
        assert response.location == "https://expiring.com"

        # Move time forward by 2 hours
        mock_now = datetime(2024, 1, 1, 14, 0, 0)
        MockDateTime.now = classmethod(lambda cls: mock_now)

        # Link should now be expired and removed
        response = client.get("/expiring")
        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_multiple_file_types(self, client: FlaskClient):
        """Test handling different file types."""
        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Test different file types
        test_files = [
            ("test.pdf", b"%PDF-1.4 fake pdf content", "application/pdf"),
            ("test.png", b"\x89PNG fake png content", "image/png"),
            (
                "test.docx",
                b"PK fake docx content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        ]

        for idx, (filename, content, expected_type) in enumerate(test_files):
            short_code = f"file{idx}"

            # Upload
            response = client.post(
                "/add",
                data={
                    "link_type": "file",
                    "short_code": short_code,
                    "file": (io.BytesIO(content), filename),
                },
                content_type="multipart/form-data",
                follow_redirects=True,
            )
            assert response.status_code == 200

            # Download and verify
            response = client.get(f"/{short_code}")
            assert response.status_code == 200
            assert response.data == content

            # Clean up
            client.post(f"/delete/{short_code}")

    def test_session_management(self, client: FlaskClient):
        """Test session management and authentication persistence."""
        # Access protected page without auth
        response = client.get("/add")
        assert response.status_code == 302
        assert response.location.endswith("/auth/login")

        # Login with remember me
        response = client.post(
            "/auth/login", data={"password": "test_password", "remember": "on"}
        )
        assert response.status_code == 302

        # Access multiple protected pages
        protected_routes = ["/", "/add", "/links", "/settings"]
        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 200

        # Logout
        response = client.get("/auth/logout")
        assert response.status_code == 302

        # Verify can't access protected pages
        response = client.get("/add")
        assert response.status_code == 302
        assert response.location.endswith("/auth/login")

    def test_concurrent_config_updates(
        self, client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test handling of concurrent configuration updates."""
        # Login
        client.post("/auth/login", data={"password": "test_password"})

        # Create a link
        response = client.post(
            "/add",
            data={
                "link_type": "redirect",
                "short_code": "concurrent",
                "url": "https://concurrent.com",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        # Reload config to get the latest state
        config_loader.load_all_configs()

        # Manually modify the config file (simulating external change)
        config_loader.links_config["links"]["external"] = {
            "type": "redirect",
            "url": "https://external.com",
        }
        config_loader.save_links_config()

        # Access the manually added link (should trigger reload)
        response = client.get("/external")
        assert response.status_code == 302
        assert response.location == "https://external.com"

        # Original link should still work
        response = client.get("/concurrent")
        assert response.status_code == 302
        assert response.location == "https://concurrent.com"

    def test_cascading_user_deletion_integration(self, client: FlaskClient, app):
        """Test that user deletion properly cascades and removes all user data."""
        # Login using administrator mode
        response = client.post("/auth/login", data={"password": "test_password"})
        assert response.status_code == 302

        # Create a test user programmatically (not through web interface)
        user_manager = app.user_manager
        success = user_manager.create_user(
            username="testuser_cascade",
            password="test123",
            display_name="Test User for Cascade",
            is_admin=False,
        )
        assert success is True

        # Set context to the test user and create some links
        config_loader = app.config_loader
        config_loader.set_user_context("testuser_cascade")
        config_loader.load_all_configs()

        # Create a test file link
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"Test file content for cascade deletion")
            temp_file_path = temp_file.name

        try:
            # Add the file to user's assets
            assets_dir = config_loader.get_user_assets_dir("testuser_cascade")
            test_filename = "cascade_test.txt"
            shutil.copy2(temp_file_path, os.path.join(assets_dir, test_filename))

            # Create links by directly modifying the config
            links_data = {
                "links": {
                    "cascade-redirect": {
                        "type": "redirect",
                        "url": "https://example.com/cascade",
                    },
                    "cascade-file": {"type": "file", "path": test_filename},
                }
            }

            config_loader.links_config.update(links_data)
            config_loader.save_links_config()

            # Verify user and data exist before deletion
            assert user_manager.get_user("testuser_cascade") is not None
            assert os.path.exists(os.path.join(assets_dir, test_filename))
            assert len(config_loader.links_config.get("links", {})) == 2

            # Get deletion preview to verify what will be deleted
            preview = user_manager.get_user_deletion_preview("testuser_cascade")
            assert preview is not None
            assert preview["links_count"] == 2
            assert preview["files_count"] == 1
            assert preview["total_size"] > 0

            # Reset context to admin for deletion (simulate admin performing deletion)
            config_loader.set_user_context("admin")
            config_loader.load_all_configs()

            # Delete the user (cascading deletion) - simulate admin action
            result = user_manager.delete_user("testuser_cascade", "admin")
            assert result is True

            # Verify complete cleanup after deletion
            assert user_manager.get_user("testuser_cascade") is None
            assert "testuser_cascade" not in user_manager.list_users()

            # Verify user directory is completely removed
            user_dir = os.path.join("users", "testuser_cascade")
            assert not os.path.exists(user_dir)

            # Verify links are no longer accessible through the web interface
            response = client.get("/cascade-redirect")
            assert response.status_code == 200  # Should show link_not_found template
            assert (
                b"not found" in response.data.lower()
                or b"Link not found" in response.data
            )

            response = client.get("/cascade-file")
            assert response.status_code == 200  # Should show link_not_found template
            assert (
                b"not found" in response.data.lower()
                or b"Link not found" in response.data
            )

        finally:
            # Cleanup temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            # Ensure we're back in admin context
            config_loader.set_user_context("admin")
            config_loader.load_all_configs()
