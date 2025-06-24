"""
Main routes for the Trunk8 application.

This module handles the primary application routes including the home page,
settings management functionality, and user management for multi-user support.
"""

from typing import Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ..auth.decorators import (
    admin_required,
    get_current_user,
    get_display_name,
    is_admin,
    login_required,
)

# Create blueprint
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index() -> str:
    """
    Render the welcome page.

    Displays the main dashboard/welcome page for authenticated users.
    Shows user-specific information and links.

    Returns:
        str: Rendered welcome template.
    """
    current_user = get_current_user()
    config_loader = current_app.config_loader

    # Get user's link count
    link_count = 0
    if current_user:
        config_loader.set_user_context(current_user)
        config_loader.load_all_configs()
        link_count = len(config_loader.links_config.get("links", {}))

    # For admin, show total system stats
    total_users = 0
    total_links = 0
    if is_admin():
        user_manager = current_app.user_manager
        total_users = len(user_manager.list_users())

        # Get all users' link counts
        all_user_links = config_loader.get_all_user_links(get_current_user())
        total_links = sum(len(links) for links in all_user_links.values())

    return render_template(
        "index.html",
        current_user=current_user,
        display_name=get_display_name(),
        link_count=link_count,
        total_users=total_users,
        total_links=total_links,
        is_admin=is_admin(),
    )


@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> Union[str, Response]:
    """
    Handle settings page for per-user theme configuration.

    GET: Display the settings form with current theme selections.
    POST: Process theme updates and save to user-specific configuration.

    Returns:
        Union[str, Response]: Either rendered settings template or redirect response.
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return redirect(url_for("main.index"))

    config_loader = current_app.config_loader
    config_loader.set_user_context(current_user)
    config_loader.load_all_configs()

    if request.method == "POST":
        # Get form data
        new_theme = request.form.get("theme")
        new_markdown_theme = request.form.get("markdown_theme")

        # Validate themes
        available_themes = config_loader.themes_config.get("themes", {})
        if new_theme not in available_themes:
            flash("Invalid theme selected.", "error")
            return redirect(url_for("main.settings"))

        if new_markdown_theme not in available_themes:
            flash("Invalid markdown theme selected.", "error")
            return redirect(url_for("main.settings"))

        # Admin updates global config, regular users update personal config
        if current_user == "admin":
            # Update global configuration for admin
            config_loader.app_config.setdefault("app", {})
            config_loader.app_config["app"]["theme"] = new_theme
            config_loader.app_config["app"]["markdown_theme"] = new_markdown_theme

            # Save global configuration
            if config_loader.save_app_config():
                flash("Theme settings updated successfully!", "success")
            else:
                flash("Error saving settings.", "error")
        else:
            # Update user-specific configuration for regular users
            config_loader.user_config.setdefault("app", {})
            config_loader.user_config["app"]["theme"] = new_theme
            config_loader.user_config["app"]["markdown_theme"] = new_markdown_theme

            # Save user configuration
            if config_loader.save_user_config():
                flash("Theme settings updated successfully!", "success")
            else:
                flash("Error saving settings.", "error")

        return redirect(url_for("main.settings"))

    # GET request - display settings form
    themes_config = config_loader.themes_config

    current_theme = config_loader.get_effective_theme()
    current_markdown_theme = config_loader.get_effective_markdown_theme()

    # Convert themes to template format
    themes = []
    for theme_key, theme_data in themes_config.get("themes", {}).items():
        themes.append(
            {
                "value": theme_key,
                "name": theme_data.get("name", theme_key.title()),
                "description": theme_data.get("description", ""),
            }
        )

    return render_template(
        "settings.html",
        themes=themes,
        current_theme=current_theme,
        current_markdown_theme=current_markdown_theme,
    )


@main_bp.route("/users")
@admin_required
def users() -> str:
    """
    Display user management page (admin only).

    Shows list of all users with management options.

    Returns:
        str: Rendered users template.
    """
    user_manager = current_app.user_manager
    config_loader = current_app.config_loader

    # Get all users
    all_users = []
    for username in user_manager.list_users():
        user_data = user_manager.get_user(username)
        if user_data:
            # Get user's link count
            user_links_file = config_loader.get_user_links_file(username)
            try:
                import toml

                with open(user_links_file, "r") as f:
                    user_links = toml.load(f)
                    link_count = len(user_links.get("links", {}))
            except (OSError, toml.TomlDecodeError, KeyError):
                link_count = 0

            all_users.append(
                {
                    "username": username,
                    "display_name": user_data.get("display_name", username),
                    "is_admin": user_data.get("is_admin", False),
                    "created_at": user_data.get("created_at", "Unknown"),
                    "link_count": link_count,
                }
            )

    return render_template("users.html", users=all_users)


@main_bp.route("/users/<username>")
@admin_required
def user_detail(username: str) -> str:
    """
    Display detailed user information (admin only).

    Args:
        username: Username to show details for.

    Returns:
        str: Rendered user detail template.
    """
    user_manager = current_app.user_manager
    config_loader = current_app.config_loader

    user_data = user_manager.get_user(username)
    if not user_data:
        flash(f"User '{username}' not found.", "error")
        return redirect(url_for("main.users"))

    # Get user's links
    config_loader.set_user_context(username)
    config_loader.load_all_configs()
    user_links = config_loader.links_config.get("links", {})

    # Get user's assets directory info
    assets_dir = config_loader.get_user_assets_dir(username)
    asset_count = 0
    total_size = 0

    try:
        import os

        if os.path.exists(assets_dir):
            for file in os.listdir(assets_dir):
                file_path = os.path.join(assets_dir, file)
                if os.path.isfile(file_path):
                    asset_count += 1
                    total_size += os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        pass

    user_info = {
        "username": username,
        "display_name": user_data.get("display_name", username),
        "is_admin": user_data.get("is_admin", False),
        "created_at": user_data.get("created_at", "Unknown"),
        "link_count": len(user_links),
        "asset_count": asset_count,
        "total_size": total_size,
        "links": user_links,
    }

    return render_template("user_detail.html", user=user_info)


@main_bp.route("/users/<username>/delete", methods=["POST"])
@admin_required
def delete_user(username: str) -> Response:
    """
    Delete a user (admin only).

    Args:
        username: Username to delete.

    Returns:
        Response: Redirect response.
    """
    if username == "admin":
        flash("Cannot delete the admin user.", "error")
        return redirect(url_for("main.users"))

    user_manager = current_app.user_manager
    current_user = get_current_user()

    if user_manager.delete_user(username, current_user):
        flash(f"User '{username}' deleted successfully.", "success")
    else:
        flash(f"Failed to delete user '{username}'.", "error")

    return redirect(url_for("main.users"))


@main_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile() -> Union[str, Response]:
    """
    Handle user profile page.

    GET: Display profile information.
    POST: Update profile information.

    Returns:
        Union[str, Response]: Either rendered profile template or redirect response.
    """
    user_manager = current_app.user_manager
    current_user = get_current_user()

    if not current_user:
        flash("User not found.", "error")
        return redirect(url_for("main.index"))

    user_data = user_manager.get_user(current_user)
    if not user_data:
        flash("User data not found.", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        # Handle password change
        if request.form.get("action") == "change_password":
            current_password = request.form.get("current_password", "").strip()
            new_password = request.form.get("new_password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            # Validate current password
            if not user_manager.authenticate_user(current_user, current_password):
                flash("Current password is incorrect.", "error")
                return redirect(url_for("main.profile"))

            # Validate new password
            if not new_password:
                flash("New password is required.", "error")
                return redirect(url_for("main.profile"))

            if new_password != confirm_password:
                flash("New passwords do not match.", "error")
                return redirect(url_for("main.profile"))

            if len(new_password) < 4:
                flash("Password must be at least 4 characters.", "error")
                return redirect(url_for("main.profile"))

            # Change password
            if user_manager.change_password(current_user, new_password):
                flash("Password changed successfully.", "success")
            else:
                flash("Failed to change password.", "error")

            return redirect(url_for("main.profile"))

    return render_template("profile.html", user=user_data, username=current_user)
