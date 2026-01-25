# Links data models and utilities
# This module can be expanded with more sophisticated data models in the future

from datetime import datetime
from typing import Any


class Link:
    """
    Represents a link in the system.

    This class encapsulates all data and behavior for a shortened link,
    including validation, expiration checking, and serialization.

    Attributes:
        short_code (str): The unique identifier for this link.
        type (Optional[str]): The type of link (file, redirect, markdown).
        path (Optional[str]): File path for file/markdown links.
        url (Optional[str]): Target URL for redirect links.
        expiration_date (Optional[str]): ISO format expiration date string.
    """

    def __init__(self, short_code: str, link_data: dict[str, Any]) -> None:
        """
        Initialize a Link instance.

        Args:
            short_code: Unique identifier for the link.
            link_data: Dictionary containing link configuration data.
        """
        self.short_code = short_code
        self.type = link_data.get("type")
        self.path = link_data.get("path")
        self.url = link_data.get("url")
        self.expiration_date = link_data.get("expiration_date")

    @property
    def is_expired(self) -> bool:
        """
        Check if the link has expired.

        Compares the current datetime with the link's expiration date.

        Returns:
            bool: True if the link has expired, False otherwise.
                 Returns False if no expiration date is set or if there's
                 an error parsing the expiration date.
        """
        if not self.expiration_date:
            return False

        try:
            exp_date = datetime.fromisoformat(self.expiration_date)
            return datetime.now() > exp_date
        except ValueError:
            # Invalid date format, consider it non-expired to avoid data loss
            return False

    def to_dict(self) -> dict[str, Any]:
        """
        Convert link to dictionary format for saving.

        Creates a dictionary representation suitable for serialization
        to TOML or other configuration formats.

        Returns:
            Dict[str, Any]: Dictionary containing all non-None link attributes.
        """
        data: dict[str, Any] = {"type": self.type}

        if self.path:
            data["path"] = self.path
        if self.url:
            data["url"] = self.url
        if self.expiration_date:
            data["expiration_date"] = self.expiration_date

        return data
