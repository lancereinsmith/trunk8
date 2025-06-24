# Installation

This guide will walk you through installing Trunk8 on your system. Choose the installation method that best suits your needs.

## Prerequisites

Before installing Trunk8, ensure you have:

- **Python 3.12 or higher** - Trunk8 requires Python 3.12+
- **Git** - For cloning the repository
- **A web server** - For production deployments (optional for development)

## Installation Methods

### Option 1: Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver, written in Rust. It's the recommended way to install Trunk8.

#### 1. Install uv

=== "macOS/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

=== "Using pip"

    ```bash
    pip install uv
    ```

#### 2. Clone the Repository

```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
```

#### 3. Install Dependencies

```bash
# For production (runtime dependencies only)
uv sync

# For development (includes test and documentation dependencies)
uv sync --extra dev
```

This command will:

- Create a virtual environment in `.venv`
- Install dependencies from `pyproject.toml`
- Lock dependencies in `uv.lock` for reproducible builds

**Dependency Groups:**

- `test`: Testing tools (pytest, pytest-flask, pytest-cov, pytest-mock)
- `docs`: Documentation tools (mkdocs, mkdocs-material, mkdocstrings)
- `dev`: Convenience group that includes both test and docs dependencies

#### 4. Activate Virtual Environment

=== "macOS/Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```bash
    .venv\Scripts\activate
    ```

### Option 2: Using pip

If you prefer using pip, follow these steps:

#### 1. Clone the Repository

```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
```

#### 2. Create Virtual Environment

```bash
python -m venv .venv
```

#### 3. Activate Virtual Environment

=== "macOS/Linux"

    ```bash
    source .venv/bin/activate
    ```

=== "Windows"

    ```bash
    .venv\Scripts\activate
    ```

#### 4. Install Dependencies

```bash
# For production (runtime dependencies only)
pip install -e .

# For development (includes test and documentation dependencies)
pip install -e .[dev]
```

The `-e` flag installs the package in "editable" mode, which is useful for development.

**Available dependency groups:**

- `pip install -e .[test]` - Install with testing dependencies
- `pip install -e .[docs]` - Install with documentation dependencies  
- `pip install -e .[dev]` - Install with all development dependencies

### Option 3: Docker Installation

For the easiest deployment, use Docker:

```bash
docker pull ghcr.io/lancereinsmith/trunk8:latest
```

Or build from source:

```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
docker build -t trunk8 .
```

See the [Docker Deployment](docker.md) guide for detailed Docker instructions.

## Verify Installation

After installation, verify everything is working:

### 1. Check Python Version

```bash
python --version
```

Should show Python 3.12 or higher.

### 2. Run Development Server

```bash
python run.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

### 3. Access the Application

Open your web browser and navigate to `http://localhost:5001`. You should see the Trunk8 login page.

## Next Steps

Now that Trunk8 is installed, you can:

- Follow the [Quick Start](quickstart.md) guide to create your first link
- Learn about [Docker Deployment](docker.md) for production use
- Configure Trunk8 using the [Configuration Guide](../configuration/overview.md)
- Set up authentication with [Environment Variables](../configuration/environment.md)

## Troubleshooting

### Common Issues

#### Permission Denied

If you get permission errors during installation:

```bash
# On macOS/Linux
chmod +x run.py
```

#### Port Already in Use

If port 5001 is already in use:

1. Set a different port using the `TRUNK8_PORT` environment variable:
   ```bash
   export TRUNK8_PORT=5002
   python run.py
   ```

2. Or stop the process using port 5001:
   ```bash
   # Find process
   lsof -i :5001
   # Kill process
   kill -9 <PID>
   ```

#### Missing Dependencies

If you encounter missing dependency errors:

```bash
# With uv (runtime dependencies)
uv sync --refresh

# With uv (development dependencies)
uv sync --extra dev --refresh

# With pip (runtime dependencies)
pip install -e . --upgrade

# With pip (development dependencies)
pip install -e .[dev] --upgrade
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](../reference/faq.md)
2. Search [GitHub Issues](https://github.com/lancereinsmith/trunk8/issues)
3. Create a new issue with:
   - Your Python version
   - Your operating system
   - Complete error messages
   - Steps to reproduce 