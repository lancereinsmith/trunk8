# Configuration Overview

Trunk8 uses a flexible TOML-based system for configuration and data storage that allows you to customize almost every aspect of the application. Configuration changes are automatically reloaded without requiring a server restart.

## Configuration and Data Files

Trunk8 uses TOML files for configuration and data storage:

### 1. config/config.toml
The main application configuration file containing:

- Theme settings
- File storage locations
- Session configuration
- Application behavior

### 2. users/users.toml
Stores user account data in multi-user mode:

- User credentials and password hashes
- Admin privileges configuration
- User display names and metadata
- Account creation timestamps

### 3. users/{username}/links.toml (Per-User Data Storage)
Stores each user's link data:

- Short codes and their mappings
- Link types and properties
- Expiration dates
- File paths and URLs

**Note**: Each user has their own isolated links.toml file in their directory.

### 4. config/themes.toml
Contains available theme definitions:

- Theme names and descriptions
- Loaded automatically on startup
- Read-only (not meant to be edited)

## Configuration Loading

### Automatic Reloading

Trunk8 monitors configuration files for changes and automatically reloads them:

- No server restart required
- Changes apply immediately
- File modification times are tracked

### Default Values

If files don't exist, Trunk8 creates them with sensible defaults:

- `config/config.toml` - Default theme and paths (configuration)
- `users/users.toml` - Admin user with default password (user management)
- `users/{username}/links.toml` - Empty links structure per user
- `config/themes.toml` - Falls back to built-in themes

## Configuration Hierarchy

```
Environment Variables
    ↓
TOML Configuration Files
    ↓
Application Defaults
```

1. **Environment Variables** - Highest priority (e.g., `TRUNK8_ADMIN_PASSWORD`)
2. **TOML Files** - User-editable configuration
3. **Defaults** - Built-in fallback values

## File Locations

By default, configuration files are located in the application root:

```
trunk8/
├── config/
│   ├── config.toml  # Application settings
│   └── themes.toml  # Available themes
└── users/           # Multi-user data
    ├── users.toml   # User management
    ├── admin/
    │   ├── links.toml  # Admin links
    │   └── assets/     # Admin files
    └── {username}/
        ├── links.toml  # User links
        └── assets/     # User files
```

## Quick Configuration Examples

### Basic Application Settings

```toml
# config/config.toml
[app]
theme = "darkly"              # UI theme
markdown_theme = "cerulean"   # Markdown rendering theme

max_file_size_mb = 100

[session]
permanent_lifetime_days = 30  # Session duration
```

### Sample User Configuration

```toml
# users/users.toml
[users]

[users.admin]
password_hash = "hashed_password"
is_admin = true
display_name = "Administrator"
created_at = "2024-01-01T00:00:00"

[users.john]
password_hash = "hashed_password"
is_admin = false
display_name = "John Doe"
created_at = "2024-01-01T00:00:00"
```

### Sample Link Configuration (Per-User)

```toml
# users/admin/links.toml or users/{username}/links.toml
[links.homepage]
type = "redirect"
url = "https://example.com"

[links.document]
type = "file"
path = "f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf"
original_filename = "Q4-Financial-Report-2024.pdf"
file_size = 2048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:30:00"
expiration_date = "2024-12-31T23:59:59"

[links.readme]
type = "markdown"
path = "9a8f6e4d-2b1c-4d3e-8f7a-6b5c4d3e2f1a.md"
original_filename = "project-readme.md"
upload_date = "2024-01-10T14:20:30"
```

### Environment Variables

```bash
# Security settings (not in TOML files)
export TRUNK8_ADMIN_PASSWORD="secure-password"
export TRUNK8_SECRET_KEY="random-secret-key"
export TRUNK8_LOG_LEVEL=INFO
export TRUNK8_PORT=5001
```

## Configuration Best Practices

### 1. Backup Your Configuration

Before making changes:
```bash
cp config/config.toml config/config.toml.backup
cp users/users.toml users/users.toml.backup
# Backup all user directories
cp -r users/ users_backup/
```

### 2. Use Version Control

Track configuration changes:
```bash
git add config/config.toml users/users.toml
git commit -m "Update configuration"
```

### 3. Validate TOML Syntax

Use a TOML validator before saving:

- Command line: `python -m toml config/config.toml`

### 4. Organize Links Logically

Group related links:
```toml
# Team resources
[links.team-calendar]
[links.team-handbook]
[links.team-directory]

# Project Alpha
[links.alpha-spec]
[links.alpha-repo]
[links.alpha-docs]
```

## Configuration Security

### Sensitive Data

Never store sensitive data in TOML files:

- ❌ Passwords
- ❌ API keys
- ❌ Secret tokens

Use environment variables instead:

- ✅ `TRUNK8_ADMIN_PASSWORD`
- ✅ `TRUNK8_SECRET_KEY`

### File Permissions

Secure your configuration files:

```bash
# Restrict access to owner only
chmod 600 config/config.toml users/users.toml
chmod -R 600 users/*/links.toml

# Ensure correct ownership
chown -R www-data:www-data config/ users/
```

## Troubleshooting Configuration

### Common Issues

#### Changes Not Taking Effect
- Check file syntax for errors
- Verify file permissions
- Look for error messages in logs

#### Invalid TOML Syntax
```
Error loading config file: Invalid TOML
```

- Check for unclosed quotes
- Verify table names are unique
- Ensure proper indentation

#### Missing Configuration
- Trunk8 creates default files automatically
- Check write permissions in directory
- Verify disk space availability

## Migration and Upgrades

### Backing Up Configuration

Before upgrading:
```bash
tar -czf trunk8-config-backup.tar.gz config/ users/
```

## Next Steps

Dive deeper into specific configuration areas:

- [Application Config](app-config.md) - Detailed `config/config.toml` reference
- [Links Data](links-config.md) - Managing `links.toml` data
- [Themes Config](themes-config.md) - Understanding themes
- [Environment Variables](environment.md) - Security configuration 