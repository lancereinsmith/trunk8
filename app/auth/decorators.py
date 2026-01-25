from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar, cast

from flask import flash, redirect, session, url_for

P = ParamSpec("P")
R = TypeVar("R")


def login_required(f: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to require user authentication for protected routes.

    This decorator checks if the user is authenticated by verifying the session.
    If not authenticated, it redirects to the login page with a warning message.

    Args:
        f (F): The function to be decorated. Must be a callable that returns a response.

    Returns:
        F: The decorated function that checks authentication before executing.

    Example:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "This is a protected route"
    """

    @wraps(f)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
        if not session.get("authenticated"):
            flash("Please log in to access this page.", "warning")
            return cast(R, redirect(url_for("auth.login")))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator to require admin authentication for protected routes.

    This decorator checks if the user is authenticated and has admin privileges.
    If not authenticated or not admin, redirects appropriately.

    Args:
        f (F): The function to be decorated. Must be a callable that returns a response.

    Returns:
        F: The decorated function that checks admin authentication before executing.

    Example:
        @app.route('/admin-only')
        @admin_required
        def admin_route():
            return "This is an admin-only route"
    """

    @wraps(f)
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> R:
        if not session.get("authenticated"):
            flash("Please log in to access this page.", "warning")
            return cast(R, redirect(url_for("auth.login")))

        if not session.get("is_admin"):
            flash("Admin access required for this page.", "error")
            return cast(R, redirect(url_for("main.index")))

        return f(*args, **kwargs)

    return decorated_function


def get_current_user() -> str | None:
    """
    Get the current authenticated user's username.

    For admins, this may return the user they're currently viewing/managing
    if they've switched user context.

    Returns:
        Username of current user, or None if not authenticated.
    """
    if not session.get("authenticated"):
        return None

    # If admin is viewing another user's context, return that user
    active_user = session.get("active_user")
    if active_user and session.get("is_admin"):
        return active_user

    # Otherwise return the logged-in user
    return session.get("username")


def get_session_user() -> str | None:
    """
    Get the actually logged-in user's username (not switched context).

    Returns:
        Username of the session user, or None if not authenticated.
    """
    if not session.get("authenticated"):
        return None

    return session.get("username")


def is_admin() -> bool:
    """
    Check if the current session user has admin privileges.

    Returns:
        True if current session user is admin, False otherwise.
    """
    return session.get("authenticated", False) and session.get("is_admin", False)


def get_display_name() -> str:
    """
    Get the display name for the current user context.

    Returns:
        Display name of current user or "Unknown User" if not available.
    """
    if not session.get("authenticated"):
        return "Unknown User"

    # If admin is viewing another user's context, show that user's name
    if session.get("active_user") and session.get("is_admin"):
        return session.get("active_display_name", session.get("active_user", "Unknown User"))

    # Otherwise show the logged-in user's name
    return session.get("display_name", session.get("username", "Unknown User"))


def get_user_context() -> dict:
    """
    Get comprehensive user context information.

    Returns:
        Dictionary containing user context information.
    """
    return {
        "authenticated": session.get("authenticated", False),
        "username": session.get("username"),
        "display_name": session.get("display_name"),
        "is_admin": session.get("is_admin", False),
        "active_user": session.get("active_user"),
        "active_display_name": session.get("active_display_name"),
        "current_user": get_current_user(),
        "session_user": get_session_user(),
        "effective_display_name": get_display_name(),
    }
