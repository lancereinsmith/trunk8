"""
Link management routes for the Trunk8 application.

This module handles all link-related functionality including creation,
editing, deletion, and serving of links. Enhanced with UUID4 security
for file uploads and comprehensive metadata storage.
"""

import mimetypes
import os
import secrets
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from ..auth.decorators import get_current_user, is_admin, login_required
from ..links.utils import validate_short_code
from ..utils.logging_config import get_logger

# Create blueprint
links_bp = Blueprint("links", __name__)

# Initialize logger
logger = get_logger(__name__)

# File upload constants - MAX_FILE_SIZE now read from config
ALLOWED_EXTENSIONS = {
    # Documents
    "pdf",
    "doc",
    "docx",
    "txt",
    "rtf",
    "odt",
    # Images
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "bmp",
    "svg",
    # Archives
    "zip",
    "rar",
    "7z",
    "tar",
    "gz",
    # Spreadsheets
    "xls",
    "xlsx",
    "ods",
    "csv",
    # Presentations
    "ppt",
    "pptx",
    "odp",
    # Audio/Video
    "mp3",
    "wav",
    "mp4",
    "avi",
    "mkv",
    "mov",
    # Code
    "py",
    "js",
    "html",
    "css",
    "json",
    "xml",
    "md",
}


def secure_file_upload(file, asset_folder: str, config_loader) -> Dict[str, str]:
    """
    Securely handle file upload with UUID4 naming and metadata storage.

    Args:
        file: Werkzeug FileStorage object from request.files
        asset_folder: Directory to save the file in
        config_loader: ConfigLoader instance for getting max file size

    Returns:
        Dictionary containing file metadata

    Raises:
        ValueError: If file validation fails
    """
    if not file or not file.filename:
        raise ValueError("No file provided")

    # Get original filename and validate
    original_filename = secure_filename(file.filename)
    if not original_filename:
        raise ValueError("Invalid filename")

    # Check file extension
    file_ext = Path(original_filename).suffix.lower().lstrip(".")
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type '.{file_ext}' not allowed")

    # Generate secure UUID4 filename
    secure_filename_uuid = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(asset_folder, secure_filename_uuid)

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer

    # Get max file size from config
    max_file_size = config_loader.get_max_file_size_bytes()
    if file_size > max_file_size:
        max_size_mb = max_file_size // 1024 // 1024
        raise ValueError(f"File too large (max {max_size_mb}MB)")

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(original_filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Save file
    os.makedirs(asset_folder, exist_ok=True)
    file.save(file_path)

    # Create metadata
    metadata = {
        "path": secure_filename_uuid,
        "original_filename": original_filename,
        "file_size": file_size,
        "mime_type": mime_type,
        "upload_date": datetime.now().isoformat(),
    }

    logger.info(
        f"File uploaded: {original_filename} -> {secure_filename_uuid} ({file_size} bytes)"
    )
    return metadata


def get_file_display_info(link_data: Dict) -> Dict[str, str]:
    """
    Get display information for file links (supports both old and new formats).

    Args:
        link_data: Link configuration dictionary

    Returns:
        Dictionary with display information
    """
    # New format with metadata
    if "original_filename" in link_data:
        return {
            "display_name": link_data["original_filename"],
            "file_size": link_data.get("file_size", 0),
            "upload_date": link_data.get("upload_date"),
            "mime_type": link_data.get("mime_type", "application/octet-stream"),
        }

    # Legacy format - try to extract from path
    path = link_data.get("path", "")
    if "_" in path:
        # Old format: "randomhex_originalname.ext"
        _, original_part = path.split("_", 1)
        return {
            "display_name": original_part,
            "file_size": 0,
            "upload_date": None,
            "mime_type": "application/octet-stream",
        }

    # Fallback
    return {
        "display_name": path,
        "file_size": 0,
        "upload_date": None,
        "mime_type": "application/octet-stream",
    }


@links_bp.route("/<short_code>")
def handle_link(short_code: str) -> Union[str, Response]:
    """
    Handle requests for shortened links.

    Serves links from any user's data if they exist. This is the public
    endpoint for accessing links, so it doesn't require authentication.

    Args:
        short_code: The shortened code for the link.

    Returns:
        Union[str, Response]: Either a file download, redirect response, or rendered template.
    """
    config_loader = current_app.config_loader
    user_manager = current_app.user_manager

    # Search for the link across all users
    link_data = None
    owner_username = None

    for username in user_manager.list_users():
        try:
            user_links_file = config_loader.get_user_links_file(username)
            import toml

            with open(user_links_file, "r") as f:
                user_links = toml.load(f)
                if short_code in user_links.get("links", {}):
                    link_data = user_links["links"][short_code]
                    owner_username = username
                    break
        except (FileNotFoundError, Exception):
            continue

    if not link_data:
        logger.info(f"Link not found: {short_code}")
        return render_template("link_not_found.html")

    # Check for expiration
    expiration_date = link_data.get("expiration_date")
    if expiration_date:
        try:
            exp_date = datetime.fromisoformat(expiration_date)
            if datetime.now() > exp_date:
                logger.info(
                    f"Expired link accessed: {short_code} (expired: {expiration_date})"
                )
                return render_template("link_not_found.html")
        except ValueError:
            logger.warning(
                f"Invalid expiration date format for link {short_code}: {expiration_date}"
            )
            pass  # Invalid date format, ignore expiration

    logger.info(
        f"Link accessed: {short_code} (type: {link_data.get('type')}, owner: {owner_username})"
    )
    link_type = link_data.get("type")

    if link_type == "file":
        filename = link_data.get("path")
        if filename and owner_username:
            asset_folder = config_loader.get_user_assets_dir(owner_username)
            full_path = os.path.join(asset_folder, filename)
            if os.path.exists(full_path):
                # Get display info for proper filename
                display_info = get_file_display_info(link_data)
                download_name = display_info["display_name"]

                return send_from_directory(
                    asset_folder,
                    filename,
                    as_attachment=True,
                    download_name=download_name,
                )

        flash(f"File not found for link '{short_code}'.", "error")
        return render_template("index.html")

    elif link_type == "redirect":
        url = link_data.get("url")
        if url:
            return redirect(url)
        else:
            flash(f"Redirect URL not specified for link '{short_code}'.", "error")
            return render_template("index.html")

    elif link_type == "markdown":
        filename = link_data.get("path")
        if filename and owner_username:
            asset_folder = config_loader.get_user_assets_dir(owner_username)
            file_path = os.path.join(asset_folder, filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                    # Ensure there's a newline at the top
                    if not markdown_content.startswith("\n"):
                        markdown_content = "\n" + markdown_content

                # Determine markdown theme based on viewer
                current_user = get_current_user()

                if current_user:
                    # Logged-in user: use their effective markdown theme
                    config_loader.set_user_context(current_user)
                    config_loader.load_all_configs()
                    markdown_theme = config_loader.get_effective_markdown_theme()
                else:
                    # Public access: use admin default
                    markdown_theme = config_loader.app_config.get("app", {}).get(
                        "markdown_theme", "cerulean"
                    )

                return render_template(
                    "markdown_render.html",
                    markdown_filename=filename,
                    markdown_content=markdown_content,
                    markdown_theme=markdown_theme,
                )

        flash(f"Markdown file not found for link '{short_code}'.", "error")
        return render_template("index.html")

    elif link_type == "html":
        filename = link_data.get("path")
        if filename and owner_username:
            asset_folder = config_loader.get_user_assets_dir(owner_username)
            file_path = os.path.join(asset_folder, filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()

                return render_template(
                    "html_render.html",
                    html_filename=filename,
                    html_content=html_content,
                )

        flash(f"HTML file not found for link '{short_code}'.", "error")
        return render_template("index.html")
    else:
        flash(f"Unknown link type for '{short_code}'.", "error")
        return render_template("index.html")


@links_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_link() -> Union[str, Response]:
    """
    Handle link creation.

    GET: Display the add link form.
    POST: Process form data and create new link.

    Creates links in the current user's data space.

    Returns:
        Union[str, Response]: Either a success redirect or rendered form template.
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
        short_code = request.form.get("short_code", "").strip()
        link_type = request.form.get("link_type", "").strip()

        # Auto-generate short code if not provided
        if not short_code:
            short_code = secrets.token_urlsafe(6)
            # Ensure it doesn't already exist
            user_manager = current_app.user_manager
            while True:
                link_exists = False
                for username in user_manager.list_users():
                    try:
                        user_links_file = config_loader.get_user_links_file(username)
                        import toml

                        with open(user_links_file, "r") as f:
                            user_links = toml.load(f)
                            if short_code in user_links.get("links", {}):
                                link_exists = True
                                break
                    except (OSError, toml.TomlDecodeError, KeyError):
                        continue
                if not link_exists:
                    break
                short_code = secrets.token_urlsafe(6)

        # Validation
        if not link_type:
            flash("Link type is required.", "error")
            return render_template("add_link.html")

        # Validate short code against reserved words and built-in routes
        is_valid, error_message = validate_short_code(short_code)
        if not is_valid:
            flash(error_message, "error")
            return render_template("add_link.html")

        # Check if short code already exists globally
        user_manager = current_app.user_manager
        link_exists = False
        for username in user_manager.list_users():
            try:
                user_links_file = config_loader.get_user_links_file(username)
                import toml

                with open(user_links_file, "r") as f:
                    user_links = toml.load(f)
                    if short_code in user_links.get("links", {}):
                        link_exists = True
                        break
            except (OSError, toml.TomlDecodeError, KeyError):
                continue

        if link_exists:
            flash(f"Short code '{short_code}' already exists.", "error")
            return render_template("add_link.html")

        # Create link data
        new_link_data = {"type": link_type}

        # Handle expiration date
        if request.form.get("enable_expiration") == "on":
            expiration_date = request.form.get("expiration_date")
            if expiration_date:
                new_link_data["expiration_date"] = expiration_date

        # Handle different link types
        asset_folder = config_loader.get_user_assets_dir(current_user)

        if link_type == "file":
            uploaded_file = request.files.get("file")
            if uploaded_file and uploaded_file.filename != "":
                try:
                    file_metadata = secure_file_upload(
                        uploaded_file, asset_folder, config_loader
                    )
                    new_link_data.update(file_metadata)
                except ValueError as e:
                    flash(f"File upload error: {str(e)}", "error")
                    return render_template("add_link.html")
            else:
                flash("No file uploaded for file link.", "error")
                return render_template("add_link.html")

        elif link_type == "markdown":
            markdown_input_type = request.form.get("markdown_input_type", "file")

            if markdown_input_type == "file":
                uploaded_file = request.files.get("markdown_file")
                if uploaded_file and uploaded_file.filename != "":
                    try:
                        # Check if the uploaded file is HTML based on extension
                        original_filename = secure_filename(uploaded_file.filename)
                        file_ext = Path(original_filename).suffix.lower().lstrip(".")

                        if file_ext in ["html", "htm"]:
                            # HTML file detected - change link type to html
                            new_link_data["type"] = "html"
                            secure_filename_uuid = f"{uuid.uuid4()}.html"
                        else:
                            # Regular markdown file
                            secure_filename_uuid = f"{uuid.uuid4()}.md"

                        file_path = os.path.join(asset_folder, secure_filename_uuid)

                        os.makedirs(asset_folder, exist_ok=True)
                        uploaded_file.save(file_path)

                        # Store metadata
                        new_link_data.update(
                            {
                                "path": secure_filename_uuid,
                                "original_filename": original_filename,
                                "upload_date": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        flash(f"Markdown file upload error: {str(e)}", "error")
                        return render_template("add_link.html")
                else:
                    flash("No markdown file uploaded.", "error")
                    return render_template("add_link.html")
            else:  # text input
                markdown_content = request.form.get("markdown_text_content", "").strip()
                if markdown_content:
                    # Ensure there's an empty line at the top
                    if not markdown_content.startswith("\n"):
                        markdown_content = "\n" + markdown_content

                    secure_filename_uuid = f"{uuid.uuid4()}.md"
                    file_path = os.path.join(asset_folder, secure_filename_uuid)

                    os.makedirs(asset_folder, exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)

                    new_link_data.update(
                        {
                            "path": secure_filename_uuid,
                            "original_filename": f"{short_code}.md",
                            "upload_date": datetime.now().isoformat(),
                        }
                    )
                else:
                    flash("No markdown content provided.", "error")
                    return render_template("add_link.html")

        elif link_type == "html":
            html_input_type = request.form.get("html_input_type", "file")

            if html_input_type == "file":
                uploaded_file = request.files.get("html_file")
                if uploaded_file and uploaded_file.filename != "":
                    try:
                        # For HTML files, we use UUID but store as .html
                        secure_filename_uuid = f"{uuid.uuid4()}.html"
                        file_path = os.path.join(asset_folder, secure_filename_uuid)

                        os.makedirs(asset_folder, exist_ok=True)
                        uploaded_file.save(file_path)

                        # Store metadata
                        new_link_data.update(
                            {
                                "path": secure_filename_uuid,
                                "original_filename": secure_filename(
                                    uploaded_file.filename
                                ),
                                "upload_date": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        flash(f"HTML file upload error: {str(e)}", "error")
                        return render_template("add_link.html")
                else:
                    flash("No HTML file uploaded.", "error")
                    return render_template("add_link.html")
            else:  # text input
                html_content = request.form.get("html_text_content", "").strip()
                if html_content:
                    secure_filename_uuid = f"{uuid.uuid4()}.html"
                    file_path = os.path.join(asset_folder, secure_filename_uuid)

                    os.makedirs(asset_folder, exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    new_link_data.update(
                        {
                            "path": secure_filename_uuid,
                            "original_filename": f"{short_code}.html",
                            "upload_date": datetime.now().isoformat(),
                        }
                    )
                else:
                    flash("No HTML content provided.", "error")
                    return render_template("add_link.html")

        elif link_type == "redirect":
            url = request.form.get("url")
            if url:
                new_link_data["url"] = url
            else:
                flash("URL is required for redirect link.", "error")
                return render_template("add_link.html")

        # Add the new link to user's data
        if "links" not in config_loader.links_config:
            config_loader.links_config["links"] = {}

        config_loader.links_config["links"][short_code] = new_link_data

        # Save the updated links config
        if config_loader.save_links_config():
            logger.info(
                f"Link created: {short_code} (type: {link_type}, user: {current_user})"
            )
            return render_template("link_created.html", short_code=short_code)
        else:
            logger.error(f"Failed to save link: {short_code} (user: {current_user})")
            flash("Error saving link.", "error")
            return render_template("add_link.html")

    return render_template("add_link.html")


@links_bp.route("/links")
@login_required
def list_links() -> str:
    """
    Display list of links for the current user.

    Admin users can see all links from all users.
    Regular users only see their own links.

    Returns:
        str: Rendered links list template.
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return redirect(url_for("main.index"))

    config_loader = current_app.config_loader

    if is_admin():
        # Admin can see all links
        all_user_links = config_loader.get_all_user_links(current_user)

        # Format for template with enhanced display info
        formatted_links = []
        for username, user_links in all_user_links.items():
            for short_code, link_data in user_links.items():
                link_info = {
                    "short_code": short_code,
                    "owner": username,
                    "type": link_data.get("type", "unknown"),
                    "expiration_date": link_data.get("expiration_date"),
                }

                # Enhanced target display
                if link_data.get("type") == "file":
                    display_info = get_file_display_info(link_data)
                    link_info["target"] = display_info["display_name"]
                elif link_data.get("type") == "markdown":
                    display_info = get_file_display_info(link_data)
                    link_info["target"] = display_info["display_name"]
                elif link_data.get("type") == "html":
                    display_info = get_file_display_info(link_data)
                    link_info["target"] = display_info["display_name"]
                else:
                    link_info["target"] = link_data.get("url") or link_data.get(
                        "path", ""
                    )

                formatted_links.append(link_info)

        return render_template("list_links.html", links=formatted_links, is_admin=True)
    else:
        # Regular user sees only their links
        config_loader.set_user_context(current_user)
        config_loader.load_all_configs()

        user_links = config_loader.links_config.get("links", {})

        # Format for template with enhanced display info
        formatted_links = []
        for short_code, link_data in user_links.items():
            link_info = {
                "short_code": short_code,
                "owner": current_user,
                "type": link_data.get("type", "unknown"),
                "expiration_date": link_data.get("expiration_date"),
            }

            # Enhanced target display
            if link_data.get("type") == "file":
                display_info = get_file_display_info(link_data)
                link_info["target"] = display_info["display_name"]
            elif link_data.get("type") == "markdown":
                display_info = get_file_display_info(link_data)
                link_info["target"] = display_info["display_name"]
            elif link_data.get("type") == "html":
                display_info = get_file_display_info(link_data)
                link_info["target"] = display_info["display_name"]
            else:
                link_info["target"] = link_data.get("url") or link_data.get("path", "")

            formatted_links.append(link_info)

        return render_template("list_links.html", links=formatted_links, is_admin=False)


@links_bp.route("/edit_link/<short_code>", methods=["GET", "POST"])
@login_required
def edit_link(short_code: str) -> Union[str, Response]:
    """
    Handle link editing.

    GET: Display the edit form for the specified link.
    POST: Process form data and update the link.

    Users can only edit their own links unless they are admin.

    Args:
        short_code: The short code of the link to edit.

    Returns:
        Union[str, Response]: Either a success redirect or rendered form template.
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return redirect(url_for("main.index"))

    config_loader = current_app.config_loader
    user_manager = current_app.user_manager

    # Find the link and its owner
    link_data = None
    owner_username = None

    for username in user_manager.list_users():
        try:
            user_links_file = config_loader.get_user_links_file(username)
            import toml

            with open(user_links_file, "r") as f:
                user_links = toml.load(f)
                if short_code in user_links.get("links", {}):
                    link_data = user_links["links"][short_code]
                    owner_username = username
                    break
        except (OSError, toml.TomlDecodeError, KeyError):
            continue

    if not link_data:
        flash(f"Link '{short_code}' not found.", "error")
        return redirect(url_for("links.list_links"))

    # Check permissions - users can only edit their own links, admins can edit any
    if not is_admin() and owner_username != current_user:
        flash("You don't have permission to edit this link.", "error")
        return redirect(url_for("links.list_links"))

    # Set context to the link owner for editing
    config_loader.set_user_context(owner_username)
    config_loader.load_all_configs()

    if request.method == "POST":
        link_type = request.form.get("link_type")
        new_link_data = {"type": link_type}

        # Handle expiration date
        if request.form.get("enable_expiration") == "on":
            expiration_date = request.form.get("expiration_date")
            if expiration_date:
                new_link_data["expiration_date"] = expiration_date

        asset_folder = config_loader.get_user_assets_dir(owner_username)

        if link_type == "file":
            if "file" not in request.files:
                flash("No file selected", "error")
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                flash("No file selected", "error")
                return redirect(request.url)

            if file:
                # Delete old file if it exists
                if link_data.get("path"):
                    old_file_path = os.path.join(asset_folder, link_data["path"])
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError as e:
                            flash(f"Error deleting old file: {e}", "warning")

                # Upload new file with secure naming
                try:
                    file_metadata = secure_file_upload(
                        file, asset_folder, config_loader
                    )
                    new_link_data.update(file_metadata)
                except ValueError as e:
                    flash(f"File upload error: {str(e)}", "error")
                    return redirect(request.url)

                # Update the link data
                config_loader.links_config["links"][short_code] = new_link_data

                if config_loader.save_links_config():
                    flash("Link updated successfully", "success")
                    return redirect(url_for("links.list_links"))
                else:
                    flash("Error saving changes", "error")

        elif link_type == "redirect":
            url = request.form.get("url")
            if not url:
                flash("URL is required", "error")
                return redirect(request.url)

            new_link_data["url"] = url

            # Update the link data
            config_loader.links_config["links"][short_code] = new_link_data

            if config_loader.save_links_config():
                flash("Link updated successfully", "success")
                return redirect(url_for("links.list_links"))
            else:
                flash("Error saving changes", "error")

        elif link_type == "markdown":
            markdown_input_type = request.form.get("markdown_input_type")

            if markdown_input_type == "file":
                if "markdown_file" not in request.files:
                    flash("No file selected", "error")
                    return redirect(request.url)

                file = request.files["markdown_file"]
                if file.filename == "":
                    flash("No file selected", "error")
                    return redirect(request.url)

                if file:
                    # Delete old file if it exists
                    if link_data.get("path"):
                        old_file_path = os.path.join(asset_folder, link_data["path"])
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except OSError as e:
                                flash(f"Error deleting old file: {e}", "warning")

                    # Upload new markdown file
                    try:
                        # Check if the uploaded file is HTML based on extension
                        original_filename = secure_filename(file.filename)
                        file_ext = Path(original_filename).suffix.lower().lstrip(".")

                        if file_ext in ["html", "htm"]:
                            # HTML file detected - change link type to html
                            new_link_data["type"] = "html"
                            secure_filename_uuid = f"{uuid.uuid4()}.html"
                        else:
                            # Regular markdown file
                            secure_filename_uuid = f"{uuid.uuid4()}.md"

                        file_path = os.path.join(asset_folder, secure_filename_uuid)

                        os.makedirs(asset_folder, exist_ok=True)
                        file.save(file_path)

                        new_link_data.update(
                            {
                                "path": secure_filename_uuid,
                                "original_filename": original_filename,
                                "upload_date": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        flash(f"Markdown file upload error: {str(e)}", "error")
                        return redirect(request.url)

                    # Update the link data
                    config_loader.links_config["links"][short_code] = new_link_data

                    if config_loader.save_links_config():
                        flash("Link updated successfully", "success")
                        return redirect(url_for("links.list_links"))
                    else:
                        flash("Error saving changes", "error")

            else:  # text input
                markdown_content = request.form.get("markdown_text_content")
                if not markdown_content:
                    flash("Markdown content is required", "error")
                    return redirect(request.url)

                # Ensure content starts with a newline
                if not markdown_content.startswith("\n"):
                    markdown_content = "\n" + markdown_content

                # Delete old file if it exists
                if link_data.get("path"):
                    old_file_path = os.path.join(asset_folder, link_data["path"])
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError as e:
                            flash(f"Error deleting old file: {e}", "warning")

                # Create new file with UUID
                secure_filename_uuid = f"{uuid.uuid4()}.md"
                file_path = os.path.join(asset_folder, secure_filename_uuid)

                try:
                    os.makedirs(asset_folder, exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                except OSError as e:
                    flash(f"Error writing markdown file: {e}", "error")
                    return redirect(request.url)

                new_link_data.update(
                    {
                        "path": secure_filename_uuid,
                        "original_filename": f"{short_code}.md",
                        "upload_date": datetime.now().isoformat(),
                    }
                )

                # Update the link data
                config_loader.links_config["links"][short_code] = new_link_data

                if config_loader.save_links_config():
                    flash("Link updated successfully", "success")
                    return redirect(url_for("links.list_links"))
                else:
                    flash("Error saving changes", "error")

        elif link_type == "html":
            html_input_type = request.form.get("html_input_type")

            if html_input_type == "file":
                if "html_file" not in request.files:
                    flash("No file selected", "error")
                    return redirect(request.url)

                file = request.files["html_file"]
                if file.filename == "":
                    flash("No file selected", "error")
                    return redirect(request.url)

                if file:
                    # Delete old file if it exists
                    if link_data.get("path"):
                        old_file_path = os.path.join(asset_folder, link_data["path"])
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except OSError as e:
                                flash(f"Error deleting old file: {e}", "warning")

                    # Upload new HTML file
                    try:
                        secure_filename_uuid = f"{uuid.uuid4()}.html"
                        file_path = os.path.join(asset_folder, secure_filename_uuid)

                        os.makedirs(asset_folder, exist_ok=True)
                        file.save(file_path)

                        new_link_data.update(
                            {
                                "path": secure_filename_uuid,
                                "original_filename": secure_filename(file.filename),
                                "upload_date": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        flash(f"HTML file upload error: {str(e)}", "error")
                        return redirect(request.url)

                    # Update the link data
                    config_loader.links_config["links"][short_code] = new_link_data

                    if config_loader.save_links_config():
                        flash("Link updated successfully", "success")
                        return redirect(url_for("links.list_links"))
                    else:
                        flash("Error saving changes", "error")

            else:  # text input
                html_content = request.form.get("html_text_content")
                if not html_content:
                    flash("HTML content is required", "error")
                    return redirect(request.url)

                # Delete old file if it exists
                if link_data.get("path"):
                    old_file_path = os.path.join(asset_folder, link_data["path"])
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError as e:
                            flash(f"Error deleting old file: {e}", "warning")

                # Create new file with UUID
                secure_filename_uuid = f"{uuid.uuid4()}.html"
                file_path = os.path.join(asset_folder, secure_filename_uuid)

                try:
                    os.makedirs(asset_folder, exist_ok=True)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                except OSError as e:
                    flash(f"Error writing HTML file: {e}", "error")
                    return redirect(request.url)

                new_link_data.update(
                    {
                        "path": secure_filename_uuid,
                        "original_filename": f"{short_code}.html",
                        "upload_date": datetime.now().isoformat(),
                    }
                )

                # Update the link data
                config_loader.links_config["links"][short_code] = new_link_data

                if config_loader.save_links_config():
                    flash("Link updated successfully", "success")
                    return redirect(url_for("links.list_links"))
                else:
                    flash("Error saving changes", "error")

    # Add display info for template
    if link_data and link_data.get("type") in ["file", "markdown", "html"]:
        display_info = get_file_display_info(link_data)
        link_data["display_info"] = display_info

    return render_template("edit_link.html", short_code=short_code, link=link_data)


@links_bp.route("/delete_link/<short_code>", methods=["POST"])
@login_required
def delete_link(short_code: str) -> Response:
    """
    Delete a link.

    Users can only delete their own links unless they are admin.

    Args:
        short_code: The short code of the link to delete.

    Returns:
        Response: Redirect response to the links list.
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return redirect(url_for("main.index"))

    config_loader = current_app.config_loader
    user_manager = current_app.user_manager

    # Find the link and its owner
    link_data = None
    owner_username = None

    for username in user_manager.list_users():
        try:
            user_links_file = config_loader.get_user_links_file(username)
            import toml

            with open(user_links_file, "r") as f:
                user_links = toml.load(f)
                if short_code in user_links.get("links", {}):
                    link_data = user_links["links"][short_code]
                    owner_username = username
                    break
        except (OSError, toml.TomlDecodeError, KeyError):
            continue

    if not link_data:
        flash(f"Link '{short_code}' not found.", "error")
        return redirect(url_for("links.list_links"))

    # Check permissions
    if not is_admin() and owner_username != current_user:
        flash("You don't have permission to delete this link.", "error")
        return redirect(url_for("links.list_links"))

    # Set context to the link owner for deletion
    config_loader.set_user_context(owner_username)
    config_loader.load_all_configs()

    # Delete associated file if it exists
    if link_data.get("type") in ["file", "markdown", "html"] and link_data.get("path"):
        asset_folder = config_loader.get_user_assets_dir(owner_username)
        file_path = os.path.join(asset_folder, link_data["path"])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except OSError as e:
                flash(f"Error deleting file: {e}", "warning")

    # Remove link from config
    if short_code in config_loader.links_config.get("links", {}):
        del config_loader.links_config["links"][short_code]

        if config_loader.save_links_config():
            logger.info(
                f"Link deleted: {short_code} (owner: {owner_username}, deleted by: {current_user})"
            )
            flash(f"Link '{short_code}' deleted successfully.", "success")
        else:
            logger.error(
                f"Failed to delete link: {short_code} (owner: {owner_username})"
            )
            flash("Error deleting link.", "error")
    else:
        logger.warning(
            f"Attempted to delete non-existent link: {short_code} (user: {current_user})"
        )
        flash(f"Link '{short_code}' not found in user data.", "error")

    return redirect(url_for("links.list_links"))


@links_bp.route("/delete/<short_code>", methods=["POST"])
@login_required
def delete_link_short(short_code: str) -> Response:
    """
    Delete a link (short route for compatibility).

    This route provides compatibility with existing tests and templates
    that expect /delete/<short_code> instead of /delete_link/<short_code>.

    Args:
        short_code: The short code of the link to delete.

    Returns:
        Response: Redirect response to the links list.
    """
    return delete_link(short_code)
