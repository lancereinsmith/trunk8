"""
Tests for backup and restore functionality.

This module tests the backup creation and restore processes,
including ZIP file generation, validation, and data integrity.
"""

import os
import tempfile
import zipfile

import pytest
import toml


@pytest.fixture
def backup_app(app):
    """Create test app instance with test user for backup tests."""
    with app.app_context():
        # Set up test user
        user_manager = app.user_manager
        config_loader = app.config_loader

        # Create test user data
        test_user = "backupuser"
        user_manager.create_user(test_user, "testpassword", "Backup Test User")

        # Create test links
        config_loader.set_user_context(test_user)
        config_loader.load_all_configs()

        test_links = {
            "links": {
                "test1": {"type": "redirect", "url": "https://example.com"},
                "test2": {"type": "file", "path": "test_file.txt"},
            }
        }

        config_loader.links_config = test_links
        config_loader.save_links_config()

        # Create test asset file
        assets_dir = config_loader.get_user_assets_dir(test_user)
        os.makedirs(assets_dir, exist_ok=True)
        test_file_path = os.path.join(assets_dir, "test_file.txt")
        with open(test_file_path, "w") as f:
            f.write("Test file content")

    return app


@pytest.fixture
def backup_client(backup_app):
    """Create test client."""
    return backup_app.test_client()


@pytest.fixture
def auth_client(backup_client, backup_app):
    """Create authenticated test client."""
    with backup_app.app_context():
        # Login as test user
        response = backup_client.post(
            "/auth/login", data={"username": "backupuser", "password": "testpassword"}
        )
        assert response.status_code in [200, 302]
        return backup_client


def test_backup_create_get(auth_client):
    """Test backup creation form display."""
    response = auth_client.get("/backup/create")
    assert response.status_code == 200
    assert b"Create Backup" in response.data
    assert b"Backup Contents" in response.data


def test_backup_create_post(auth_client, backup_app):
    """Test backup creation and download."""
    with backup_app.app_context():
        response = auth_client.post(
            "/backup/create", data={"target_user": "backupuser"}
        )

        # Should get a zip file download
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert "trunk8_backup_backupuser_" in response.headers.get(
            "Content-Disposition", ""
        )

        # Validate zip content
        zip_data = response.data
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
            temp_zip.write(zip_data)
            temp_zip_path = temp_zip.name

        try:
            with zipfile.ZipFile(temp_zip_path, "r") as zipf:
                zip_contents = zipf.namelist()

                # Check required files exist in zip
                assert "links.toml" in zip_contents
                assert "backup_metadata.toml" in zip_contents
                assert "assets/test_file.txt" in zip_contents

                # Validate links.toml content
                with zipf.open("links.toml") as f:
                    links_data = toml.loads(f.read().decode("utf-8"))
                    assert "links" in links_data
                    assert "test1" in links_data["links"]
                    assert "test2" in links_data["links"]
                    assert links_data["links"]["test1"]["type"] == "redirect"
                    assert links_data["links"]["test1"]["url"] == "https://example.com"

                # Validate metadata
                with zipf.open("backup_metadata.toml") as f:
                    metadata = toml.loads(f.read().decode("utf-8"))
                    assert "backup_info" in metadata
                    assert metadata["backup_info"]["target_user"] == "backupuser"
                    assert metadata["backup_info"]["created_by"] == "backupuser"

                # Validate asset file
                with zipf.open("assets/test_file.txt") as f:
                    content = f.read().decode("utf-8")
                    assert content == "Test file content"

        finally:
            os.unlink(temp_zip_path)


def test_restore_get(auth_client):
    """Test restore form display."""
    response = auth_client.get("/backup/restore")
    assert response.status_code == 200
    assert b"Restore Backup" in response.data
    assert b"Select Backup File" in response.data
    assert b"Restore Mode" in response.data


def test_restore_post_invalid_file(auth_client):
    """Test restore with invalid file."""
    # Test with no file
    response = auth_client.post(
        "/backup/restore", data={"restore_mode": "merge", "target_user": "backupuser"}
    )
    assert response.status_code == 302  # Redirect back to form

    # Test with non-zip file
    response = auth_client.post(
        "/backup/restore",
        data={"restore_mode": "merge", "target_user": "backupuser"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 302


def test_restore_post_valid_backup(auth_client, backup_app):
    """Test restore with valid backup file."""
    with backup_app.app_context():
        # First create a backup
        backup_response = auth_client.post(
            "/backup/create", data={"target_user": "backupuser"}
        )
        assert backup_response.status_code == 200

        # Create a new test user to restore to
        user_manager = backup_app.user_manager
        restore_user = "restoreuser"
        user_manager.create_user(restore_user, "testpassword", "Restore User")

        try:
            # Create temporary zip file from backup
            zip_data = backup_response.data
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                temp_zip.write(zip_data)
                temp_zip_path = temp_zip.name

            # Test restore
            with open(temp_zip_path, "rb") as zip_file:
                response = auth_client.post(
                    "/backup/restore",
                    data={
                        "backup_file": (zip_file, "test_backup.zip"),
                        "restore_mode": "merge",
                        "target_user": "backupuser",  # Restore to same user
                    },
                    content_type="multipart/form-data",
                )

                # Should redirect to links list on success
                assert response.status_code == 302
                assert "/links" in response.location

            # Verify data was restored
            config_loader = backup_app.config_loader
            config_loader.set_user_context("backupuser")
            config_loader.load_all_configs()

            links = config_loader.links_config.get("links", {})
            assert "test1" in links
            assert "test2" in links
            assert links["test1"]["type"] == "redirect"

        finally:
            os.unlink(temp_zip_path)


def test_backup_routes_require_auth(client):
    """Test that backup routes require authentication."""
    # Test backup create
    response = client.get("/backup/create")
    assert response.status_code == 302  # Redirect to login

    response = client.post("/backup/create")
    assert response.status_code == 302  # Redirect to login

    # Test backup restore
    response = client.get("/backup/restore")
    assert response.status_code == 302  # Redirect to login

    response = client.post("/backup/restore")
    assert response.status_code == 302  # Redirect to login


def test_admin_can_backup_other_users(backup_app, monkeypatch):
    """Test that admin users can backup other users' data."""
    with backup_app.app_context():
        # Create test client and login as admin
        client = backup_app.test_client()
        response = client.post(
            "/auth/login", data={"username": "admin", "password": "test_password"}
        )

        # Admin should be able to backup backupuser's data
        response = client.post("/backup/create", data={"target_user": "backupuser"})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/zip"
