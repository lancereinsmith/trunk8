# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Trunk8 project.

## Workflows

### 🧪 Tests (`tests.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- **test**: Runs the full test suite with coverage reporting
  - Uses Python 3.12
  - Installs dependencies with `uv`
  - Runs linting with `flake8`
  - Executes tests with `pytest`
  - Uploads coverage to Codecov
- **security**: Performs security scanning
  - Runs `bandit` for Python security analysis
  - Uploads security scan results as artifacts
- **build**: Tests Docker image building
  - Builds Docker image to ensure Dockerfile is valid
  - Uses Docker layer caching for efficiency

### 📚 Documentation (`docs.yml`)

Runs when documentation files are changed.

**Jobs:**
- **build-docs**: Builds documentation with MkDocs
  - Validates all documentation can be built
  - Uploads documentation artifacts
- **deploy-docs**: Deploys to GitHub Pages (main branch only)
  - Automatically deploys documentation on main branch pushes
  - Uses `mkdocs gh-deploy` for GitHub Pages deployment

### 🐳 Docker (`docker.yml`)

Builds and publishes Docker images.

**Jobs:**
- **build-and-push**: 
  - Builds multi-architecture images (amd64, arm64)
  - Pushes to GitHub Container Registry (`ghcr.io`)
  - Creates proper tags for releases and branches
  - Uses GitHub Actions cache for faster builds

**Image Tags:**
- `latest` - Latest main branch
- `main` - Main branch builds
- `v1.2.3` - Release tags
- `pr-123` - Pull request builds (not pushed)

### 🤖 Dependabot (`dependabot.yml`)

Automatically creates pull requests for dependency updates.

**Updates:**
- **Python dependencies** - Weekly on Mondays
- **GitHub Actions** - Weekly on Mondays  
- **Docker base images** - Weekly on Mondays

## Usage

### Running Tests Locally

```bash
# Install dependencies
uv sync --extra dev

# Run tests
source .venv/bin/activate
pytest --cov=app

# Run linting
flake8 app/

# Run security checks
bandit -r app/
```

### Building Documentation Locally

```bash
# Install docs dependencies
uv sync --extra docs

# Serve docs locally
source .venv/bin/activate
mkdocs serve

# Build docs
mkdocs build
```

### Building Docker Image Locally

```bash
# Build image
docker build -t trunk8:local .

# Run container
docker run -p 5001:5001 trunk8:local
```

## Configuration

### Secrets Required

The workflows require these repository secrets:

- `GITHUB_TOKEN` - Automatically provided by GitHub
- `CODECOV_TOKEN` - Optional, for Codecov integration

### Branch Protection

Recommended branch protection rules for `main`:

- Require status checks to pass before merging
- Require branches to be up to date before merging
- Required status checks:
  - `test`
  - `security`
  - `build`
  - `build-docs`

### GitHub Pages

To enable documentation deployment:

1. Go to repository Settings → Pages
2. Set Source to "Deploy from a branch"
3. Select `gh-pages` branch
4. Documentation will be available at `https://username.github.io/trunk8`

## Troubleshooting

### Failed Tests

Check the test logs in the GitHub Actions tab. Common issues:

- Missing dependencies: Ensure `pyproject.toml` is up to date
- Test failures: Run tests locally to debug
- Coverage issues: Add tests for new code

### Failed Docker Build

- Check Dockerfile syntax
- Ensure all required files are included
- Verify base image is available

### Failed Documentation Build

- Check MkDocs configuration in `mkdocs.yml`
- Ensure all referenced files exist
- Validate Markdown syntax

### Dependabot Issues

- Check if dependencies have breaking changes
- Review and test dependency updates before merging
- Update version constraints if needed 