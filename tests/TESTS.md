# Trunk8 Test Suite

This directory contains the comprehensive test suite for the Trunk8 link shortener application.

## Test Structure

The test suite is organized into the following modules:

- **`test_auth.py`**: Tests for authentication functionality (login, logout, session management)
- **`test_links.py`**: Tests for link management (creation, retrieval, editing, deletion, expiration)
- **`test_main.py`**: Tests for main routes (index, settings, theme management)
- **`test_config_loader.py`**: Tests for configuration loading and saving utilities
- **`test_models.py`**: Tests for data models (Link model)
- **`test_integration.py`**: End-to-end integration tests for complete workflows

## Running the Tests

### Install Dependencies

First, ensure all dependencies are installed:

```bash
# Using pip
pip install -e .

# Or using uv (if you have it installed)
uv pip install -e .
```

### Run All Tests

```bash
# Run all tests with coverage report
pytest

# Run tests with more verbose output
pytest -v

# Run tests and show print statements
pytest -s
```

### Run Specific Test Files

```bash
# Run only authentication tests
pytest tests/test_auth.py

# Run only link management tests
pytest tests/test_links.py
```

### Run Tests by Category

Tests are marked with different categories:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run all tests except slow ones
pytest -m "not slow"
```

### Coverage Reports

```bash
# Generate coverage report in terminal
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

### Test-Specific Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run tests and stop on first failure
pytest -x

# Run only tests that failed in the last run
pytest --lf

# Run tests matching a specific pattern
pytest -k "test_login"
```

## Environment Variables for Testing

The test suite uses the following environment variables:

- `TRUNK8_SECRET_KEY`: Set to `test_secret_key` for tests
- `TRUNK8_ADMIN_PASSWORD`: Set to `test_password` for tests

These are automatically set by the test fixtures.

## Test Fixtures

The test suite provides several useful fixtures in `conftest.py`:

- **`app`**: A configured Flask application instance for testing
- **`client`**: A Flask test client for making requests
- **`authenticated_client`**: A pre-authenticated test client
- **`config_loader`**: A ConfigLoader instance with test configurations
- **`populated_links`**: A ConfigLoader with pre-populated test links
- **`sample_links`**: Sample link data for testing
- **`temp_dir`**: A temporary directory for test files
- **`test_config_files`**: Set of temporary config files for testing

## Writing New Tests

When adding new tests:

1. Place them in the appropriate test file based on functionality
2. Use descriptive test names that explain what is being tested
3. Use appropriate fixtures to avoid code duplication
4. Add docstrings to test functions explaining the test scenario
5. Mark integration tests with `@pytest.mark.integration`
6. Clean up any created resources (files, links) at the end of tests

## Debugging Tests

If a test fails:

1. Run the specific test with `-v` for verbose output
2. Use `-s` to see print statements
3. Add `pytest.set_trace()` in the test to drop into a debugger
4. Check the test's use of fixtures and assertions
5. Verify the test environment is properly isolated

## Continuous Integration

The test suite is designed to run in CI environments. Make sure:

- All tests pass locally before pushing
- Tests don't depend on external services
- Tests clean up after themselves
- Tests use temporary directories and files
- Tests are isolated and can run in any order 