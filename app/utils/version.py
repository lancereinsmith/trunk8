"""
Version utility for the Trunk8 application.

This module provides a single source of truth for the application version
by reading it from pyproject.toml.
"""

from pathlib import Path

import toml


def get_version() -> str:
    """
    Get the application version from pyproject.toml.

    Returns:
        str: The version string from pyproject.toml.

    Raises:
        FileNotFoundError: If pyproject.toml cannot be found.
        KeyError: If version is not found in pyproject.toml.
    """
    # Get the project root directory (parent of app directory)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    with open(pyproject_path, "r") as f:
        pyproject_data = toml.load(f)

    version = pyproject_data.get("project", {}).get("version")
    if version is None:
        raise KeyError("Version not found in pyproject.toml [project] section")

    return version


__version__: str = get_version()
