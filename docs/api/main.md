# Main Routes Module (app.main)

The main module handles general application routes including the home page, settings, user management, and profile functionality.

## Overview

The `app.main` module provides:
- Home page and dashboard
- Settings interface for themes and configuration
- User management interface (admin only)
- User profile and switching functionality
- General application navigation

## Blueprint Routes

### Main Application Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page and dashboard |
| `/settings` | GET, POST | Settings interface |
| `/users` | GET | User management (admin only) |
| `/users/<username>` | GET | User details (admin only) |
| `/profile` | GET | Current user profile |

## Route Handlers

### index()

```python
@main_bp.route("/")
@login_required
def index() -> str:
    """
    Display the home page with user dashboard.
    
    Returns:
        Rendered template with user statistics and quick actions.
    """
```

**Features:**
- User-specific dashboard
- Link count statistics
- Quick action buttons
- Recent links preview
- User context display

**Context Provided:**
- Total link count for current user
- Links by type breakdown
- Expiring links warning
- User display name and admin status

### settings()

```python
@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> Union[str, Response]:
    """
    Handle application settings.
    
    GET: Display the settings form.
    POST: Process settings updates.
    """
```

**Features:**
- Theme selection (UI and markdown)
- Settings validation
- Real-time preview
- Configuration persistence
- Flash message feedback

**POST Data:**
- `theme` (required) - UI theme selection
- `markdown_theme` (required) - Markdown rendering theme

**Validation:**
- Theme existence validation
- Configuration file write permissions
- TOML syntax validation

### users()

```python
@main_bp.route("/users")
@admin_required
def users() -> str:
    """
    Display user management interface (admin only).
    
    Returns:
        Rendered template with all users list.
    """
```

**Features:**
- Admin-only access
- All users listing
- User statistics
- Management actions
- User creation link

**User Information:**
- Username and display name
- Admin status indicator
- Account creation date
- Link count per user
- Storage usage statistics

### user_detail()

```python
@main_bp.route("/users/<username>")
@admin_required
def user_detail(username: str) -> Union[str, Response]:
    """
    Display detailed user information (admin only).
    
    Args:
        username: Username to display details for.
    """
```

**Features:**
- User existence validation
- Detailed user information
- User's links overview
- Deletion preview
- User switching option

**Information Displayed:**
- User profile details
- Link statistics by type
- Storage usage breakdown
- Recent activity
- Administrative actions

### profile()

```python
@main_bp.route("/profile")
@login_required
def profile() -> str:
    """
    Display current user's profile.
    
    Returns:
        Rendered template with user profile information.
    """
```

**Features:**
- Current user information
- Account statistics
- Settings shortcuts
- Data overview

## Template Context

### Dashboard Context

The home page provides rich context for dashboard display:

```python
context = {
    'user_stats': {
        'total_links': int,
        'redirect_count': int,
        'file_count': int,
        'markdown_count': int,
        'expired_count': int
    },
    'recent_links': [Link],  # Recent 5 links
    'expiring_soon': [Link], # Links expiring in 7 days
    'storage_usage': {
        'total_files': int,
        'total_size': int
    }
}
```

### Settings Context

Settings page provides theme information:

```python
context = {
    'current_theme': str,
    'current_markdown_theme': str,
    'available_themes': Dict[str, Dict[str, str]],
    'theme_categories': {
        'light': List[str],
        'dark': List[str],
        'unique': List[str]
    }
}
```

### User Management Context

User management pages provide comprehensive user data:

```python
context = {
    'users': [
        {
            'username': str,
            'display_name': str,
            'is_admin': bool,
            'created_at': str,
            'link_count': int,
            'file_count': int,
            'storage_usage': int
        }
    ],
    'total_users': int,
    'admin_count': int
}
```

## User Statistics

### Link Statistics

```python
def get_user_link_stats(username: str) -> Dict[str, int]:
    """
    Get comprehensive link statistics for a user.
    
    Args:
        username: Username to get stats for.
        
    Returns:
        Dictionary with link counts by type and status.
    """
```

Returns:
- Total links
- Links by type (redirect, file, markdown)
- Expired links count
- Links expiring soon

### Storage Statistics

```python
def get_user_storage_stats(username: str) -> Dict[str, Any]:
    """
    Get storage usage statistics for a user.
    
    Args:
        username: Username to get stats for.
        
    Returns:
        Dictionary with storage information.
    """
```

Returns:
- Total files count
- Total storage used (bytes)
- Average file size
- Largest files

## Administrative Functions

### User Management

```python
def get_all_users_info() -> List[Dict[str, Any]]:
    """
    Get information for all users (admin only).
    
    Returns:
        List of user information dictionaries.
    """
```

### User Deletion Preview

```python
def get_deletion_preview(username: str) -> Optional[Dict[str, Any]]:
    """
    Get preview of what will be deleted for a user.
    
    Args:
        username: Username to preview deletion for.
        
    Returns:
        Dictionary with deletion impact information.
    """
```

## Security Features

### Access Control

- Route-level authentication with `@login_required`
- Admin-only routes with `@admin_required`
- User context validation
- Session-based authentication

### Data Protection

- User-specific data access
- Admin privilege verification
- Input validation and sanitization
- CSRF protection via Flask session

## Flash Messages

The module uses consistent flash message categories:

```python
# Success messages
flash("Settings saved successfully!", "success")
flash("User created successfully!", "success")

# Error messages  
flash("Invalid theme selection.", "error")
flash("User not found.", "error")

# Info messages
flash("Switched to user view", "info")
flash("Returned to admin view", "info")
```

## Template Integration

### Base Template Variables

All routes provide base template variables:

```python
# User context
'current_user': str,
'is_admin': bool,
'display_name': str,
'is_switching': bool,

# Theme context
'current_theme': str,
'current_markdown_theme': str,
'available_themes': Dict
```

### Navigation Context

```python
# Navigation state
'active_page': str,  # Current page identifier
'show_admin_menu': bool,
'user_switching_active': bool
```

## Error Handling

### Common Error Responses

```python
# User not found (404)
if not user_manager.get_user(username):
    return render_template('user_not_found.html'), 404

# Access denied (403)
if not session.get('is_admin'):
    return render_template('access_denied.html'), 403

# Configuration error
try:
    config_loader.save_app_config()
except Exception as e:
    flash(f"Error saving settings: {e}", "error")
```

## Configuration Integration

### Settings Management

```python
# Load current settings
app_config = config_loader.app_config

# Update settings
app_config['app']['theme'] = new_theme
app_config['app']['markdown_theme'] = new_markdown_theme

# Save changes
config_loader.save_app_config()
```

### Theme Validation

```python
def validate_theme(theme_name: str) -> bool:
    """Validate theme exists in available themes."""
    available_themes = config_loader.themes_config.get('themes', {})
    return theme_name in available_themes
```

## Testing Support

### Route Testing

```python
def test_home_page(authenticated_client):
    response = authenticated_client.get('/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_settings_update(authenticated_client):
    response = authenticated_client.post('/settings', data={
        'theme': 'darkly',
        'markdown_theme': 'flatly'
    })
    assert response.status_code == 302

def test_admin_user_list(authenticated_admin_client):
    response = authenticated_admin_client.get('/users')
    assert response.status_code == 200
```

### Context Testing

```python
def test_dashboard_context(authenticated_client):
    with authenticated_client.application.test_request_context():
        # Test context variables
        response = authenticated_client.get('/')
        # Verify context data
```

## Performance Considerations

- Cached user statistics calculation
- Lazy loading of user data
- Efficient theme loading
- Minimal database queries per request

## Future Enhancements

Planned improvements:

- User profile editing
- Advanced user statistics
- Settings export/import
- User activity logging
- Dashboard customization
- Bulk user operations

## Next Steps

- [Authentication Module](auth.md) - User authentication system
- [Links Module](links.md) - Link management functionality
- [Utilities](utils.md) - Configuration and user management 