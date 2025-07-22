"""
Test suite for link management functionality.

Tests cover link creation, retrieval, editing, deletion, and expiration handling
for all link types (file, redirect, markdown, html).
"""

import io
import os
from datetime import datetime, timedelta

from flask.testing import FlaskClient

from app.utils.config_loader import ConfigLoader


class TestLinkCreation:
    """Test link creation functionality."""

    def test_add_link_page_requires_auth(self, client: FlaskClient):
        """Test that add link page requires authentication."""
        response = client.get("/add")
        assert response.status_code == 302
        assert response.location.endswith("/auth/login")

    def test_add_link_page_authenticated(self, authenticated_client: FlaskClient):
        """Test accessing add link page when authenticated."""
        response = authenticated_client.get("/add")
        assert response.status_code == 200
        assert b"Add Link" in response.data

    def test_create_file_link(self, authenticated_client: FlaskClient, app):
        """Test creating a file link."""
        # Create a test file
        data = {
            "link_type": "file",
            "short_code": "testfile",
            "file": (io.BytesIO(b"Test file content"), "test.txt"),
        }

        response = authenticated_client.post(
            "/add", data=data, content_type="multipart/form-data", follow_redirects=True
        )

        assert response.status_code == 200
        assert b"testfile" in response.data

        # Verify file was saved (files are renamed to UUID for security)
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        asset_folder = config_loader.get_user_assets_dir()
        files = os.listdir(asset_folder)
        # Check that a .txt file with UUID pattern exists
        import re

        uuid_pattern = (
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.txt"
        )
        assert any(re.match(uuid_pattern, f) for f in files)

    def test_create_redirect_link(
        self, authenticated_client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test creating a redirect link."""
        data = {
            "link_type": "redirect",
            "short_code": "testredirect",
            "url": "https://example.com",
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b"testredirect" in response.data

        # Verify link was saved
        config_loader.load_all_configs()
        links = config_loader.links_config.get("links", {})
        assert "testredirect" in links
        assert links["testredirect"]["url"] == "https://example.com"

    def test_create_markdown_link_file(self, authenticated_client: FlaskClient, app):
        """Test creating a markdown link with file upload."""
        data = {
            "link_type": "markdown",
            "short_code": "testmd",
            "markdown_input_type": "file",
            "markdown_file": (io.BytesIO(b"# Test\n\nMarkdown content"), "test.md"),
        }

        response = authenticated_client.post(
            "/add", data=data, content_type="multipart/form-data", follow_redirects=True
        )

        assert response.status_code == 200
        assert b"testmd" in response.data

    def test_create_markdown_link_text(
        self, authenticated_client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test creating a markdown link with text input."""
        data = {
            "link_type": "markdown",
            "short_code": "testmdtext",
            "markdown_input_type": "text",
            "markdown_text_content": "# Test Header\n\nThis is test content",
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b"testmdtext" in response.data

    def test_create_html_link_file(self, authenticated_client: FlaskClient, app):
        """Test creating an HTML link with file upload."""
        html_content = b"<html><head><title>Test</title></head><body><h1>Test HTML</h1></body></html>"
        data = {
            "link_type": "html",
            "short_code": "testhtml",
            "html_input_type": "file",
            "html_file": (io.BytesIO(html_content), "test.html"),
        }

        response = authenticated_client.post(
            "/add", data=data, content_type="multipart/form-data", follow_redirects=True
        )

        assert response.status_code == 200
        assert b"testhtml" in response.data

        # Verify file was saved with UUID filename
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        asset_folder = config_loader.get_user_assets_dir()
        files = os.listdir(asset_folder)

        import re

        uuid_pattern = (
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.html"
        )
        html_files = [f for f in files if re.match(uuid_pattern, f)]
        assert len(html_files) > 0

        # Verify file content
        with open(os.path.join(asset_folder, html_files[0]), "r") as f:
            saved_content = f.read()
            assert "Test HTML" in saved_content

        # Verify link metadata
        config_loader.load_all_configs()
        links = config_loader.links_config.get("links", {})
        assert "testhtml" in links
        assert links["testhtml"]["type"] == "html"
        assert "original_filename" in links["testhtml"]
        assert links["testhtml"]["original_filename"] == "test.html"

    def test_create_html_link_text(
        self, authenticated_client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test creating an HTML link with text input."""
        html_content = "<html><head><title>Text Test</title></head><body><h1>HTML from Text</h1></body></html>"
        data = {
            "link_type": "html",
            "short_code": "testhtmltext",
            "html_input_type": "text",
            "html_text_content": html_content,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)

        assert response.status_code == 200
        assert b"testhtmltext" in response.data

        # Verify link was saved
        config_loader.load_all_configs()
        links = config_loader.links_config.get("links", {})
        assert "testhtmltext" in links
        assert links["testhtmltext"]["type"] == "html"
        assert "path" in links["testhtmltext"]

    def test_create_html_link_no_file(self, authenticated_client: FlaskClient):
        """Test creating HTML link without uploading file."""
        data = {
            "link_type": "html",
            "short_code": "nofile",
            "html_input_type": "file",
        }

        response = authenticated_client.post("/add", data=data)

        assert response.status_code == 200
        assert b"No HTML file uploaded" in response.data

    def test_create_html_link_no_content(self, authenticated_client: FlaskClient):
        """Test creating HTML link without text content."""
        data = {
            "link_type": "html",
            "short_code": "nocontent",
            "html_input_type": "text",
            "html_text_content": "",
        }

        response = authenticated_client.post("/add", data=data)

        assert response.status_code == 200
        assert b"No HTML content provided" in response.data

    def test_create_link_with_expiration(
        self, authenticated_client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test creating a link with expiration date."""
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M")

        data = {
            "link_type": "redirect",
            "short_code": "expiring",
            "url": "https://example.com",
            "enable_expiration": "on",
            "expiration_date": future_date,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)

        assert response.status_code == 200

        # Verify expiration was saved
        config_loader.load_all_configs()
        links = config_loader.links_config.get("links", {})
        assert "expiring" in links
        assert "expiration_date" in links["expiring"]

    def test_create_link_auto_generated_code(
        self, authenticated_client: FlaskClient, config_loader: ConfigLoader
    ):
        """Test creating a link without specifying short code."""
        data = {"link_type": "redirect", "url": "https://auto-generated.com"}

        response = authenticated_client.post("/add", data=data, follow_redirects=True)

        assert response.status_code == 200

        # Verify a link was created
        config_loader.load_all_configs()
        links = config_loader.links_config.get("links", {})
        assert len(links) > 0
        assert any(
            link["url"] == "https://auto-generated.com" for link in links.values()
        )

    def test_create_duplicate_short_code(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test creating a link with duplicate short code."""
        data = {
            "link_type": "redirect",
            "short_code": "test_redirect",  # Already exists
            "url": "https://duplicate.com",
        }

        response = authenticated_client.post("/add", data=data)

        assert response.status_code == 200
        assert b"already exists" in response.data

    def test_create_file_link_no_file(self, authenticated_client: FlaskClient):
        """Test creating file link without uploading file."""
        data = {"link_type": "file", "short_code": "nofile"}

        response = authenticated_client.post("/add", data=data)

        assert response.status_code == 200
        assert b"No file uploaded" in response.data

    def test_create_redirect_link_no_url(self, authenticated_client: FlaskClient):
        """Test creating redirect link without URL."""
        data = {"link_type": "redirect", "short_code": "nourl"}

        response = authenticated_client.post("/add", data=data)

        assert response.status_code == 200
        assert b"URL is required" in response.data


class TestLinkRetrieval:
    """Test link retrieval and serving functionality."""

    def test_handle_file_link(self, client: FlaskClient, populated_links: ConfigLoader):
        """Test serving a file link."""
        response = client.get("/test_file")

        assert response.status_code == 200
        assert response.data == b"This is a test file."

    def test_handle_redirect_link(
        self, client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test handling redirect link."""
        response = client.get("/test_redirect")

        assert response.status_code == 302
        assert response.location == "https://example.com"

    def test_handle_markdown_link(
        self, client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test rendering markdown link."""
        response = client.get("/test_markdown")

        assert response.status_code == 200
        # Check for client-side markdown rendering with Strapdown.js
        assert b"Test Markdown" in response.data
        assert b"<textarea" in response.data
        assert b"strapdown.min.js" in response.data

    def test_handle_html_link(self, client: FlaskClient, populated_links: ConfigLoader):
        """Test rendering HTML link."""
        response = client.get("/test_html")

        assert response.status_code == 200
        # Check for HTML rendering template
        assert b"Test HTML Page" in response.data
        assert b"<html>" in response.data or b"<!DOCTYPE html>" in response.data
        # Verify it uses the html_render.html template structure
        assert (
            b".navbar" in response.data and b"display: none !important" in response.data
        )

    def test_handle_html_link_missing_file(self, client: FlaskClient, app):
        """Test handling HTML link with missing file."""
        # Create an HTML link with non-existent file
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        links = config_loader.links_config.setdefault("links", {})
        links["missing_html"] = {
            "type": "html",
            "path": "nonexistent.html",
        }
        config_loader.save_links_config()

        response = client.get("/missing_html")

        assert response.status_code == 200
        assert b"HTML file not found" in response.data

    def test_handle_nonexistent_link(self, client: FlaskClient):
        """Test accessing non-existent link."""
        response = client.get("/nonexistent")

        assert response.status_code == 200
        assert (
            b"link_not_found.html" in response.data
            or b"not found" in response.data.lower()
        )

    def test_handle_expired_link(
        self, client: FlaskClient, populated_links: ConfigLoader, app
    ):
        """Test accessing expired link."""
        # Manually trigger expiration check to ensure expired links are removed
        from app.links.utils import check_expired_links

        # Check and remove expired links before accessing
        check_expired_links(populated_links)

        # The expired_link should now be gone
        response = client.get("/expired_link")

        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_handle_future_link(
        self, client: FlaskClient, populated_links: ConfigLoader, mock_datetime
    ):
        """Test accessing link with future expiration."""
        response = client.get("/future_link")

        assert response.status_code == 302
        assert response.location == "https://future.com"


class TestLinkManagement:
    """Test link listing, editing, and deletion."""

    def test_list_links_requires_auth(self, client: FlaskClient):
        """Test that links list requires authentication."""
        response = client.get("/links")
        assert response.status_code == 302
        assert response.location.endswith("/auth/login")

    def test_list_links_authenticated(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test listing links when authenticated."""
        response = authenticated_client.get("/links")

        assert response.status_code == 200
        assert b"test_file" in response.data
        assert b"test_redirect" in response.data
        assert b"test_markdown" in response.data

    def test_delete_file_link(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader, app
    ):
        """Test deleting a file link."""
        # Verify file exists in admin user's asset directory
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        asset_folder = config_loader.get_user_assets_dir()
        test_file_path = os.path.join(asset_folder, "test.txt")
        assert os.path.exists(test_file_path)

        response = authenticated_client.post("/delete/test_file", follow_redirects=True)

        assert response.status_code == 200

        # Verify link and file were deleted
        populated_links.load_all_configs()
        links = populated_links.links_config.get("links", {})
        assert "test_file" not in links
        assert not os.path.exists(test_file_path)

    def test_delete_redirect_link(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test deleting a redirect link."""
        response = authenticated_client.post(
            "/delete/test_redirect", follow_redirects=True
        )

        assert response.status_code == 200

        # Verify link was deleted
        populated_links.load_all_configs()
        links = populated_links.links_config.get("links", {})
        assert "test_redirect" not in links

    def test_delete_html_link(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader, app
    ):
        """Test deleting an HTML link."""
        # Verify HTML file exists in admin user's asset directory
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        asset_folder = config_loader.get_user_assets_dir()
        html_file_path = os.path.join(asset_folder, "test.html")
        assert os.path.exists(html_file_path)

        response = authenticated_client.post("/delete/test_html", follow_redirects=True)

        assert response.status_code == 200

        # Verify link and file were deleted
        populated_links.load_all_configs()
        links = populated_links.links_config.get("links", {})
        assert "test_html" not in links
        assert not os.path.exists(html_file_path)

    def test_delete_nonexistent_link(self, authenticated_client: FlaskClient):
        """Test deleting non-existent link."""
        response = authenticated_client.post(
            "/delete/nonexistent", follow_redirects=True
        )

        assert response.status_code == 200
        assert b"not found" in response.data.lower()

    def test_edit_link_page(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test accessing edit link page."""
        response = authenticated_client.get("/edit_link/test_redirect")

        assert response.status_code == 200
        assert b"Edit Link" in response.data
        assert b"https://example.com" in response.data

    def test_edit_html_link_page(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test accessing edit page for HTML link."""
        response = authenticated_client.get("/edit_link/test_html")

        assert response.status_code == 200
        assert b"Edit Link" in response.data
        # Should show HTML content or indicate it's an HTML link

    def test_edit_redirect_link(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test editing a redirect link."""
        data = {"link_type": "redirect", "url": "https://updated.com"}

        response = authenticated_client.post(
            "/edit_link/test_redirect", data=data, follow_redirects=True
        )

        assert response.status_code == 200

        # Verify link was updated
        populated_links.load_all_configs()
        links = populated_links.links_config.get("links", {})
        assert links["test_redirect"]["url"] == "https://updated.com"

    def test_edit_html_link_text(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader, app
    ):
        """Test editing an HTML link with text content."""
        new_html_content = "<html><head><title>Updated</title></head><body><h1>Updated HTML</h1></body></html>"
        data = {
            "link_type": "html",
            "html_input_type": "text",
            "html_text_content": new_html_content,
        }

        response = authenticated_client.post(
            "/edit_link/test_html", data=data, follow_redirects=True
        )

        assert response.status_code == 200

        # Verify content was updated
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        links = config_loader.links_config.get("links", {})
        html_path = links["test_html"]["path"]

        asset_folder = config_loader.get_user_assets_dir()
        with open(os.path.join(asset_folder, html_path), "r") as f:
            saved_content = f.read()
            assert "Updated HTML" in saved_content

    def test_edit_html_link_file_upload(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader, app
    ):
        """Test editing an HTML link with file upload."""
        new_html_content = b"<html><head><title>New Upload</title></head><body><h1>New Upload HTML</h1></body></html>"
        data = {
            "link_type": "html",
            "html_input_type": "file",
            "html_file": (io.BytesIO(new_html_content), "updated.html"),
        }

        response = authenticated_client.post(
            "/edit_link/test_html",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert response.status_code == 200

        # Verify content was updated
        config_loader = app.config_loader
        config_loader.set_user_context("admin")
        config_loader.load_all_configs()

        links = config_loader.links_config.get("links", {})
        html_path = links["test_html"]["path"]

        asset_folder = config_loader.get_user_assets_dir()
        with open(os.path.join(asset_folder, html_path), "r") as f:
            saved_content = f.read()
            assert "New Upload HTML" in saved_content

    def test_edit_link_add_expiration(
        self, authenticated_client: FlaskClient, populated_links: ConfigLoader
    ):
        """Test adding expiration to existing link."""
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")

        data = {
            "link_type": "redirect",
            "url": "https://example.com",
            "enable_expiration": "on",
            "expiration_date": future_date,
        }

        response = authenticated_client.post(
            "/edit_link/test_redirect", data=data, follow_redirects=True
        )

        assert response.status_code == 200

        # Verify expiration was added
        populated_links.load_all_configs()
        links = populated_links.links_config.get("links", {})
        assert "expiration_date" in links["test_redirect"]

    def test_edit_nonexistent_link(self, authenticated_client: FlaskClient):
        """Test editing non-existent link."""
        response = authenticated_client.get("/edit_link/nonexistent")

        assert response.status_code == 302
        assert response.location.endswith("/links")


class TestHTMLLinkSpecialCases:
    """Test special cases and edge cases for HTML links."""

    def test_html_link_with_javascript(
        self, authenticated_client: FlaskClient, client: FlaskClient
    ):
        """Test HTML link containing JavaScript."""
        html_content = """
        <html>
        <head><title>JS Test</title></head>
        <body>
            <h1 id="header">Original</h1>
            <script>
                document.getElementById('header').innerHTML = 'Modified by JS';
            </script>
        </body>
        </html>
        """
        data = {
            "link_type": "html",
            "short_code": "jstest",
            "html_input_type": "text",
            "html_text_content": html_content,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Access the HTML link
        response = client.get("/jstest")
        assert response.status_code == 200
        assert b"<script>" in response.data
        assert b"Modified by JS" in response.data

    def test_html_link_with_css(
        self, authenticated_client: FlaskClient, client: FlaskClient
    ):
        """Test HTML link containing CSS styles."""
        html_content = """
        <html>
        <head>
            <title>CSS Test</title>
            <style>
                .red-text { color: red; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1 class="red-text">Styled Content</h1>
        </body>
        </html>
        """
        data = {
            "link_type": "html",
            "short_code": "csstest",
            "html_input_type": "text",
            "html_text_content": html_content,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Access the HTML link
        response = client.get("/csstest")
        assert response.status_code == 200
        assert b"<style>" in response.data
        assert b"red-text" in response.data
        assert b"Styled Content" in response.data

    def test_html_link_with_expiration(
        self, authenticated_client: FlaskClient, client: FlaskClient
    ):
        """Test HTML link with expiration date."""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")

        html_content = "<html><body><h1>Expiring HTML</h1></body></html>"
        data = {
            "link_type": "html",
            "short_code": "expiringhtml",
            "html_input_type": "text",
            "html_text_content": html_content,
            "enable_expiration": "on",
            "expiration_date": future_date,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Should be accessible before expiration
        response = client.get("/expiringhtml")
        assert response.status_code == 200
        assert b"Expiring HTML" in response.data

    def test_html_link_special_characters(
        self, authenticated_client: FlaskClient, client: FlaskClient
    ):
        """Test HTML link with special characters and unicode."""
        html_content = """
        <html>
        <head><title>Special Characters</title></head>
        <body>
            <h1>Special Characters Test</h1>
            <p>Unicode: ñáéíóú 中文 🚀</p>
            <p>HTML entities: &lt; &gt; &amp; &quot;</p>
        </body>
        </html>
        """
        data = {
            "link_type": "html",
            "short_code": "specialchars",
            "html_input_type": "text",
            "html_text_content": html_content,
        }

        response = authenticated_client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Access the HTML link
        response = client.get("/specialchars")
        assert response.status_code == 200
        assert "ñáéíóú".encode("utf-8") in response.data
        assert "&lt;".encode("utf-8") in response.data


class TestLinkExpiration:
    """Test link expiration functionality."""

    def test_expired_links_cleanup(
        self, app, populated_links: ConfigLoader, mock_datetime
    ):
        """Test that expired links are cleaned up."""
        from app.links.utils import check_expired_links

        # Initially should have expired_link
        links = populated_links.links_config.get("links", {})
        assert "expired_link" in links

        # Run cleanup
        check_expired_links(populated_links)

        # Verify expired link was removed
        links = populated_links.links_config.get("links", {})
        assert "expired_link" not in links
        assert "future_link" in links  # Future link should remain

    def test_link_model_expiration_check(self):
        """Test Link model expiration checking."""
        from app.links.models import Link

        # Test expired link
        expired_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": (datetime.now() - timedelta(days=1)).isoformat(),
        }
        expired_link = Link("expired", expired_data)
        assert expired_link.is_expired is True

        # Test future link
        future_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": (datetime.now() + timedelta(days=1)).isoformat(),
        }
        future_link = Link("future", future_data)
        assert future_link.is_expired is False

        # Test no expiration
        no_exp_data = {"type": "redirect", "url": "https://example.com"}
        no_exp_link = Link("noexp", no_exp_data)
        assert no_exp_link.is_expired is False
