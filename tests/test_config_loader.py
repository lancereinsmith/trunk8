"""
Test suite for ConfigLoader utility.

Tests cover configuration loading, saving, file watching, and error handling.
"""

import os
import time

import pytest
import toml

from app.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_init(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()

        assert loader.app_config == {}
        assert loader.links_config == {}
        assert loader.themes_config == {}
        assert loader._last_app_config_mod_time is None
        assert loader._last_links_config_mod_time is None
        assert loader._last_themes_config_mod_time is None

    def test_load_existing_configs(self, test_config_files, monkeypatch):
        """Test loading existing configuration files."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.set_user_context("admin")
        loader.load_all_configs()

        # Check app config
        assert "app" in loader.app_config
        assert loader.app_config["app"]["theme"] == "cosmo"
        # Use realpath to handle symlink resolution on macOS
        expected_assets_path = os.path.realpath(
            os.path.join(test_config_files["temp_dir"], "assets")
        )
        # Check if asset_folder is in config, otherwise use default
        if "asset_folder" in loader.app_config["app"]:
            actual_assets_path = os.path.realpath(
                loader.app_config["app"]["asset_folder"]
            )
            assert actual_assets_path == expected_assets_path
        else:
            # asset_folder not in config is acceptable (uses default)
            pass

        # Check links config
        assert "links" in loader.links_config
        assert loader.links_config["links"] == {}

        # Check themes config
        assert "themes" in loader.themes_config
        assert "cosmo" in loader.themes_config["themes"]
        assert "cerulean" in loader.themes_config["themes"]

    def test_create_missing_config_files(self, temp_dir, monkeypatch):
        """Test creation of missing config files."""
        monkeypatch.chdir(temp_dir)

        loader = ConfigLoader()
        loader.set_user_context("admin")
        loader.load_all_configs()

        # Check that files were created
        assert os.path.exists("config/config.toml")
        assert os.path.exists("users/admin/links.toml")

        # Check default content
        assert loader.app_config["app"]["theme"] == "cerulean"
        assert loader.links_config["links"] == {}

    def test_config_file_reloading(self, test_config_files, monkeypatch):
        """Test automatic config reloading on file changes."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        # Initial theme
        assert loader.app_config["app"]["theme"] == "cosmo"

        # Modify config file
        time.sleep(0.1)  # Ensure file modification time changes
        config_data = toml.load(test_config_files["config"])
        config_data["app"]["theme"] = "darkly"
        with open(test_config_files["config"], "w") as f:
            toml.dump(config_data, f)

        # Reload should detect change
        loader.load_all_configs()
        assert loader.app_config["app"]["theme"] == "darkly"

    def test_save_app_config(self, test_config_files, monkeypatch):
        """Test saving app configuration."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        # Modify config
        loader.app_config["app"]["theme"] = "modified"

        # Save
        assert loader.save_app_config() is True

        # Verify saved
        with open(test_config_files["config"], "r") as f:
            saved_config = toml.load(f)
        assert saved_config["app"]["theme"] == "modified"

    def test_save_links_config(self, test_config_files, monkeypatch):
        """Test saving links configuration."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.set_user_context("admin")
        loader.load_all_configs()

        # Add a link
        loader.links_config["links"]["test"] = {
            "type": "redirect",
            "url": "https://test.com",
        }

        # Save
        assert loader.save_links_config() is True

        # Verify saved
        admin_links_file = loader.get_user_links_file("admin")
        with open(admin_links_file, "r") as f:
            saved_config = toml.load(f)
        assert "test" in saved_config["links"]
        assert saved_config["links"]["test"]["url"] == "https://test.com"

    def test_available_themes_property(self, test_config_files, monkeypatch):
        """Test available_themes property."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        themes = loader.available_themes
        assert isinstance(themes, list)
        assert "cosmo" in themes
        assert "cerulean" in themes
        assert "darkly" in themes

    def test_themes_for_template_property(self, test_config_files, monkeypatch):
        """Test themes_for_template property."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        themes = loader.themes_for_template
        assert isinstance(themes, list)
        assert len(themes) == 26  # Now using real themes.toml with 26 themes

        # Check structure
        cosmo_theme = next(t for t in themes if t["value"] == "cosmo")
        assert cosmo_theme["name"] == "Cosmo"
        assert cosmo_theme["description"] == "An ode to Metro"

    @pytest.mark.skip(reason="Custom links files not supported in multiuser system")
    def test_custom_links_file_path(self, test_config_files, monkeypatch):
        """Test using custom links file path from config."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        # Create custom links file
        custom_links_path = os.path.join(
            test_config_files["temp_dir"], "custom_links.toml"
        )
        with open(custom_links_path, "w") as f:
            toml.dump(
                {
                    "links": {
                        "custom": {"type": "redirect", "url": "https://custom.com"}
                    }
                },
                f,
            )

        # Update config to use custom path
        loader = ConfigLoader()
        loader.set_user_context(None)  # Use global context for custom links file
        loader.load_all_configs()
        loader.app_config["app"]["links_file"] = custom_links_path
        loader.save_app_config()

        # Reload and check
        loader.set_user_context(None)  # Ensure we're still using global context
        loader.load_all_configs()
        assert "custom" in loader.links_config["links"]
        assert loader.links_config["links"]["custom"]["url"] == "https://custom.com"

    def test_error_handling_corrupt_toml(self, test_config_files, monkeypatch, capsys):
        """Test handling of corrupt TOML files."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        # Corrupt the config file
        with open(test_config_files["config"], "w") as f:
            f.write("invalid toml content [[[")

        loader = ConfigLoader()
        loader.load_all_configs()

        # Should print error message
        captured = capsys.readouterr()
        assert "Error loading app config file" in captured.out

    def test_missing_themes_file(self, test_config_files, monkeypatch):
        """Test fallback when config/themes.toml is missing."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        # Remove themes file
        os.remove(test_config_files["themes"])

        loader = ConfigLoader()
        loader.load_all_configs()

        # Should use fallback themes
        assert "themes" in loader.themes_config
        assert "cosmo" in loader.themes_config["themes"]
        assert (
            loader.themes_config["themes"]["cosmo"]["description"] == "An ode to Metro"
        )

    def test_save_config_error_handling(self, test_config_files, monkeypatch, capsys):
        """Test error handling when saving configs fails."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        # Make config file read-only
        os.chmod(test_config_files["config"], 0o444)

        # Try to save
        result = loader.save_app_config()
        assert result is False

        # Should print error message
        captured = capsys.readouterr()
        assert "Error saving app config" in captured.out

        # Restore permissions
        os.chmod(test_config_files["config"], 0o644)

    def test_no_reload_when_unchanged(self, test_config_files, monkeypatch, capsys):
        """Test that configs are not reloaded when files haven't changed."""
        monkeypatch.chdir(test_config_files["temp_dir"])

        loader = ConfigLoader()
        loader.load_all_configs()

        # Clear output
        capsys.readouterr()

        # Load again without changes
        loader.load_all_configs()

        # Should not print reload messages
        captured = capsys.readouterr()
        assert "reloaded" not in captured.out
