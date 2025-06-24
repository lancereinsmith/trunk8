# Application Factory (app)

The main application module contains the Flask application factory and core configuration.

## Overview

The `app` module provides the main entry point for creating and configuring the Trunk8 Flask application. It implements the application factory pattern for better testing and deployment flexibility.

## Main Functions

### create_app()

```python
def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create Flask application instance with configuration.

    Args:
        config_name: Configuration name (not used currently, reserved for future).

    Returns:
        Flask: Configured Flask application instance.
    """
```

Creates and configures a Flask application instance with:

- Configuration loading via `ConfigLoader`
- User management via `UserManager`
- Blueprint registration
- Template context processors
- Request handlers
- Jinja2 filters

**Usage:**
```python
from app import create_app

app = create_app()
app.run(debug=True, port=5001)
```

## Configuration Functions

### _configure_app()

```python
def _configure_app(app: Flask, app_config: Dict[str, Any]) -> None:
    """
    Configure Flask app with settings from TOML config.

    Args:
        app: Flask application instance to configure.
        app_config: Dictionary containing application configuration data.
    """
```

Configures:

- Secret key from environment variable or default
- Session lifetime from config

### _register_blueprints()

```python
def _register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Args:
        app: Flask application instance.
    """
```

Registers blueprints:

- `auth_bp` - Authentication routes
- `backup_bp` - Backup/restore functionality  
- `links_bp` - Link management
- `main_bp` - Main application routes

## Context Processors

### inject_user_context()

Provides user information to all templates:

- Current username
- Admin status
- Display name
- Active user (for user switching)

### inject_theme_context()

Provides theme information to all templates:

- Current UI theme
- Current markdown theme
- Available themes list

## Request Handlers

### load_user_context()

Executed before each request:

- Loads current user context
- Sets user context in configuration loader
- Reloads configs for current user

### cleanup_expired_links()

Executed before each request:

- Checks for expired links
- Removes expired links automatically
- Cleans up associated files

## Jinja2 Filters

### to_datetime

```python
@app.template_filter("to_datetime")
def to_datetime_filter(date_string):
    """Convert datetime string to datetime object."""
```

Converts ISO datetime strings to Python datetime objects for template use.

### datetime_local

```python
@app.template_filter("datetime_local")
def datetime_local_filter(dt):
    """Format datetime object for datetime-local input."""
```

Formats datetime objects for HTML datetime-local inputs.

## Application Structure

```python
# Application initialization flow
app = Flask(__name__)
config_loader = ConfigLoader()
user_manager = UserManager()



# Load all configurations
config_loader.load_all_configs()

# Configure Flask application
_configure_app(app, config_loader.app_config)

# Make utilities available
app.config_loader = config_loader
app.user_manager = user_manager

# Set up components
_register_blueprints(app)
_setup_context_processors(app)
_setup_before_request_handlers(app)
_setup_jinja_filters(app)
```

## Configuration Access

The application provides access to configuration and user management:

```python
# Access configuration loader
config_loader = app.config_loader

# Access user manager  
user_manager = app.user_manager

# Get current app config
app_config = config_loader.app_config

# Get user-specific links config
links_config = config_loader.links_config
```

## Environment Variables

The application reads these environment variables:

- `TRUNK8_SECRET_KEY` - Flask session secret key
- `TRUNK8_ADMIN_PASSWORD` - Admin password for authentication
- `TRUNK8_LOG_LEVEL` - Logging level
- `TRUNK8_PORT` - Port the development server runs on (in production, use gunicorn or other web server)


## Error Handling

The application factory includes error handling for:

- Missing configuration files
- Invalid TOML syntax
- Permission errors

## Testing Support

The application factory supports testing with:

- Configurable test settings
- Isolated test configurations
- Mock configuration loaders

**Example:**
```python
def test_app_creation():
    app = create_app()
    assert app is not None
    assert 'config_loader' in dir(app)
    assert 'user_manager' in dir(app)
```

## Development vs Production

The application factory automatically detects environment:

```python
# Development
app.run(debug=True, port=5001)

# Production  
gunicorn run:app --bind 0.0.0.0:5001
```

## Extension Points

The application factory provides hooks for:

- Custom blueprints
- Additional context processors
- Custom Jinja2 filters
- Extra request handlers

## Next Steps

- [Authentication Module](auth.md) - User authentication system
- [Links Module](links.md) - Link management functionality
- [Configuration](utils.md) - Configuration and user management 