"""
Backup and restore routes for the Trunk8 application.

This module handles backup creation (downloading zip files) and
restore functionality (uploading and processing backup files).
"""

import os
import tempfile
import zipfile
from datetime import datetime

import toml
from flask import Response, current_app, flash, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from app import _redirect, get_config_loader, get_user_manager

from ..auth.decorators import get_current_user, is_admin, login_required
from ..utils.version import __version__
from . import backup_bp


@backup_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_backup() -> str | Response:
    """
    Create and download a backup zip file containing user's links and assets.

    GET: Display backup creation form
    POST: Generate and download backup zip file

    Returns:
        Union[str, Response]: Either rendered template or file download response
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return _redirect(url_for("main.index"))

    if request.method == "POST":
        # Check if admin is backing up another user's data
        target_user = request.form.get("target_user", current_user)

        # Validate permissions
        if target_user != current_user and not is_admin():
            flash("You don't have permission to backup other users' data.", "error")
            return _redirect(url_for("backup.create_backup"))

        config_loader = get_config_loader(current_app)
        user_manager = get_user_manager(current_app)

        # Validate target user exists
        if target_user not in user_manager.list_users():
            flash(f"User '{target_user}' not found.", "error")
            return _redirect(url_for("backup.create_backup"))

        try:
            # Create temporary zip file
            temp_dir = tempfile.mkdtemp()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"trunk8_backup_{target_user}_{timestamp}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add links.toml file
                links_file = config_loader.get_user_links_file(target_user)
                if os.path.exists(links_file):
                    zipf.write(links_file, "links.toml")
                else:
                    # Create empty links file in zip
                    empty_links = {"links": {}}
                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".toml", delete=False
                    ) as temp_links:
                        toml.dump(empty_links, temp_links)
                        temp_links_path = temp_links.name
                    zipf.write(temp_links_path, "links.toml")
                    os.unlink(temp_links_path)

                # Add user config.toml file (except for admin)
                # Admin uses global config/config.toml directly
                if target_user != "admin":
                    user_config_file = config_loader.get_user_config_file(target_user)
                    if os.path.exists(user_config_file):
                        zipf.write(user_config_file, "config.toml")
                    else:
                        # Create empty user config file in zip
                        empty_config = {"app": {}}
                        with tempfile.NamedTemporaryFile(
                            mode="w", suffix=".toml", delete=False
                        ) as temp_config:
                            toml.dump(empty_config, temp_config)
                            temp_config_path = temp_config.name
                        zipf.write(temp_config_path, "config.toml")
                        os.unlink(temp_config_path)

                # Add assets directory
                assets_dir = config_loader.get_user_assets_dir(target_user)
                if os.path.exists(assets_dir):
                    for root, _dirs, files in os.walk(assets_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Create relative path within zip
                            arcname = os.path.join("assets", os.path.relpath(file_path, assets_dir))
                            zipf.write(file_path, arcname)

                # Add metadata file
                metadata = {
                    "backup_info": {
                        "created_by": current_user,
                        "target_user": target_user,
                        "created_at": datetime.now().isoformat(),
                        "trunk8_version": __version__,
                    }
                }
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".toml", delete=False
                ) as temp_meta:
                    toml.dump(metadata, temp_meta)
                    temp_meta_path = temp_meta.name
                zipf.write(temp_meta_path, "backup_metadata.toml")
                os.unlink(temp_meta_path)

            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype="application/zip",
            )

        except Exception as e:
            flash(f"Error creating backup: {str(e)}", "error")
            return _redirect(url_for("backup.create_backup"))

    # GET request - show backup form
    user_manager = get_user_manager(current_app)
    available_users = user_manager.list_users() if is_admin() else [current_user]

    return render_template(
        "backup_create.html",
        current_user=current_user,
        available_users=available_users,
        is_admin=is_admin(),
    )


@backup_bp.route("/restore", methods=["GET", "POST"])
@login_required
def restore_backup() -> str | Response:
    """
    Restore user data from an uploaded backup zip file.

    GET: Display restore form
    POST: Process uploaded backup file and restore data

    Returns:
        Union[str, Response]: Either rendered template or redirect response
    """
    current_user = get_current_user()
    if not current_user:
        flash("User context not found.", "error")
        return _redirect(url_for("main.index"))

    if request.method == "POST":
        # Check if file was uploaded
        if "backup_file" not in request.files:
            flash("No backup file selected.", "error")
            return _redirect(url_for("backup.restore_backup"))

        backup_file = request.files["backup_file"]
        if backup_file.filename == "":
            flash("No backup file selected.", "error")
            return _redirect(url_for("backup.restore_backup"))

        # Get restore options
        restore_mode = request.form.get("restore_mode", "merge")  # merge or replace
        target_user = request.form.get("target_user", current_user)

        # Validate permissions
        if target_user != current_user and not is_admin():
            flash("You don't have permission to restore to other users.", "error")
            return _redirect(url_for("backup.restore_backup"))

        config_loader = get_config_loader(current_app)
        user_manager = get_user_manager(current_app)

        # Validate target user exists
        if target_user not in user_manager.list_users():
            flash(f"User '{target_user}' not found.", "error")
            return _redirect(url_for("backup.restore_backup"))

        try:
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            filename = secure_filename(backup_file.filename or "")
            temp_file_path = os.path.join(temp_dir, filename)
            backup_file.save(temp_file_path)

            # Validate and process zip file
            if not zipfile.is_zipfile(temp_file_path):
                flash("Invalid backup file. Please upload a valid zip file.", "error")
                return _redirect(url_for("backup.restore_backup"))

            with zipfile.ZipFile(temp_file_path, "r") as zipf:
                # Validate backup structure
                zip_contents = zipf.namelist()
                if "links.toml" not in zip_contents:
                    flash("Invalid backup file. Missing links.toml.", "error")
                    return _redirect(url_for("backup.restore_backup"))

                # Extract to temporary directory
                extract_dir = os.path.join(temp_dir, "extracted")
                zipf.extractall(extract_dir)

                # Load backup metadata if available
                metadata_path = os.path.join(extract_dir, "backup_metadata.toml")
                backup_info = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path) as f:
                        metadata = toml.load(f)
                        backup_info = metadata.get("backup_info", {})

                # Get target paths
                target_links_file = config_loader.get_user_links_file(target_user)
                target_assets_dir = config_loader.get_user_assets_dir(target_user)

                # Ensure target directories exist
                os.makedirs(os.path.dirname(target_links_file), exist_ok=True)
                os.makedirs(target_assets_dir, exist_ok=True)

                # Only get config file path for non-admin users
                target_config_file = None
                if target_user != "admin":
                    target_config_file = config_loader.get_user_config_file(target_user)
                    os.makedirs(os.path.dirname(target_config_file), exist_ok=True)

                # Restore links
                backup_links_path = os.path.join(extract_dir, "links.toml")
                with open(backup_links_path) as f:
                    backup_links = toml.load(f)

                if restore_mode == "replace":
                    # Replace existing links completely
                    restored_links = backup_links
                else:
                    # Merge with existing links
                    existing_links = {"links": {}}
                    if os.path.exists(target_links_file):
                        with open(target_links_file) as f:
                            existing_links = toml.load(f)

                    # Merge links (backup takes precedence for conflicts)
                    if "links" not in existing_links:
                        existing_links["links"] = {}

                    existing_links["links"].update(backup_links.get("links", {}))
                    restored_links = existing_links

                # Save restored links
                with open(target_links_file, "w") as f:
                    toml.dump(restored_links, f)

                # Restore user config if available (not applicable for admin)
                backup_config_path = os.path.join(extract_dir, "config.toml")
                if (
                    os.path.exists(backup_config_path)
                    and target_user != "admin"
                    and target_config_file
                ):
                    with open(backup_config_path) as f:
                        backup_config = toml.load(f)

                    if restore_mode == "replace":
                        # Replace existing config completely
                        restored_config = backup_config
                    else:
                        # Merge with existing config
                        existing_config = {"app": {}}
                        if os.path.exists(target_config_file):
                            with open(target_config_file) as f:
                                existing_config = toml.load(f)

                        # Merge config (backup takes precedence for conflicts)
                        if "app" not in existing_config:
                            existing_config["app"] = {}

                        existing_config["app"].update(backup_config.get("app", {}))
                        restored_config = existing_config

                    # Save restored config
                    with open(target_config_file, "w") as f:
                        toml.dump(restored_config, f)

                # Restore assets
                backup_assets_dir = os.path.join(extract_dir, "assets")
                restored_files = 0
                if os.path.exists(backup_assets_dir):
                    import shutil

                    for root, _dirs, files in os.walk(backup_assets_dir):
                        for file in files:
                            src_path = os.path.join(root, file)
                            # Maintain relative structure
                            rel_path = os.path.relpath(src_path, backup_assets_dir)
                            dst_path = os.path.join(target_assets_dir, rel_path)

                            # Create directory if needed
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                            # Copy file (overwrite if exists)
                            shutil.copy2(src_path, dst_path)
                            restored_files += 1

                # Clean up temp files
                import shutil

                shutil.rmtree(temp_dir)

                # Success message
                restored_links_count = len(backup_links.get("links", {}))
                restored_config_msg = ""
                if (
                    os.path.exists(backup_config_path)
                    and target_user != "admin"
                    and target_config_file
                ):
                    restored_config_msg = " and user settings"

                success_msg = "Backup restored successfully! "
                success_msg += f"Restored {restored_links_count} links{restored_config_msg} and {restored_files} files"
                if backup_info.get("created_at"):
                    success_msg += f" (created: {backup_info['created_at'][:10]})"

                flash(success_msg, "success")
                return _redirect(url_for("links.list_links"))

        except Exception as e:
            flash(f"Error restoring backup: {str(e)}", "error")
            return _redirect(url_for("backup.restore_backup"))

    # GET request - show restore form
    user_manager = get_user_manager(current_app)
    available_users = user_manager.list_users() if is_admin() else [current_user]

    return render_template(
        "backup_restore.html",
        current_user=current_user,
        available_users=available_users,
        is_admin=is_admin(),
    )
