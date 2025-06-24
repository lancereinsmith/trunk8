# API Reference Overview

This section provides detailed API documentation for Trunk8's Python modules. The documentation is automatically generated from docstrings in the source code.

## Module Structure

Trunk8 is organized into the following main modules:

### Core Modules

- **[app](app.md)** - Application factory and initialization
- **[app.auth](auth.md)** - Authentication and session management
- **[app.backup](backup.md)** - Backup and restore functionality
- **[app.links](links.md)** - Link management functionality
- **[app.main](main.md)** - Main application routes
- **[app.utils](utils.md)** - Utility functions and helpers

### Module Hierarchy

```
app/
├── __init__.py          # Application factory
├── auth/
│   ├── __init__.py      # Auth blueprint
│   ├── decorators.py    # Login required decorator
│   └── routes.py        # Login/logout routes
├── backup/
│   ├── __init__.py      # Backup blueprint
│   └── routes.py        # Backup/restore routes
├── links/
│   ├── __init__.py      # Links blueprint
│   ├── models.py        # Link data model
│   ├── routes.py        # CRUD routes
│   └── utils.py         # Link utilities
├── main/
│   ├── __init__.py      # Main blueprint
│   └── routes.py        # Home and settings
└── utils/
    ├── __init__.py      # Utils module
    ├── config_loader.py # Configuration management
    └── user_manager.py  # User management
```

## Key Functions and Classes

### Application Factory

The main application factory function creates and configures the Flask application:

```python
def create_app(config_name: Optional[str] = None) -> Flask:
    """Create Flask application instance with configuration."""
```

### Authentication System

Multi-user authentication with admin privileges:

```python
class UserManager:
    """Manages user accounts, authentication, and user-specific data access."""
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password."""
```

### Configuration Management

TOML-based configuration with automatic reloading:

```python
class ConfigLoader:
    """Manages TOML configuration files with automatic reloading."""
    
    def load_all_configs(self) -> None:
        """Load all configuration files."""
```

### Link Management

Core link handling functionality:

```python
class Link:
    """Represents a shortened link with metadata."""
    
    def is_expired(self) -> bool:
        """Check if link has expired."""
```

## Blueprint Routes

### Authentication Routes (`/auth`)

| Route | Method | Description |
|-------|--------|-------------|
| `/auth/login` | GET, POST | User login page and handler |
| `/auth/logout` | GET | Logout handler |
| `/auth/register` | GET, POST | User registration (admin only) |
| `/auth/switch-user/<username>` | GET | Switch user context (admin only) |
| `/auth/switch-back` | GET | Return to admin context |

### Link Management Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/add` | GET, POST | Add new link |
| `/links` | GET | List all links |
| `/edit_link/<code>` | GET, POST | Edit existing link |
| `/delete_link/<code>` | POST | Delete link |
| `/<code>` | GET | Access/redirect to link |

### Backup Routes (`/backup`)

| Route | Method | Description |
|-------|--------|-------------|
| `/backup/create` | GET, POST | Create and download backup archive (ZIP file) |
| `/backup/restore` | GET, POST | Upload and restore from backup archive |

### Main Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page |
| `/settings` | GET, POST | Settings interface |
| `/users` | GET | User management (admin only) |
| `/users/<username>` | GET | User details (admin only) |
| `/profile` | GET | Current user profile |

## Data Models

### Link Model

```python
class Link:
    """
    Represents a shortened link with metadata.
    
    Attributes:
        short_code: Unique identifier for the link
        type: Link type ('redirect', 'file', 'markdown')
        url: Target URL for redirect links
        path: File path for file/markdown links
        expiration_date: Optional expiration timestamp
    """
```

### User Context

```python
# User session data structure
{
    "authenticated": bool,
    "username": str,
    "is_admin": bool,
    "display_name": str,
    "active_user": str,  # For user switching
    "active_display_name": str
}
```

## Configuration Structure

### Application Config (`config/config.toml`)

```toml
[app]
theme = "cerulean"
markdown_theme = "cerulean"

max_file_size_mb = 100

[session]
permanent_lifetime_days = 30
```

### User Data (`users/users.toml`)

```toml
[users.username]
password_hash = "hashed_password"
is_admin = true
display_name = "Display Name"
created_at = "2024-01-01T00:00:00"
```

### Links Data (`users/{username}/links.toml`)

```toml
[links.shortcode]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"
```

## Error Handling

Standard HTTP responses:

- `200` - Success
- `302` - Redirect (after successful operations)
- `401` - Unauthorized (login required)
- `403` - Forbidden (admin required)
- `404` - Not found (invalid link)
- `500` - Server error

## Security Features

- Password-based authentication
- Session management with configurable lifetime
- Admin privilege system
- User data isolation
- Secure file naming
- Input validation and sanitization

## Extending the API

### Adding New Routes

1. Create route in appropriate blueprint:
```python
@links_bp.route('/api/links', methods=['GET'])
@login_required
def api_list_links():
    """API endpoint to list links."""
    links = get_user_links()
    return jsonify(links)
```

2. Add authentication if needed:
```python
from .auth.decorators import login_required, admin_required
```

3. Handle errors appropriately:
```python
try:
    result = process_request()
    return jsonify(result)
except Exception as e:
    return jsonify({'error': str(e)}), 400
```

### Creating New Modules

1. Create module directory with `__init__.py`
2. Define blueprint if needed
3. Register in application factory
4. Add documentation

## Development Guidelines

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description explaining what the function does,
    any important details, and usage examples.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When invalid input is provided.
    """
    pass
```

### Type Hints

All functions should include type hints:

```python
from typing import Dict, List, Optional, Any, Union

def process_links(
    links: List[Dict[str, Any]], 
    filter_expired: bool = True
) -> Optional[List[Link]]:
    """Process and optionally filter links."""
    pass
```

## Testing

### Unit Tests

Test individual functions:
```python
def test_link_creation():
    link = Link('test', {'type': 'redirect', 'url': 'http://example.com'})
    assert link.short_code == 'test'
    assert link.type == 'redirect'
```

### Integration Tests

Test complete workflows:
```python
def test_add_link_workflow(authenticated_client):
    response = authenticated_client.post('/add', data={
        'short_code': 'test',
        'link_type': 'redirect',
        'url': 'http://example.com'
    })
    assert response.status_code == 302
```

## Performance Considerations

- Configuration caching (implemented)
- Lazy loading of resources
- Efficient file handling
- Session optimization
- Database-ready architecture (future)

## Next Steps

Explore specific modules:

- [Application Factory](app.md) - Core application setup
- [Authentication](auth.md) - Security implementation
- [Backup & Restore](backup.md) - Data backup and recovery
- [Links Management](links.md) - CRUD operations
- [Configuration](utils.md) - Settings management 