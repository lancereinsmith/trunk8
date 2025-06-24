# Contributing to Trunk8

Thank you for your interest in contributing to Trunk8! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the community's best interests

## Ways to Contribute

### Reporting Bugs

Found a bug? Please help us fix it!

1. **Check existing issues** first to avoid duplicates
2. **Create a new issue** with:
    - Clear, descriptive title
    - Steps to reproduce
    - Expected vs actual behavior
    - System information (Python version, OS, etc.)
    - Error messages or logs
 
Example bug report:
```markdown
**Description:**
Links with special characters in markdown content fail to render.

**Steps to reproduce:**
1. Create a markdown link
2. Add content with `<script>` tags
3. Access the link

**Expected:** Markdown renders with escaped HTML
**Actual:** Page shows error 500

**Environment:**
- Python 3.12.1
- macOS 14.0
- Firefox 120.0
```

### Suggesting Features

Have an idea for improvement?

1. **Check existing issues** and discussions
2. **Open a discussion** to gauge interest
3. **Create a feature request** with:
    - Use case description
    - Proposed solution
    - Alternative approaches
    - Mockups or examples (if applicable)

### Contributing Code

Ready to code? Great! Here's how:

#### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR-USERNAME/trunk8.git
cd trunk8
git remote add upstream https://github.com/lancereinsmith/trunk8.git
```

#### 2. Set Up Development Environment

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --extra dev

# Activate environment
source .venv/bin/activate
```

#### 3. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

#### 4. Make Your Changes

Follow these guidelines:

##### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions focused and small
- Use meaningful variable names

Example:
```python
from typing import Optional, Dict, Any

def create_link(
    short_code: str, 
    link_data: Dict[str, Any]
) -> Optional[Link]:
    """
    Create a new link with the given short code and data.
    
    Args:
        short_code: Unique identifier for the link.
        link_data: Dictionary containing link type and properties.
        
    Returns:
        Link object if successful, None if short code exists.
        
    Raises:
        ValueError: If link_data is invalid.
    """
    # Implementation
```

##### Testing

Add tests for new functionality:

```python
# tests/test_links.py
def test_create_link_with_expiration():
    """Test creating a link with expiration date."""
    link_data = {
        'type': 'redirect',
        'url': 'https://example.com',
        'expiration_date': '2024-12-31T23:59:59'
    }
    link = Link('test', link_data)
    assert not link.is_expired
```

Run tests:
```bash
pytest
pytest --cov=app  # With coverage
```

##### Documentation

- Update docstrings
- Add/update user documentation
- Include examples
- Update README if needed

#### 5. Commit Your Changes

Write clear commit messages:

```bash
# Good
git commit -m "Add expiration date validation for links"

# Better (multi-line)
git commit -m "Add expiration date validation for links

- Validate ISO format for expiration dates
- Show error message for invalid formats
- Add tests for edge cases
- Update documentation

Fixes #123"
```

Commit message guidelines:

- Start with a verb (Add, Fix, Update, Remove)
- Keep first line under 50 characters
- Add detailed description if needed
- Reference issues with "Fixes #123"

#### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

On GitHub:

1. Click "New Pull Request"
2. Select your branch
3. Fill out the PR template
4. Request reviews if you know relevant reviewers

Pull Request checklist:

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Reviewing Pull Requests

Help review other contributions:

1. **Test the changes** locally
2. **Review code** for:
    - Correctness
    - Style consistency
    - Test coverage
    - Documentation
3. **Provide feedback**:
    - Be constructive
    - Suggest specific improvements
    - Acknowledge good work

## Development Guidelines

### Project Structure

Understand the codebase:

```
trunk8/
├── app/                 # Main application
│   ├── auth/           # Authentication
│   ├── links/          # Link management
│   ├── main/           # Main routes
│   ├── utils/          # Utilities
│   ├── static/         # CSS, JS, images
│   └── templates/      # HTML templates
├── config/              # Configuration files
├── tests/              # Test files
├── docs/               # Documentation
└── run.py             # Entry point
```

### Adding New Features

1. **Discuss first** - Open an issue or discussion
2. **Design** - Plan the implementation
3. **Implement** - Follow coding standards
4. **Test** - Add comprehensive tests
5. **Document** - Update all relevant docs

### Dependencies

When adding dependencies:

1. **Justify the need** - Avoid unnecessary dependencies
2. **Check licenses** - Ensure compatibility
3. **Update pyproject.toml**:
   ```toml
   dependencies = [
       "new-package>=1.0.0",
   ]
   ```
4. **Run `uv sync --extra dev`** to update lock file
5. **Document** usage and purpose

### Database Migration (Future)

If implementing database support:

1. Use SQLAlchemy with Alembic
2. Keep migrations compatible with existing data
3. Provide migration documentation
4. Test with production data volumes

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_links.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Writing Tests

Test categories:
- **Unit tests** - Test individual functions
- **Integration tests** - Test component interactions
- **End-to-end tests** - Test complete workflows

Example test structure:
```python
import pytest
from app.links.models import Link

class TestLink:
    """Test Link model functionality."""
    
    def test_link_creation(self):
        """Test basic link creation."""
        # Arrange
        link_data = {'type': 'redirect', 'url': 'http://example.com'}
        
        # Act
        link = Link('test', link_data)
        
        # Assert
        assert link.short_code == 'test'
        assert link.type == 'redirect'
    
    def test_expired_link(self):
        """Test link expiration detection."""
        # Test implementation
```

### Test Coverage

Aim for:

- 80%+ overall coverage
- 100% coverage for critical paths
- Test edge cases and error conditions

## Documentation

### Types of Documentation

1. **Code Documentation**
    - Docstrings for all public functions
    - Type hints for clarity
    - Inline comments for complex logic

2. **User Documentation**
    - Clear examples
    - Common use cases
    - Troubleshooting guides

3. **API Documentation**
    - Endpoint descriptions
    - Request/response examples
    - Error codes

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## Release Process

### Version Numbering

We follow Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR** - Breaking changes
- **MINOR** - New features (compatible with existing installations)
- **PATCH** - Bug fixes

### Release Steps

1. Update version in `pyproject.toml`
2. Update CHANGELOG
3. Create release PR
4. Tag release after merge
5. Build and publish Docker image

## Getting Help

### Resources

- [Documentation](https://trunk8.readthedocs.io)
- [GitHub Issues](https://github.com/lancereinsmith/trunk8/issues)
- [Discussions](https://github.com/lancereinsmith/trunk8/discussions)

### Communication

- **Issues** - Bug reports and feature requests
- **Discussions** - Questions and ideas
- **Pull Requests** - Code contributions

## Recognition

Contributors are recognized in:

- GitHub contributors page
- Release notes
- Documentation credits

Thank you for contributing to Trunk8! 🎉 