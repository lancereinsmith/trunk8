# Testing Guide

This guide covers testing practices and procedures for Trunk8 development.

## Testing Philosophy

Trunk8 follows these testing principles:
- Test behavior, not implementation
- Aim for high coverage but prioritize critical paths
- Write tests before fixing bugs
- Keep tests simple and readable
- Use descriptive test names

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_auth.py         # Authentication tests
├── test_config_loader.py # Configuration tests
├── test_integration.py  # End-to-end tests
├── test_links.py        # Link management tests
├── test_main.py         # Main routes tests
└── test_models.py       # Data model tests
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with output
pytest -v

# Run specific file
pytest tests/test_links.py

# Run specific test
pytest tests/test_links.py::test_add_link

# Run tests matching pattern
pytest -k "test_redirect"

# Stop on first failure
pytest -x
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=app

# Generate HTML report
pytest --cov=app --cov-report=html

# Show missing lines
pytest --cov=app --cov-report=term-missing

# Coverage with branches
pytest --cov=app --cov-branch
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration
```

## Writing Tests

### Test File Structure

```python
"""Tests for link management functionality."""
import pytest
from datetime import datetime, timedelta
from app.links.models import Link

class TestLinkModel:
    """Test Link model functionality."""
    
    def test_link_creation(self):
        """Test creating a basic link."""
        link = Link('test', {'type': 'redirect', 'url': 'http://example.com'})
        assert link.short_code == 'test'
        assert link.type == 'redirect'
        assert link.url == 'http://example.com'
    
    def test_link_expiration(self):
        """Test link expiration detection."""
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        link = Link('expired', {
            'type': 'redirect',
            'url': 'http://example.com',
            'expiration_date': past_date
        })
        assert link.is_expired is True
```

### Using Fixtures

```python
# conftest.py
import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    client.post('/auth/login', data={'password': 'admin'})
    return client

@pytest.fixture
def sample_link():
    """Create sample link data."""
    return {
        'short_code': 'test',
        'link_type': 'redirect',
        'url': 'https://example.com'
    }
```

### Testing Routes

```python
def test_home_redirects_to_login(client):
    """Test unauthenticated access redirects to login."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_home_with_auth(authenticated_client):
    """Test authenticated access to home page."""
    response = authenticated_client.get('/')
    assert response.status_code == 200
    assert b'Welcome to Trunk8' in response.data

def test_add_link(authenticated_client, sample_link):
    """Test adding a new link."""
    response = authenticated_client.post('/add', data=sample_link)
    assert response.status_code == 302
    
    # Verify link was created
    response = authenticated_client.get(f"/{sample_link['short_code']}")
    assert response.status_code == 302
```

### Testing Forms

```python
def test_login_form_validation(client):
    """Test login form with invalid data."""
    # Empty password
    response = client.post('/auth/login', data={'password': ''})
    assert response.status_code == 200
    assert b'Password is required' in response.data
    
    # Wrong password
    response = client.post('/auth/login', data={'password': 'wrong'})
    assert response.status_code == 200
    assert b'Invalid password' in response.data

def test_link_form_validation(authenticated_client):
    """Test link form validation."""
    # Missing required fields
    response = authenticated_client.post('/add', data={})
    assert response.status_code == 200
    assert b'Short code is required' in response.data
    
    # Invalid link type
    response = authenticated_client.post('/add', data={
        'short_code': 'test',
        'link_type': 'invalid'
    })
    assert response.status_code == 200
    assert b'Invalid link type' in response.data
```

### Testing File Uploads

```python
def test_file_upload(authenticated_client):
    """Test file upload functionality."""
    data = {
        'short_code': 'testfile',
        'link_type': 'file',
        'file': (io.BytesIO(b"test content"), 'test.txt')
    }
    
    response = authenticated_client.post('/add', 
        data=data, 
        content_type='multipart/form-data'
    )
    assert response.status_code == 302
    
    # Verify file link works
    response = authenticated_client.get('/testfile')
    assert response.status_code == 200
    assert response.data == b"test content"
```

### Testing Configuration

```python
def test_config_loading(app):
    """Test configuration loading."""
    config_loader = app.config_loader
    
    # Test default values
    assert config_loader.app_config['app']['theme'] == 'cerulean'
    assert config_loader.app_config['app']['asset_folder'] == 'assets'
    
    # Test config reload
    original_mod_time = config_loader._last_app_config_mod_time
    config_loader.load_configs()
    assert config_loader._last_app_config_mod_time == original_mod_time

def test_theme_validation(app):
    """Test theme validation."""
    config_loader = app.config_loader
    valid_themes = config_loader.available_themes
    
    assert 'cosmo' in valid_themes
    assert 'darkly' in valid_themes
    assert 'invalid-theme' not in valid_themes
```

### Testing Models

```python
class TestLinkModel:
    """Test Link model."""
    
    def test_to_dict(self):
        """Test link serialization."""
        link = Link('test', {
            'type': 'redirect',
            'url': 'https://example.com',
            'expiration_date': '2024-12-31T23:59:59'
        })
        
        data = link.to_dict()
        assert data['type'] == 'redirect'
        assert data['url'] == 'https://example.com'
        assert 'expiration_date' in data
    
    def test_expiration_edge_cases(self):
        """Test expiration edge cases."""
        # No expiration date
        link = Link('permanent', {'type': 'redirect', 'url': 'http://example.com'})
        assert link.is_expired is False
        
        # Invalid date format
        link = Link('invalid', {
            'type': 'redirect',
            'url': 'http://example.com',
            'expiration_date': 'not-a-date'
        })
        assert link.is_expired is False
```

### Testing Error Handling

```python
def test_404_handling(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert b'Link not found' in response.data

def test_invalid_file_handling(authenticated_client):
    """Test handling of missing files."""
    # Create file link with non-existent file
    config_loader = authenticated_client.application.config_loader
    config_loader.links_config['links']['broken'] = {
        'type': 'file',
        'path': 'nonexistent.pdf'
    }
    
    response = authenticated_client.get('/broken')
    assert response.status_code == 404
```

### Integration Tests

```python
@pytest.mark.integration
class TestLinkWorkflow:
    """Test complete link workflows."""
    
    def test_full_link_lifecycle(self, authenticated_client):
        """Test creating, editing, and deleting a link."""
        # Create link
        response = authenticated_client.post('/add', data={
            'short_code': 'lifecycle',
            'link_type': 'redirect',
            'url': 'https://example.com'
        })
        assert response.status_code == 302
        
        # Edit link
        response = authenticated_client.post('/edit_link/lifecycle', data={
            'url': 'https://example.org'
        })
        assert response.status_code == 302
        
        # Verify edit
        response = authenticated_client.get('/lifecycle', follow_redirects=False)
        assert response.location == 'https://example.org'
        
        # Delete link
        response = authenticated_client.post('/delete_link/lifecycle')
        assert response.status_code == 302
        
        # Verify deletion
        response = authenticated_client.get('/lifecycle')
        assert response.status_code == 404
```

## Testing Best Practices

### Test Organization

1. **Group related tests** in classes
2. **Use descriptive names** that explain what's being tested
3. **One assertion focus** per test when possible
4. **Arrange-Act-Assert** pattern

### Test Data

```python
# Use fixtures for reusable test data
@pytest.fixture
def links_data():
    """Sample links for testing."""
    return [
        {'short_code': 'test1', 'type': 'redirect', 'url': 'http://example1.com'},
        {'short_code': 'test2', 'type': 'file', 'path': 'test.pdf'},
        {'short_code': 'test3', 'type': 'markdown', 'path': 'test.md'}
    ]

# Use factories for complex objects
def make_link(short_code='test', **kwargs):
    """Factory for creating test links."""
    defaults = {'type': 'redirect', 'url': 'http://example.com'}
    defaults.update(kwargs)
    return Link(short_code, defaults)
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_file_upload_with_mock(authenticated_client):
    """Test file upload with mocked file system."""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock()
            
            response = authenticated_client.post('/add', data={
                'short_code': 'mockfile',
                'link_type': 'file',
                'file': (io.BytesIO(b"content"), 'test.txt')
            })
            
            assert response.status_code == 302
            mock_open.assert_called()
```


## Performance Testing

### Basic Timing

```python
import time

def test_config_reload_performance():
    """Test configuration reload is fast."""
    start = time.time()
    config_loader.load_configs()
    duration = time.time() - start
    
    assert duration < 0.1  # Should complete in under 100ms
```

### Load Testing

```python
@pytest.mark.slow
def test_many_links_performance(authenticated_client):
    """Test performance with many links."""
    # Create many links
    for i in range(1000):
        authenticated_client.post('/add', data={
            'short_code': f'perf{i}',
            'link_type': 'redirect',
            'url': f'https://example.com/{i}'
        })
    
    # Test list page performance
    start = time.time()
    response = authenticated_client.get('/links')
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0  # Should load in under 2 seconds
```

## Debugging Tests

### Print Debugging

```bash
# Show print statements
pytest -s

# Verbose output
pytest -vv
```

### Using pdb

```python
def test_complex_logic():
    """Test with debugger."""
    import pdb; pdb.set_trace()
    # Debugger will stop here
    result = complex_function()
    assert result == expected
```

### Test Logs

```python
def test_with_logging(caplog):
    """Test that captures logs."""
    with caplog.at_level(logging.INFO):
        function_that_logs()
    
    assert 'Expected message' in caplog.text
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --extra dev
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Test Checklist

Before submitting PR:

- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Bug fixes include regression tests
- [ ] Coverage hasn't decreased significantly
- [ ] Integration tests for complex features
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Tests are documented

## Next Steps

- Review [Development Setup](setup.md)
- Read [Contributing Guide](contributing.md)
- Explore [Architecture](architecture.md)
- Check existing tests in `tests/` directory 