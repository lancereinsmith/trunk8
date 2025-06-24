# Per-User Configuration (users/{username}/config.toml)

Trunk8 supports individual configuration files for each user, allowing personalized theme preferences while maintaining system-wide defaults.

## Overview

Each regular user can have their own `config.toml` file that overrides admin-level defaults. The admin user modifies global defaults directly. This enables:

- **Personal theme preferences** - Each regular user can choose their own UI and markdown themes
- **Admin control of defaults** - Admin changes global defaults that affect new users
- **Inheritance from admin defaults** - Users without custom settings inherit system defaults
- **Backup and restore support** - User settings are included in personal backups (except admin)

## File Location

Per-user configuration files are located at:
```
users/{username}/config.toml  # For regular users only
```

**Note**: Admin user does not have a personal config file and modifies global defaults directly via `config/config.toml`.

Examples:
```
users/
├── admin/
│   └── links.toml        # Admin has no personal config.toml
├── john/
│   ├── config.toml       # John's personal settings
│   └── links.toml
└── mary/
    ├── config.toml       # Mary's personal settings
    └── links.toml
```

## Configuration Hierarchy

Trunk8 uses a hierarchical configuration system:

1. **Admin Defaults** (`config/config.toml`) - Admin modifies this directly
2. **User Overrides** (`users/{username}/config.toml`) - For regular users only

### Resolution Order

For admin user:

1. Use themes directly from `config/config.toml`
2. If missing, use built-in fallback ("cerulean")

For regular users:

1. Check user's `config.toml` file
2. If not found, use admin default from `config/config.toml`
3. If admin default missing, use built-in fallback ("cerulean")

### Examples

**Admin sets defaults:**
```toml
# config/config.toml
[app]
theme = "cosmo"           # Default for new users
markdown_theme = "flatly" # Default markdown theme
```

**User John's preferences:**
```toml
# users/john/config.toml
[app]
theme = "darkly"          # Overrides admin default
# markdown_theme not specified, inherits "flatly" from admin
```

**User Mary's preferences:**
```toml
# users/mary/config.toml
[app]
theme = "cyborg"          # Overrides admin default  
markdown_theme = "solar"  # Overrides admin default
```

**Result:**

- John sees: UI="darkly", Markdown="flatly"
- Mary sees: UI="cyborg", Markdown="solar"
- New users see: UI="cosmo", Markdown="flatly"

## Managing User Configuration

### Via Web Interface

Users can modify their settings through the Settings page:

1. Log in to Trunk8
2. Navigate to Settings
3. Select preferred themes
4. Click "Save Settings"
5. Changes are saved to:
    - `config/config.toml` (for admin - affects system defaults)
    - `users/{username}/config.toml` (for regular users)

### Manual Editing

Users or admins can edit configuration files directly:

```toml
# users/john/config.toml
[app]
theme = "slate"
markdown_theme = "litera"
```

## Supported Settings

### theme

**Type**: String  
**Description**: UI theme for the user's interface  
**Valid Values**: Any theme from `config/themes.toml`  
**Fallback**: Admin default, then "cerulean"

**Example**:
```toml
theme = "darkly"
```

### markdown_theme

**Type**: String  
**Description**: Theme for rendering markdown content  
**Valid Values**: Any theme from `config/themes.toml`  
**Fallback**: Admin default, then "cerulean"

**Example**:
```toml
markdown_theme = "flatly"
```

## Best Practices

### For Users

1. **Use the Settings page** - Easier than manual editing and validates themes
2. **Test combinations** - Try different UI/markdown theme combinations
3. **Consider accessibility** - Choose high-contrast themes if needed
4. **Backup settings** - Personal configurations are included in user backups

### For Administrators

1. **Set sensible defaults** - Choose themes that work well for most users
2. **Document theme choices** - Help users understand available options
3. **Monitor theme usage** - Consider making popular user themes the default
4. **Respect user preferences** - Don't overwrite user configurations unnecessarily

## Migration and Upgrades

### From Global Configuration

When upgrading from versions without per-user configuration:

1. **Admin defaults preserved** - Global settings become admin defaults
2. **Users inherit settings** - All users initially see the previous global theme
3. **Gradual migration** - Users can customize themes as desired
4. **No data loss** - All existing functionality is preserved
