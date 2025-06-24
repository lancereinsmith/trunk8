# Application Configuration (config/config.toml)

The `config/config.toml` file contains admin-level configuration for Trunk8. This includes system-wide defaults and session settings that apply to all users.

## Configuration Hierarchy

Trunk8 uses a hierarchical configuration system for theme settings:

1. **Admin Defaults** (`config/config.toml`) -> System-wide defaults
2. **User Overrides** (`users/{username}/config.toml`) -> Individual user preferences

## File Location

The file is located in the config directory:
```
trunk8/
├── config/
│   ├── config.toml    # Admin-level configuration (this file)
│   └── themes.toml    # Available themes
└── users/
    └── {username}/
        └── config.toml # Per-user theme overrides
```

## File Structure

```toml
# Admin-level Configuration for Trunk8
# This file contains system-wide defaults and admin-only settings

[app]
# Default themes for new users (can be overridden per-user)
theme = "cerulean"
markdown_theme = "cerulean"
# Maximum file upload size in megabytes (admin-only)
max_file_size_mb = 100

# Note: Users can override theme settings in their individual config.toml files:
# users/{username}/config.toml

[session]
# Session configuration (admin-only, applies to all users)
permanent_lifetime_days = 30
```

## Configuration Options

### theme

**Type**: String  
**Default**: `"cerulean"`  
**Description**: Default UI theme for new users. Existing users can override this in their personal configuration.

**Valid values**: Any theme name from `config/themes.toml`

**Example**:
```toml
theme = "darkly"  # Dark theme default for new users
```

### markdown_theme

**Type**: String  
**Default**: `"cerulean"`  
**Description**: Default theme for rendering markdown content for new users. Can be different from the UI theme.

**Valid values**: Any theme name from `config/themes.toml`

**Example**:
```toml
markdown_theme = "flatly"  # Light, readable theme for content
```

### max_file_size_mb

**Type**: Integer  
**Default**: `100`  
**Description**: Maximum file upload size in megabytes. This limit applies to all file uploads across all users. Cannot be overridden per-user for security reasons.

**Examples**:
```toml
# Default (100MB)
max_file_size_mb = 100

# Smaller for limited storage
max_file_size_mb = 50

# Larger for high-capacity usage
max_file_size_mb = 500
```

**Notes**:
- Ensure your web server (e.g., Nginx) `client_max_body_size` is set appropriately
- Consider available disk space when increasing limits
- Restart required after changing this setting

### permanent_lifetime_days

**Type**: Integer  
**Default**: `30`  
**Description**: Number of days a "Remember me" session stays active. This applies to all users and cannot be overridden per-user.

**Examples**:
```toml
# Default (30 days)
permanent_lifetime_days = 30

# Shorter for security
permanent_lifetime_days = 7

# Longer for convenience
permanent_lifetime_days = 90
```

## Per-User Configuration

### User Theme Overrides

Each user can override the admin defaults by creating their own `config.toml` file:

**Location**: `users/{username}/config.toml`

**Example**:
```toml
[app]
theme = "cyborg"              # User prefers dark theme
markdown_theme = "flatly"     # But light content for readability
```

### Inheritance Rules

- New users inherit admin defaults automatically
- Users can override themes via the Settings page
- If a user's config.toml doesn't specify a theme, admin default is used
- Admin can change defaults, affecting only users without overrides

## Default Configuration

If `config/config.toml` doesn't exist, Trunk8 creates it with these defaults:

```toml
# Admin-level Configuration for Trunk8
# This file contains system-wide defaults and admin-only settings

[app]
# Default themes for new users (can be overridden per-user)
theme = "cerulean"
markdown_theme = "cerulean"
# Maximum file upload size in megabytes (admin-only)
max_file_size_mb = 100

[session]
# Session configuration (admin-only, applies to all users)
permanent_lifetime_days = 30
```

## Automatic Reloading

Changes to `config/config.toml` are automatically detected and applied:

1. File modification time is checked before each request
2. If changed, configuration is reloaded
3. No server restart required
4. Changes apply immediately

## Examples

### Dark Mode Configuration

```toml
[app]
theme = "darkly"              # Dark UI
markdown_theme = "flatly"     # Light markdown for readability

max_file_size_mb = 100        # Standard file size limit

[session]
permanent_lifetime_days = 30  # Session lifetime for "remember me" feature
```

### Basic Configuration

```toml
[app]
theme = "cosmo"
markdown_theme = "cosmo"

max_file_size_mb = 100

[session]
permanent_lifetime_days = 30
```

### High Security Setup

```toml
[app]
theme = "slate"
markdown_theme = "slate"

max_file_size_mb = 50         # Reduced file size for security

[session]
permanent_lifetime_days = 1  # Sessions expire daily
```

### Development Configuration

```toml
[app]
theme = "sketchy"            # Fun development theme
markdown_theme = "sketchy"

max_file_size_mb = 200       # Larger files for development testing

[session]
permanent_lifetime_days = 365  # Long sessions for development
```

## Advanced Usage

### Multiple Configurations

Maintain different configs for different environments:

```bash
# Development
cp config.dev.toml config/config.toml

# Staging
cp config.staging.toml config/config.toml

# Production
cp config.prod.toml config/config.toml
```

### Programmatic Access

Read configuration in Python:

```python
import toml

# Load configuration
with open('config/config.toml', 'r') as f:
    config = toml.load(f)

# Access values
current_theme = config['app']['theme']
```

### Dynamic Updates

Update configuration programmatically:

```python
import toml

# Load current config
with open('config/config.toml', 'r') as f:
    config = toml.load(f)

# Update theme
config['app']['theme'] = 'darkly'

# Save changes
with open('config/config.toml', 'w') as f:
    toml.dump(config, f)
```

## Validation

### TOML Syntax

Validate syntax before saving:

```bash
# Using Python
python -m toml config/config.toml

# Using toml-cli
toml validate config/config.toml
```

### Theme Validation

Ensure theme exists:

```python
import toml

# Load available themes
with open('config/themes.toml', 'r') as f:
    themes = toml.load(f)['themes']

# Load config
with open('config/config.toml', 'r') as f:
    config = toml.load(f)

# Validate
theme = config['app']['theme']
if theme not in themes:
    print(f"Invalid theme: {theme}")
```


## Troubleshooting

### Configuration Not Loading

1. **Check file permissions**
   ```bash
   ls -la config/config.toml
   # Should be readable by app user
   ```

2. **Verify TOML syntax**
   ```bash
   python -c "import toml; toml.load('config/config.toml')"
   ```

3. **Look for typos**
    - Keys are case-sensitive
    - Strings need quotes
    - No trailing commas

### Theme Not Applying

1. Clear browser cache
2. Check theme name spelling
3. Verify theme exists in `config/themes.toml`
4. Try a known-good theme like "cosmo"



## Best Practices

### Documentation

Best to document your configuration:

```toml
[app]
# Using darkly for better visibility in bright office environment
theme = "darkly"

# Flatly for markdown to ensure readability
markdown_theme = "flatly"

[session]
# 7 day sessions for security compliance
permanent_lifetime_days = 7
```

### Version Control

Track configuration changes:

```bash
git add config/config.toml
git commit -m "Change theme to darkly for better visibility"
```

### Backup

Before making changes:

```bash
cp config/config.toml config/config.toml.backup-$(date +%Y%m%d)
```

### Testing

Test configuration changes:

1. Make change in development
2. Verify all features work
3. Test theme rendering
4. Apply to production

## Security Considerations

### Safe Options

These can be safely stored in `config/config.toml`:

- Theme names
- Relative paths
- Session timeouts
- UI preferences

### Unsafe Options

Never store in `config/config.toml`:

- Passwords
- API keys
- Absolute paths with sensitive info
- Personal information

### File Permissions

```bash
# Restrict access
chmod 644 config/config.toml

# Verify
ls -la config/config.toml
# -rw-r--r-- (readable by all, writable by owner)
```

## Future Options

Planned configuration options:

```toml
[app]
# Current options...

# Future additions
site_title = "My Links"
default_expiration_days = 30
allowed_file_types = ["pdf", "jpg", "png", "doc"]
enable_analytics = false
timezone = "UTC"

[features]
enable_qr_codes = true
enable_click_tracking = false
enable_api = true

[limits]
max_links_per_ip = 100
rate_limit_per_minute = 60
```

## Next Steps

- Configure [Links](links-config.md)
- Understand [Themes](themes-config.md)
- Set up [Environment Variables](environment.md)
- Review [Security Best Practices](../deployment/security.md) 