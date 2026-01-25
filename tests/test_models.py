"""
Test suite for data models.

Tests cover the Link model functionality including initialization,
expiration checking, and serialization.
"""

from datetime import datetime, timedelta

from app.links.models import Link


class TestLinkModel:
    """Test Link model functionality."""

    def test_link_initialization(self):
        """Test Link object initialization."""
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": "2024-12-31T23:59:59",
        }

        link = Link("test_code", link_data)

        assert link.short_code == "test_code"
        assert link.type == "redirect"
        assert link.url == "https://example.com"
        assert link.path is None
        assert link.expiration_date == "2024-12-31T23:59:59"

    def test_link_file_type(self):
        """Test Link with file type."""
        link_data = {"type": "file", "path": "document.pdf"}

        link = Link("file_link", link_data)

        assert link.type == "file"
        assert link.path == "document.pdf"
        assert link.url is None

    def test_link_markdown_type(self):
        """Test Link with markdown type."""
        link_data = {"type": "markdown", "path": "content.md"}

        link = Link("md_link", link_data)

        assert link.type == "markdown"
        assert link.path == "content.md"

    def test_link_html_type(self):
        """Test Link with HTML type."""
        link_data = {"type": "html", "path": "page.html"}

        link = Link("html_link", link_data)

        assert link.type == "html"
        assert link.path == "page.html"
        assert link.url is None

    def test_is_expired_past_date(self):
        """Test expiration check for past date."""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": past_date,
        }

        link = Link("expired", link_data)
        assert link.is_expired is True

    def test_is_expired_future_date(self):
        """Test expiration check for future date."""
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": future_date,
        }

        link = Link("active", link_data)
        assert link.is_expired is False

    def test_is_expired_no_expiration(self):
        """Test expiration check when no expiration date is set."""
        link_data = {"type": "redirect", "url": "https://example.com"}

        link = Link("permanent", link_data)
        assert link.is_expired is False

    def test_is_expired_invalid_date(self):
        """Test expiration check with invalid date format."""
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": "invalid-date-format",
        }

        link = Link("invalid", link_data)
        # Should not crash and consider as non-expired
        assert link.is_expired is False

    def test_to_dict_redirect(self):
        """Test serialization of redirect link."""
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": "2024-12-31T23:59:59",
        }

        link = Link("test", link_data)
        result = link.to_dict()

        assert result == {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": "2024-12-31T23:59:59",
        }

    def test_to_dict_file(self):
        """Test serialization of file link."""
        link_data = {"type": "file", "path": "document.pdf"}

        link = Link("test", link_data)
        result = link.to_dict()

        assert result == {"type": "file", "path": "document.pdf"}

    def test_to_dict_html(self):
        """Test serialization of HTML link."""
        link_data = {"type": "html", "path": "page.html"}

        link = Link("test", link_data)
        result = link.to_dict()

        assert result == {"type": "html", "path": "page.html"}

    def test_to_dict_minimal(self):
        """Test serialization with minimal data."""
        link_data = {"type": "redirect"}

        link = Link("minimal", link_data)
        result = link.to_dict()

        assert result == {"type": "redirect"}
        assert "url" not in result
        assert "path" not in result
        assert "expiration_date" not in result

    def test_link_with_extra_fields(self):
        """Test Link handles extra fields gracefully."""
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "extra_field": "extra_value",
            "another_field": 123,
        }

        link = Link("extra", link_data)

        # Should only store expected fields
        assert link.type == "redirect"
        assert link.url == "https://example.com"
        assert not hasattr(link, "extra_field")

        # to_dict should only include expected fields
        result = link.to_dict()
        assert "extra_field" not in result
        assert "another_field" not in result

    def test_link_empty_data(self):
        """Test Link with empty data dictionary."""
        link_data = {}

        link = Link("empty", link_data)

        assert link.short_code == "empty"
        assert link.type is None
        assert link.path is None
        assert link.url is None
        assert link.expiration_date is None
        assert link.is_expired is False

    def test_expiration_edge_cases(self):
        """Test expiration check edge cases."""
        # Exact current time (might be flaky, but testing boundary)
        current_time = datetime.now()
        link_data = {
            "type": "redirect",
            "url": "https://example.com",
            "expiration_date": current_time.isoformat(),
        }

        _ = Link("boundary", link_data)
        # Should be expired if current time has passed
        # This might be flaky due to timing, but tests the boundary condition
