# Development Setup

This guide will help you set up a development environment for contributing to Trunk8.

## Prerequisites

- Python 3.12 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)
- Basic knowledge of Flask and Python

## Setting Up Your Environment

### 1. Fork and Clone

First, fork the repository on GitHub, then:

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/trunk8.git
cd trunk8

# Add upstream remote
git remote add upstream https://github.com/lancereinsmith/trunk8.git
```

### 2. Install uv (Recommended)

We recommend using [uv](https://github.com/astral-sh/uv) for faster dependency management:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv
# Or, `uv sync --group dev` will create a virtual environment  
# and install dependencies in one step.

source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using standard Python
python -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
# Using uv (install all development dependencies)
uv sync --group dev

# Or using pip (install all development dependencies)
pip install -e .[dev]
```

**Available dependency groups:**

- `uv sync` or `pip install -e .` - Runtime dependencies only
- `uv sync --group test` or `pip install -e .[test]` - With testing tools
- `uv sync --group docs` or `pip install -e .[docs]` - With documentation tools
- `uv sync --group dev` or `pip install -e .[dev]` - All development dependencies

### 5. Set Up Environment Variables

Create a `.env` file for development:

```bash
# .env
TRUNK8_ADMIN_PASSWORD=admin # Change in production
TRUNK8_SECRET_KEY=your-secret-key #Change in production
TRUNK8_LOG_LEVEL=INFO
TRUNK8_PORT=5001
```

### 6. Verify Installation

```bash
# Run the development server
python run.py

# Run tests
pytest

# Check code coverage
pytest --cov=app
```

## Development Tools

### IDE Setup

#### VS Code

Recommended extensions:

- Python
- Pylance
- Python Test Explorer
- TOML Language Support
- Flask Snippets

`.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

#### PyCharm

1. Open project
2. Configure Python interpreter to use `.venv`
3. Enable Flask support in project settings
4. Configure pytest as test runner

### Code Quality Tools

#### Linting

```bash
# Install linting tools using uv:
uv pip install pylint black isort mypy

# Or using pip:
pip install pylint black isort mypy

# Run linters
pylint app/
black app/
isort app/
mypy app/
```

#### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

Install:

```bash
pip install pre-commit
pre-commit install
```

## Project Structure

```text
trunk8/
├── app/                    # Main application package
│   ├── __init__.py        # Application factory
│   ├── auth/              # Authentication blueprint
│   ├── links/             # Links management blueprint
│   ├── main/              # Main routes blueprint
│   ├── utils/             # Utility modules
│   ├── static/            # CSS, JS, images
│   └── templates/         # Jinja2 templates
├── tests/                 # Test files
├── docs/                  # Documentation (MkDocs)
├── run.py                 # Application entry point
├── config/
│   ├── config.toml        # App configuration
│   └── themes.toml        # Available themes
├── links.toml             # Links data storage
├── pyproject.toml         # Project metadata
├── Dockerfile             # Docker configuration
└── mkdocs.yml            # Documentation config
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/add-new-feature
```

### 2. Make Changes

Follow these guidelines:

- Write clean, documented code
- Add type hints
- Follow PEP 8 style guide
- Update tests
- Update documentation

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_links.py

# Run with coverage
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
# xdg-open htmlcov/index.html  # Linux
# start htmlcov/index.html  # Windows
```

### 4. Test Manually

```bash
# Start development server
python run.py

# Test different scenarios:
# - Create various link types
# - Test expiration
# - Try different themes
# - Check error handling
```

### 5. Update Documentation

```bash
# Start documentation server
mkdocs serve

# View at http://localhost:8000
```

### 6. Commit and Push

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of changes"

# Push to your fork
git push origin feature/add-new-feature
```

### 7. Create Pull Request

1. Go to GitHub
2. Create pull request from your branch
3. Fill out PR template
4. Wait for review

## Common Development Tasks

### Adding a New Route

1. Add route to appropriate blueprint:

```python
# app/links/routes.py
@links_bp.route('/new-route')
@login_required
def new_route():
    return render_template('new_route.html')
```

1. Create template in `app/templates/`
2. Add tests in `tests/`
3. Update documentation

### Adding a New Configuration Option

1. Update `ConfigLoader` in `app/utils/config_loader.py`
2. Add default value
3. Document in configuration guide
4. Add tests

### Modifying Templates

1. Edit template in `app/templates/`
2. Use Jinja2 template inheritance
3. Test with different themes
4. Check mobile responsiveness

### Adding Tests

Create test file in `tests/`:

```python
# tests/test_new_feature.py
import pytest
from app import create_app

class TestNewFeature:
    def test_feature_works(self, client):
        response = client.get('/new-route')
        assert response.status_code == 200
```

## Debugging

### Flask Debug Mode

Debug mode is enabled by default in development:

```python
# run.py
if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

### Using Debugger

#### VS Code

1. Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_ENV": "development"
            },
            "args": ["run", "--port", "5001"],
            "jinja": true
        }
    ]
}
```

1. Set breakpoints
2. Press F5 to start debugging

#### PyCharm

1. Right-click `run.py`
2. Select "Debug 'run'"
3. Set breakpoints as needed

### Logging

Add logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

## Performance Profiling

### Using Flask-Profiler

```bash
pip install flask-profiler
```

Add to your code:

```python
from flask_profiler import Profiler

profiler = Profiler()
profiler.init_app(app)
```

### Memory Profiling

```bash
pip install memory-profiler

# Run with profiling
python -m memory_profiler run.py
```

## Database Development (Future)

When and if database support is added:

### Migrations

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Add user table"

# Apply migration
flask db upgrade
```

### Testing with Database

```python
# tests/conftest.py
@pytest.fixture
def db_session():
    # Create test database
    # Yield session
    # Cleanup
```

## Documentation Development

### Writing Docs

1. Use Markdown format
2. Follow existing structure
3. Include code examples

### Building Docs

```bash
# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Troubleshooting Development Issues

### Import Errors

```bash
# Ensure you're in virtual environment
which python  # Should show .venv path

# Reinstall in development mode
pip install -e .
```

### Test Failures

```bash
# Run single test for debugging
pytest tests/test_file.py::test_name -v

# Show print statements
pytest -s
```

### Configuration Issues

```bash
# Check TOML syntax
python -m toml config/config.toml

# Reset to defaults
rm config/config.toml links.toml
# Files recreated on next run
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [TOML Specification](https://toml.io/)

## Next Steps

- Read [Contributing Guide](contributing.md)
- Review [Architecture](architecture.md)
- Explore [Testing Guide](testing.md)
- Check [API Reference](../api/overview.md)
