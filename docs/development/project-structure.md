# Project Structure

This document provides a detailed overview of Trunk8's project structure and file organization.

## Directory Overview

```
trunk8/
├── app/                    # Main application package
├── debug/                  # Debug utilities (optional)
├── docs/                   # MkDocs documentation
├── tests/                  # Test suite
├── users/                  # Multi-user data storage (NEW)
│   ├── users.toml         # User management data
│   ├── admin/             # Admin user data
│   │   ├── links.toml     # Admin's links
│   │   └── assets/        # Admin's files
│   └── {username}/        # Other users' data
│       ├── links.toml     # User's links
│       └── assets/        # User's files
├── config/
│   ├── config.toml        # Application configuration
│   └── themes.toml        # Available themes
├── Dockerfile             # Docker configuration
├── LICENSE                # MIT license
├── mkdocs.yml             # Documentation config
├── pyproject.toml         # Project metadata
├── pytest.ini             # Pytest configuration
├── README.md              # Project readme
├── run.py                 # Application entry point
├── TODO.md                # Development tasks
└── uv.lock                # Dependency lock file
```

## Core Application (`app/`)

### Application Package Structure

```
app/
├── __init__.py            # Application factory
├── auth/                  # Authentication blueprint
│   ├── __init__.py       # Blueprint registration
│   ├── decorators.py     # Login required decorator
│   └── routes.py         # Login/logout routes
├── links/                 # Links management blueprint
│   ├── __init__.py       # Blueprint registration
│   ├── models.py         # Link data model
│   ├── routes.py         # CRUD routes
│   └── utils.py          # Helper functions
├── main/                  # Main routes blueprint
│   ├── __init__.py       # Blueprint registration
│   └── routes.py         # Home, settings routes
├── utils/                 # Shared utilities
│   ├── __init__.py       # Module init
│   └── config_loader.py  # Configuration management
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── img/              # Images
│   └── js/               # JavaScript
└── templates/             # Jinja2 templates
```

### Key Files Explained

#### `app/__init__.py`

The application factory that:

- Creates Flask instance
- Registers blueprints
- Sets up configuration
- Defines template filters
- Handles request hooks

```python
def create_app() -> Flask:
    """Application factory pattern."""
    app = Flask(__name__)
    # Configuration and setup...
    return app
```

#### `app/auth/`

Authentication module handling:

- User login/logout
- Session management
- Access control decorators

Key components:

- `decorators.py`: `@login_required` decorator
- `routes.py`: `/auth/login` and `/auth/logout` endpoints

#### `app/links/`

Core functionality for link management:

- `models.py`: `Link` class for data representation
- `routes.py`: CRUD operations for links
- `utils.py`: File handling, expiration checks

#### `app/main/`

General application routes:

- Home page (`/`)
- Settings page (`/settings`)
- Context processors

#### `app/utils/`

Shared utilities:

- `config_loader.py`: TOML configuration management
- Automatic reloading
- Default value creation
- Multi-file support

## Static Assets (`app/static/`)

```
static/
├── css/
│   └── style.css          # Custom styles
├── img/
│   └── trunk8_logo.png    # Application logo
└── js/
    └── main.js            # Custom JavaScript
```

### Asset Organization

- **CSS**: Custom styles supplementing Bootstrap
- **Images**: Logo and UI assets
- **JavaScript**: Interactive features

## Templates (`app/templates/`)

```
templates/
├── base.html              # Base template with layout
├── index.html             # Home page
├── login.html             # Login form
├── add_link.html          # Add link form
├── edit_link.html         # Edit link form
├── list_links.html        # Links listing
├── link_created.html      # Success message
├── link_not_found.html    # 404 page
├── markdown_render.html   # Markdown display
└── settings.html          # Settings interface
```

### Template Hierarchy

- `base.html`: Master template with navbar and layout
- Other templates extend base using Jinja2 inheritance
- Consistent Bootstrap styling throughout

## Configuration Files

### `config/config.toml`

Application settings:
```toml
[app]
theme = "cerulean"
markdown_theme = "cerulean"

max_file_size_mb = 100

[session]
permanent_lifetime_days = 30
```

### User Data Storage (`users/`)

Multi-user data organization:

**`users/users.toml`** - User management:
```toml
[users.admin]
password_hash = "hashed_password"
is_admin = true
display_name = "Administrator"
created_at = "2024-01-01T00:00:00"
```

**`users/{username}/links.toml`** - Per-user links:
```toml
[links.example]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"
```

**Note**: Each user has isolated data storage in their own directory.

### `config/themes.toml`

Available themes catalog:
```toml
[themes.cosmo]
name = "Cosmo"
description = "An ode to Metro"
```

## Test Suite (`tests/`)

```
tests/
├── __init__.py            # Test package
├── conftest.py            # Pytest fixtures
├── test_auth.py           # Auth tests
├── test_config_loader.py  # Config tests
├── test_integration.py    # E2E tests
├── test_links.py          # Links tests
├── test_main.py           # Main routes tests
├── test_models.py         # Model tests
├── README.md              # Test documentation
└── TEST_RESULTS.md        # Test outcomes
```

### Test Organization

- Unit tests for individual components
- Integration tests for workflows
- Fixtures in `conftest.py` for reusability
- Clear naming convention: `test_*.py`

## Documentation (`docs/`)

```
docs/
├── index.md               # Documentation home
├── getting-started/       # Installation guides
├── user-guide/            # User documentation
├── configuration/         # Config reference
├── development/           # Developer guides
├── api/                   # API documentation
├── deployment/            # Deployment guides
└── reference/             # Additional resources
```

### Documentation Structure

- **Getting Started**: Quick installation and setup
- **User Guide**: Feature documentation
- **Configuration**: Detailed config options
- **Development**: Contributing guidelines
- **API Reference**: Code documentation
- **Deployment**: Production guides

## Project Files

### `run.py`

Application entry point:
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Get port from environment variable, default to 5001
    port = int(os.environ.get("TRUNK8_PORT", 5001))

    app.run(
        debug=True, host="0.0.0.0", port=port
    )
```

### `pyproject.toml`

Project metadata and dependencies:
```toml
[project]
name = "trunk8"
version = "0.2.0"
dependencies = [
    "flask>=3.1.1",
    "gunicorn>=23.0.0",
    # ...
]
```

### `Dockerfile`

Container configuration:
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
# Application setup...
CMD ["gunicorn", "run:app"]
```

### `mkdocs.yml`

Documentation configuration:
```yaml
site_name: Trunk8 Documentation
theme:
  name: material
# Navigation and plugins...
```

## File Naming Conventions

### Python Files
- Snake_case: `config_loader.py`
- Descriptive names: `routes.py`, `models.py`
- Test prefix: `test_*.py`

### Templates
- Snake_case: `add_link.html`
- Action-based: `edit_link.html`
- State-based: `link_created.html`

### Static Assets
- Lowercase: `style.css`, `main.js`
- Descriptive: `trunk8_logo.png`

## Import Structure

### Absolute Imports
```python
from app import create_app
from app.auth.decorators import login_required
from app.links.models import Link
```

### Relative Imports (within package)
```python
from .models import Link
from .utils import generate_filename
```

## Adding New Features

### Creating a New Blueprint

1. Create directory: `app/feature/`
2. Add `__init__.py`:
```python
from flask import Blueprint
feature_bp = Blueprint('feature', __name__)
from . import routes
```

3. Create `routes.py`
4. Register in `app/__init__.py`

### Adding Templates

1. Create template in `app/templates/`
2. Extend base template
3. Use consistent styling

### Adding Static Files

1. Place in appropriate `static/` subdirectory
2. Reference using `url_for('static', filename='...')`

## Build and Deployment

### Local Development
```bash
python run.py
```

### Production
```bash
gunicorn run:app --bind 0.0.0.0:5001
```

### Docker
```bash
docker build -t trunk8 .
docker run -p 5001:5001 trunk8
```

## Security Considerations

### Sensitive Files
- Never commit `.env` files
- Keep `config/config.toml` secure
- Protect `links.toml` data

### File Permissions
```bash
chmod 600 config/config.toml links.toml
chmod 755 assets/
```

## Maintenance

### Regular Tasks
- Clear old files from `assets/`
- Backup `*.toml` files
- Update dependencies
- Review security

### Monitoring
- Check `assets/` disk usage
- Monitor log files
- Track configuration changes

## Future Structure Changes

### Planned Additions
- `app/api/` - REST API endpoints
- `migrations/` - Database migrations
- `app/models/` - Shared data models
- `scripts/` - Utility scripts


## Development Tips

### Finding Files
```bash
# Find all route files
find . -name "routes.py"

# Find templates
find . -name "*.html"

# Search in code
grep -r "login_required" app/
```

### Making Changes
1. Identify affected components
2. Update code and tests
3. Update documentation
4. Test thoroughly

## Conclusion

This structure provides:
- Clear separation of concerns
- Easy navigation
- Scalable architecture
- Maintainable codebase

Follow the established patterns when adding new features to maintain consistency. 