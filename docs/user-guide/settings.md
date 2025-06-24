# Settings

The Settings page allows you to configure your personal Trunk8 theme preferences through a web interface.

## Accessing Settings

1. Log in to Trunk8
2. Click "Settings" in the navigation bar
3. Make your changes
4. Click "Save Settings"

## Per-User Theme Configuration

Trunk8 supports individual theme preferences for each user:

### How It Works
- Each user has their own theme preferences
- New users inherit admin-default themes
- Settings are saved in your personal `users/{username}/config.toml` file
- Changes only affect your account
- Admin can set system-wide defaults for new users

## Available Settings

### Theme Configuration

#### UI Theme
- Controls the appearance of your interface
- Applies to navigation, forms, buttons, and tables
- Choose from 25+ Bootswatch themes
- Personal preference, doesn't affect other users

#### Markdown Theme  
- Controls the appearance of rendered markdown content you view
- Can be different from your UI theme
- Useful for optimizing readability
- Only affects markdown content you view

### How Settings Work

When you save settings:

1. Updates are written to `users/{username}/config.toml`
2. Changes apply immediately to your account only
3. Other users are not affected
4. You can change them at any time

## Settings Files

### Personal Configuration

Your settings are stored in:
```
users/{username}/config.toml
```

Example personal configuration:
```toml
[app]
# Your personal theme preferences
theme = "darkly"              # Your UI theme
markdown_theme = "flatly"     # Your markdown theme
```

### Admin Defaults

The admin sets defaults for new users in:
```
config/config.toml
```

Example admin defaults:
```toml
# Admin-level Configuration for Trunk8
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

## Advanced Configuration

### Manual Editing

You can edit your personal settings file directly:

```toml
# users/{username}/config.toml
[app]
theme = "darkly"
markdown_theme = "flatly"
```

### Theme Inheritance

- **New users**: Inherit admin defaults
- **Existing users**: Keep their personal preferences
- **Missing settings**: Fall back to admin defaults

### Admin-Only Settings

Some settings can only be changed by admin in `config/config.toml`:

- Session timeout (`permanent_lifetime_days`)
- System-wide defaults for new users
- Maximum file upload size (`max_file_size_mb`)

## Migration from Global Settings

If you're upgrading from a previous version:

- Your old global theme settings have been moved to admin defaults
- Each user now gets their own theme preferences
- Existing users will inherit the previous global settings
- Use the Settings page to customize your personal themes

## Settings Reference

### Current Web Settings

| Setting | Description | Scope |
|---------|-------------|-------|
| UI Theme | Your interface theme | Personal only |
| Markdown Theme | Your markdown rendering theme | Personal only |

### Admin-Only Settings (config/config.toml)

| Setting | Description | Default |
|---------|-------------|---------|
| theme | Default theme for new users | cerulean |
| markdown_theme | Default markdown theme for new users | cerulean |
| permanent_lifetime_days | Session duration (all users) | 30 |
| max_file_size_mb | Maximum file upload size (MB) | 100 |

## Theme Preview

### Testing Themes

1. Select a theme from dropdown
2. Save settings
3. Theme applies immediately to your account
4. Try different pages to see full effect
5. Other users see no changes

### Theme Combinations

Popular personal combinations:

| UI Theme | Markdown Theme | Use Case |
|----------|----------------|----------|
| Darkly | Flatly | Dark UI, light docs |
| Cosmo | Cosmo | Consistent modern |
| Slate | Solar | Dev-friendly |
| Lux | Litera | Premium + readable |

## Troubleshooting

### Theme Not Applying

Try:

1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check browser console for errors
4. Verify theme name is correct

### Lost Access

If settings break your interface:

1. Ask an admin to check your user config file
2. Or edit `users/{username}/config.toml` manually:
   ```toml
   [app]
   theme = "cosmo"
   markdown_theme = "cosmo"
   ```

## Best Practices

### Testing Changes

1. Preview different themes before settling
2. Check both UI and markdown rendering
3. Consider mobile responsiveness
4. Test with your typical content

### Personal Documentation

Consider noting your preferences:
```toml
# users/john/config.toml
[app]
# Using darkly for better contrast in bright office
theme = "darkly"
# Flatly for readable documentation
markdown_theme = "flatly"
```

## Future Enhancements

Planned additions to per-user settings:

### Personal Preferences
- Language selection
- Time zone settings

## Next Steps

- Explore [available themes](themes.md)
- Learn about [configuration files](../configuration/overview.md)
- Understand [environment variables](../configuration/environment.md)
- Read about [security](../deployment/security.md) 