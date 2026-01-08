"""
Utility functions for the links module.

This module provides helper functions for link management, including
functionality to check for and remove expired links with associated
file cleanup. Now supports multi-user functionality.
"""

import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.config_loader import ConfigLoader


def check_expired_links(config_loader: "ConfigLoader") -> None:
    """
    Check for and remove expired links for the current user.

    This function should be called periodically or before serving links.
    It examines the current user's links for expiration dates, removes
    expired ones, and cleans up associated files for file and markdown links.

    Args:
        config_loader: The configuration loader instance containing links config.
    """
    if not config_loader.current_user:
        return  # No user context set

    current_time = datetime.now()  # Uses server's local time
    links = config_loader.links_config.get("links", {})
    expired_links = []

    # Find all expired links for current user
    for short_code, link_data in links.items():
        expiration_date = link_data.get("expiration_date")
        if expiration_date:
            try:
                # Parse the datetime in server's local timezone
                exp_date = datetime.fromisoformat(expiration_date)
                if current_time > exp_date:
                    expired_links.append(short_code)
            except ValueError:
                # Invalid date format, skip this link
                continue

    # Remove expired links and clean up associated files
    for short_code in expired_links:
        link_data = links[short_code]

        # If it's a file link, delete the associated file
        if link_data.get("type") in ["file", "markdown", "html"]:
            filename = link_data.get("path")
            if filename:
                asset_folder = config_loader.get_user_assets_dir(
                    config_loader.current_user
                )
                filepath = os.path.join(asset_folder, filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"Deleted expired file: {filepath}")
                    except OSError as e:
                        print(f"Error deleting expired file {filepath}: {e}")

        # Remove the link from config data
        del links[short_code]
        print(
            f"Removed expired link: {short_code} (user: {config_loader.current_user})"
        )

    # Save the updated links config if any links were removed
    if expired_links:
        if config_loader.save_links_config(config_loader.current_user):
            print(
                f"Successfully removed {len(expired_links)} expired links for user {config_loader.current_user}"
            )
        else:
            print(
                f"Error saving changes after removing expired links for user {config_loader.current_user}"
            )


def check_all_users_expired_links(config_loader: "ConfigLoader", user_manager) -> None:
    """
    Check for and remove expired links across all users (admin function).

    This function examines all users' links for expiration dates and removes
    expired ones with associated file cleanup.

    Args:
        config_loader: The configuration loader instance.
        user_manager: The user manager instance.
    """
    current_time = datetime.now()
    total_expired = 0

    for username in user_manager.list_users():
        try:
            # Set context to each user
            original_user = config_loader.current_user
            config_loader.set_user_context(username)
            config_loader.load_all_configs()

            links = config_loader.links_config.get("links", {})
            expired_links = []

            # Find expired links for this user
            for short_code, link_data in links.items():
                expiration_date = link_data.get("expiration_date")
                if expiration_date:
                    try:
                        exp_date = datetime.fromisoformat(expiration_date)
                        if current_time > exp_date:
                            expired_links.append(short_code)
                    except ValueError:
                        continue

            # Remove expired links for this user
            for short_code in expired_links:
                link_data = links[short_code]

                # Delete associated file if exists
                if link_data.get("type") in ["file", "markdown", "html"]:
                    filename = link_data.get("path")
                    if filename:
                        asset_folder = config_loader.get_user_assets_dir(username)
                        filepath = os.path.join(asset_folder, filename)
                        if os.path.exists(filepath):
                            try:
                                os.remove(filepath)
                                print(f"Deleted expired file: {filepath}")
                            except OSError as e:
                                print(f"Error deleting expired file {filepath}: {e}")

                # Remove from config
                del links[short_code]
                print(f"Removed expired link: {short_code} (user: {username})")

            # Save if changes were made
            if expired_links:
                if config_loader.save_links_config(username):
                    total_expired += len(expired_links)
                else:
                    print(f"Error saving changes for user {username}")

            # Restore original user context
            config_loader.set_user_context(original_user)

        except Exception as e:
            print(f"Error processing expired links for user {username}: {e}")
            continue

    if total_expired > 0:
        print(f"Successfully removed {total_expired} expired links across all users")


def get_user_stats(config_loader: "ConfigLoader", username: str) -> dict:
    """
    Get statistics for a specific user.

    Args:
        config_loader: The configuration loader instance.
        username: Username to get stats for.

    Returns:
        Dictionary containing user statistics.
    """
    try:
        # Set context to the user
        original_user = config_loader.current_user
        config_loader.set_user_context(username)
        config_loader.load_all_configs()

        links = config_loader.links_config.get("links", {})

        # Count by type
        stats = {
            "total_links": len(links),
            "file_links": 0,
            "redirect_links": 0,
            "markdown_links": 0,
            "expired_links": 0,
            "total_files": 0,
            "total_file_size": 0,
        }

        current_time = datetime.now()
        asset_folder = config_loader.get_user_assets_dir(username)

        for link_data in links.values():
            link_type = link_data.get("type", "unknown")

            if link_type == "file":
                stats["file_links"] += 1
            elif link_type == "redirect":
                stats["redirect_links"] += 1
            elif link_type == "markdown":
                stats["markdown_links"] += 1

            # Check expiration
            expiration_date = link_data.get("expiration_date")
            if expiration_date:
                try:
                    exp_date = datetime.fromisoformat(expiration_date)
                    if current_time > exp_date:
                        stats["expired_links"] += 1
                except ValueError:
                    pass

        # Count files and calculate total size
        if os.path.exists(asset_folder):
            for file in os.listdir(asset_folder):
                file_path = os.path.join(asset_folder, file)
                if os.path.isfile(file_path):
                    stats["total_files"] += 1
                    stats["total_file_size"] += os.path.getsize(file_path)

        # Restore original context
        config_loader.set_user_context(original_user)

        return stats

    except Exception as e:
        print(f"Error getting stats for user {username}: {e}")
        return {
            "total_links": 0,
            "file_links": 0,
            "redirect_links": 0,
            "markdown_links": 0,
            "expired_links": 0,
            "total_files": 0,
            "total_file_size": 0,
        }


def validate_short_code(short_code: str) -> tuple[bool, str]:
    """
    Validate a short code for use in URLs.

    Args:
        short_code: The short code to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not short_code:
        return False, "Short code cannot be empty"

    if len(short_code) < 1:
        return False, "Short code must be at least 1 character"

    if len(short_code) > 50:
        return False, "Short code must be 50 characters or less"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not all(c.isalnum() or c in "-_" for c in short_code):
        return (
            False,
            "Short code can only contain letters, numbers, hyphens, and underscores",
        )

    # Check for reserved words/paths that conflict with built-in routes
    reserved_words = {
        # Main routes
        "settings",
        "users",
        "profile",
        # Links routes
        "add",
        "links",
        "edit_link",
        "delete_link",
        "delete",
        # Auth routes (these are prefixed with /auth/ but we should still reserve them)
        "auth",
        "login",
        "logout",
        "register",
        "switch-user",
        "switch-back",
        # System reserved
        "admin",
        "api",
        "static",
        "assets",
        # Common route patterns that could cause conflicts
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
        "configuration",
        "system",
        "health",
        "status",
        "favicon.ico",
        "robots.txt",
        "sitemap.xml",
    }

    if short_code.lower() in reserved_words:
        return False, f"'{short_code}' is a reserved word and cannot be used"

    return True, ""


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted size string.
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)

    for i, unit in enumerate(size_names):
        if size < 1024.0 or i == len(size_names) - 1:
            if i == 0:
                return f"{int(size)} {unit}"
            else:
                return f"{size:.1f} {unit}"
        size /= 1024.0

    return f"{size:.1f} TB"
