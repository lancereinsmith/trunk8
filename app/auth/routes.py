"""
Authentication routes for the Trunk8 application.

This module handles user login and logout functionality with session management,
optional "remember me" functionality, and multi-user support.
"""

import os

from flask import Blueprint, Response, flash, render_template, request, session, url_for

from app import _redirect

from ..utils.logging_config import get_logger
from ..utils.user_manager import UserManager

# Create blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Initialize user manager and logger
user_manager = UserManager()
logger = get_logger(__name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """
    Handle user login.

    GET: Display the login form.
    POST: Process login credentials and authenticate user.

    Supports both administrator single-password mode and multi-user mode.

    Returns:
        Union[str, Response]: Either a redirect response on successful login
                             or rendered login template.
    """
    if request.method == "POST":
        # Check if this is administrator mode (password only) or multi-user mode (username + password)
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        remember = request.form.get("remember")  # Will be "on" if checked

        if not password:
            flash("Password is required.", "error")
            return render_template("login.html")

        # Multi-user authentication
        if username:
            logger.info(f"Login attempt for user: {username}")
            user_data = user_manager.authenticate_user(username, password)
            if user_data:
                session["authenticated"] = True
                session["username"] = username
                session["is_admin"] = user_data.get("is_admin", False)
                session["display_name"] = user_data.get("display_name", username)

                if remember:
                    session.permanent = True
                else:
                    session.permanent = False

                logger.info(
                    f"Successful login for user: {username} (admin: {user_data.get('is_admin', False)})"
                )
                flash(f"Welcome, {user_data.get('display_name', username)}!", "success")
                return _redirect(url_for("main.index"))
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                flash("Invalid username or password.", "error")
        else:
            # Administrator single-password mode
            logger.info("Login attempt using administrator single-password mode")
            correct_password = os.environ.get("TRUNK8_ADMIN_PASSWORD", "admin")

            if password == correct_password:
                session["authenticated"] = True
                session["username"] = "admin"  # Default to admin user
                session["is_admin"] = True
                session["display_name"] = "Administrator"

                if remember:
                    session.permanent = True
                else:
                    session.permanent = False

                logger.info("Successful login using administrator single-password mode")
                flash("Successfully logged in!", "success")
                return _redirect(url_for("main.index"))
            else:
                logger.warning("Failed login attempt using administrator single-password mode")
                flash("Invalid password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout() -> Response:
    """
    Handle user logout.

    Clears the user's session and redirects to the login page.

    Returns:
        Response: Redirect response to the login page.
    """
    username = session.get("username", "Unknown")
    logger.info(f"User logout: {username}")
    session.clear()  # Clear all session data
    flash("Successfully logged out!", "success")
    return _redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> str | Response:
    """
    Handle user registration (admin only).

    GET: Display the registration form (admin only).
    POST: Process user registration (admin only).

    Returns:
        Union[str, Response]: Either a redirect response or rendered registration template.
    """
    # Check if user is authenticated and is admin
    if not session.get("authenticated") or not session.get("is_admin"):
        flash("Admin access required to register new users.", "error")
        return _redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        display_name = request.form.get("display_name", "").strip()
        is_admin = request.form.get("is_admin") == "on"

        # Validation
        if not username:
            flash("Username is required.", "error")
            return render_template("register.html")

        if not password:
            flash("Password is required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template("register.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
            return render_template("register.html")

        # Check for invalid characters in username
        if not username.replace("_", "").replace("-", "").isalnum():
            flash(
                "Username can only contain letters, numbers, hyphens, and underscores.",
                "error",
            )
            return render_template("register.html")

        if not display_name:
            display_name = username.title()

        # Attempt to create user
        if user_manager.create_user(username, password, display_name, is_admin):
            flash(f"User '{username}' created successfully!", "success")
            return _redirect(url_for("main.users"))  # Redirect to user management page
        else:
            flash("Username already exists or registration failed.", "error")

    return render_template("register.html")


@auth_bp.route("/switch-user/<username>")
def switch_user(username: str) -> Response:
    """
    Switch to another user context (admin only).

    Args:
        username: Username to switch to.

    Returns:
        Response: Redirect response.
    """
    # Check if current user is admin
    if not session.get("authenticated") or not session.get("is_admin"):
        flash("Admin access required to switch users.", "error")
        return _redirect(url_for("main.index"))

    # Verify target user exists
    user_data = user_manager.get_user(username)
    if not user_data:
        flash(f"User '{username}' not found.", "error")
        return _redirect(url_for("main.users"))

    # Update session to switch user context
    session["active_user"] = username
    session["active_display_name"] = user_data.get("display_name", username)

    flash(f"Switched to user '{user_data.get('display_name', username)}'", "info")
    return _redirect(url_for("main.index"))


@auth_bp.route("/switch-back")
def switch_back() -> Response:
    """
    Switch back to admin user (clear user switching).

    Returns:
        Response: Redirect response.
    """
    if not session.get("authenticated") or not session.get("is_admin"):
        flash("Admin access required.", "error")
        return _redirect(url_for("main.index"))

    # Clear active user switching
    session.pop("active_user", None)
    session.pop("active_display_name", None)

    flash("Switched back to admin view", "info")
    return _redirect(url_for("main.index"))
