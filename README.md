# 🔗 Trunk8 Multi-User Link Shortener and File Host System

<div align="center">
  <img src="app/static/img/trunk8_logo.png" alt="Trunk8 Logo" width="200"/>
  
  <p>
    <a href="https://github.com/lancereinsmith/trunk8/actions/workflows/tests.yml">
      <img src="https://github.com/lancereinsmith/trunk8/actions/workflows/tests.yml/badge.svg" alt="Tests">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8/actions/workflows/docker.yml">
      <img src="https://github.com/lancereinsmith/trunk8/actions/workflows/docker.yml/badge.svg" alt="Docker">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8/actions/workflows/docs.yml">
      <img src="https://github.com/lancereinsmith/trunk8/actions/workflows/docs.yml/badge.svg" alt="Documentation">
    </a>
    <a href="https://lancereinsmith.github.io/trunk8/">
      <img src="https://img.shields.io/badge/docs-live-blue" alt="Documentation">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8">
      <img src="https://img.shields.io/github/v/tag/lancereinsmith/trunk8?label=version&color=green" alt="Latest Version">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8">
      <img src="https://img.shields.io/github/languages/top/lancereinsmith/trunk8" alt="Language">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
    </a>
  </p>
</div>

A modern, self-hosted **multi-user** link shortener and file hosting platform built with Flask. Transform long URLs into memorable short codes, host files with UUID4 naming and comprehensive metadata tracking, and create beautiful markdown documents with live rendering. Perfect for teams, organizations, or personal use with complete user isolation and admin management capabilities.

**Key Capabilities:**
- 👥 **Multi-User Support** - Individual user accounts with isolated data and admin management
- 🔗 **Smart Link Shortening** - Convert any URL into clean, memorable short codes
- 📁 **Secure File Hosting** - Upload and share files with UUID4 naming and comprehensive metadata tracking
- 📝 **Live Markdown Rendering** - Create and share markdown documents with real-time rendering using StrapDown.js
- 💻 **Raw HTML Hosting** - Host custom web pages with full CSS, JavaScript, and interactive elements
- 🎨 **Customizable Themes** - Choose from 25+ Bootswatch themes for both UI and markdown rendering
- 🔐 **Advanced Authentication** - Multi-user login system with admin privileges and user switching
- ⚡ **Live Configuration** - TOML-based config with automatic reloading
- 🐳 **Docker Ready** - One-command deployment with optimized Astral uv image
- ⏱️ **Link Expiration** - Set expiration dates for temporary links with automatic cleanup

## Multi-User Features

### User Management
- **Individual User Accounts** - Each user has their own username, password, and display name
- **Data Isolation** - Each user's links and files are stored in separate directories (`users/{username}/`)
- **Admin Privileges** - Admin users can manage all users and access all data
- **User Switching** - Admins can switch to view any user's context for support and management

### Authentication System
- **Dual Login Mode** - Supports both administrator single-password mode and multi-user authentication
- **Session Management** - Secure session handling with configurable lifetime and "remember me"
- **Admin Fallback** - Always maintains an admin user for system access

### Directory Structure
```
users/
├── users.toml              # User management data
├── admin/
│   ├── links.toml          # Admin's links
│   └── assets/             # Admin's files
├── john/
│   ├── config.toml         # John's theme preferences
│   ├── links.toml          # John's links
│   └── assets/             # John's files
└── mary/
    ├── config.toml         # Mary's theme preferences
    ├── links.toml          # Mary's links
    └── assets/             # Mary's files
```

## Features

- **Multiple Link Types**:
  - File downloads with secure storage
  - URL redirects with automatic forwarding
  - Markdown content rendering with StrapDown.js
  - Raw HTML hosting with full CSS and JavaScript support
- **User Management**:
  - Individual user accounts with isolated data
  - Admin interface for user management
  - User profile management and password changes
- **Automatic Short Code Generation**: Generates unique short codes automatically
- **File Upload Support**: Handles file uploads with UUID4 security, metadata storage, and file validation
- **Theme Support**: Configurable UI theme and separate markdown theme with 25+ available options loaded from `config/themes.toml`
- **Settings Interface**: Web-based theme configuration and settings management
- **Link Management**: View, edit, and delete existing links (with proper permissions)
- **Modern UI**: Clean and responsive Bootstrap-based interface with user indicators
- **Modular Architecture**: Blueprint-based Flask application with separated concerns
- **Automatic Expired Link Cleanup**: Expired links and associated files are automatically removed

## Dependencies

### Runtime Dependencies
- Python 3.12 or higher
- Flask 3.1.1 or higher
- TOML 0.10.2 or higher
- Gunicorn (for production deployment)
- Python-dotenv 1.0.0 or higher

### Development Dependencies (Optional)
- **Testing**: pytest, pytest-flask, pytest-cov, pytest-mock
- **Documentation**: mkdocs, mkdocs-material, mkdocstrings

Install development dependencies with: `uv sync --extra dev` or `pip install .[dev]`

## Installation

### Option 1: Using uv (Recommended)

1. Install uv if you haven't already:
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
```

3. Install dependencies and create virtual environment:
```bash
# For production (runtime dependencies only)
uv sync

# For development (includes test and documentation dependencies)
uv sync --extra dev
```

4. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### Option 2: Using pip

1. Clone the repository:
```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

3. Install the required dependencies:
```bash
# For production (runtime dependencies only)
pip install -e .

# For development (includes test and documentation dependencies)
pip install -e .[dev]
```

## Running the Application

### Development Mode
For development, you can run the application using Flask's built-in server:
```bash
python run.py
```

To use a different port, set the `TRUNK8_PORT` environment variable:
```bash
export TRUNK8_PORT=8080
python run.py
```

### Production Mode
For production deployment, use Gunicorn:
```bash
gunicorn run:app --bind 0.0.0.0:5001
```

The server will run on `http://localhost:5001` by default.

## Docker Deployment

The application includes a Dockerfile for easy containerized deployment using Astral's official uv-enabled Python image.

### Building the Docker Image

```bash
docker build -t trunk8 .
```

### Running the Container

```bash
docker run -p 5001:5001 trunk8
```

For production use, set a secure admin password and secret key:

```bash
docker run -p 5001:5001 -e TRUNK8_ADMIN_PASSWORD=your_secure_password_here -e TRUNK8_SECRET_KEY=your_secret_key_here trunk8
```

To use a different port:

```bash
docker run -p 8080:8080 -e TRUNK8_PORT=8080 -e TRUNK8_ADMIN_PASSWORD=your_secure_password_here trunk8
```

The application will be accessible at `http://localhost:5001`.

### Docker Features

- **Base Image**: Uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (Astral's official uv-enabled Python image)
- **Dependency Management**: Leverages uv for fast and reliable dependency installation
- **Production Ready**: Uses Gunicorn for production deployment
- **Optimized Caching**: Docker layers are optimized for dependency caching
- **Port**: Exposes and serves on port 5001

## Configuration

The application uses TOML files for configuration and data storage with a hierarchical per-user theme system:

### 1. config/config.toml - Admin-level configuration:
```toml
# Admin-level Configuration for Trunk8
# This file contains system-wide defaults and admin-only settings

[app]
# Default themes for new users (can be overridden per-user)
theme = "cerulean"
markdown_theme = "cerulean"
# Maximum file upload size in megabytes (admin-only)
max_file_size_mb = 100

# Note: Users can override theme settings in their individual config.toml files:
# users/{username}/config.toml

[session]
# Session configuration (admin-only, applies to all users)
permanent_lifetime_days = 30
```

### 2. users/{username}/config.toml - Per-user configuration:
```toml
[app]
# User-specific theme overrides (optional)
theme = "darkly"              # Overrides admin default
markdown_theme = "flatly"     # Different from UI theme
```

### 3. users/users.toml - User management:
```toml
[users]

[users.admin]
password_hash = "hashed_password"
is_admin = true
display_name = "Administrator"
created_at = "2024-01-01T00:00:00"

[users.john]
password_hash = "hashed_password"
is_admin = false
display_name = "John Doe"
created_at = "2024-01-01T00:00:00"
```

### 4. Per-user links files - users/{username}/links.toml:
```toml
[links.ex_redirect]
type = "redirect"
url = "https://www.example.com"

[links.ex_text]
type = "file"
path = "example.txt"

[links.ex_markdown]
type = "markdown"
path = "example.md"

[links.ex_html]
type = "html"
path = "example.html"

# Example with expiration
[links.temp_link]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"
```

### 5. config/themes.toml - Available themes configuration (automatically provided)

All files will be created automatically on first run with default values if they don't exist.

### Logging Configuration

The application includes comprehensive logging to help with debugging and monitoring:

- **Default Log Level**: INFO - provides informative messages about application operation
- **Configurable Log Level**: Set the `TRUNK8_LOG_LEVEL` environment variable to change the logging level
- **Available Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output Format**: Timestamps, module names, log levels, and descriptive messages
- **Console Output**: All logs are displayed in the console where the application is running

#### Setting Log Level

You can configure the log level using the environment variable:

```bash
# Set log level to DEBUG for verbose logging
export TRUNK8_LOG_LEVEL=DEBUG
python run.py

# Set log level to WARNING to only see warnings and errors
export TRUNK8_LOG_LEVEL=WARNING
python run.py

# Or use with Docker
docker run -p 5001:5001 -e TRUNK8_LOG_LEVEL=DEBUG trunk8
```

#### What Gets Logged

The application logs important events including:

- **Application Startup**: Initialization steps and configuration loading
- **User Authentication**: Login attempts, successful/failed authentications, logout events
- **Link Operations**: Link creation, access, editing, and deletion
- **User Management**: User creation, profile changes, admin operations
- **Errors and Warnings**: Failed operations, expired link access attempts, file handling issues
- **Configuration Changes**: Settings updates and theme changes

#### Example Log Output

```
2024-01-15 10:30:15 - trunk8 - INFO - Starting Trunk8 application initialization
2024-01-15 10:30:15 - trunk8 - INFO - Configuration files loaded
2024-01-15 10:30:15 - trunk8 - INFO - Trunk8 application initialization completed successfully
2024-01-15 10:30:20 - trunk8.auth.routes - INFO - Login attempt for user: john
2024-01-15 10:30:20 - trunk8.auth.routes - INFO - Successful login for user: john (admin: False)
2024-01-15 10:30:25 - trunk8.links.routes - INFO - Link created: abc123 (type: redirect, user: john)
2024-01-15 10:30:30 - trunk8.links.routes - INFO - Link accessed: abc123 (type: redirect, owner: john)
```

### Theme Selection

The application uses Bootswatch themes (https://bootswatch.com/) for styling. Available themes are loaded from `config/themes.toml` and include:

- brite - Clean and bright design
- cerulean - A calm blue sky
- cosmo - An ode to Metro
- cyborg - Jet black and electric blue
- darkly - Flatly in night mode
- flatly - Flat and modern
- journal - Crisp like a new sheet of paper
- litera - The medium is the message
- lumen - Light and shadow
- lux - A touch of class
- materia - Material is the metaphor
- minty - A fresh feel
- morph - A modern take
- pulse - A trace of purple
- quartz - A gem of a theme
- sandstone - A touch of warmth
- simplex - Mini and minimalist
- sketchy - A hand-drawn look
- slate - Shades of gunmetal gray
- solar - A spin on Solarized
- spacelab - Silvery and sleek
- superhero - The brave and the blue
- united - Ubuntu orange and unique font
- vapor - A subtle theme
- yeti - A friendly foundation
- zephyr - Breezy and beautiful

You can set different themes for the main UI (`theme`) and markdown rendering (`markdown_theme`) in the `config/config.toml` file.

## Per-User Theme Configuration

Trunk8 now supports individual theme preferences for each user:

### Theme Hierarchy
1. **Admin Defaults** (`config/config.toml`) - System-wide default themes
2. **User Overrides** (`users/{username}/config.toml`) - Individual user preferences

### How It Works
- Admin user modifies global defaults directly in `config/config.toml`
- Regular users inherit admin defaults but can override via personal `config.toml` files
- Each regular user's theme preferences are saved in their personal `config.toml` file
- Admin can set different defaults that apply to new users
- Existing users keep their individual preferences

### Examples

**Admin sets system defaults (affects new users):**
```toml
# config/config.toml (admin changes this directly via Settings)
[app]
theme = "darkly"              # New default for new users
markdown_theme = "flatly"     # Light markdown for readability
```

**User John prefers different themes:**
```toml
# users/john/config.toml
[app]
theme = "cerulean"            # Overrides admin default
markdown_theme = "cerulean"   # Consistent light theme
```

**User Mary uses mixed themes:**
```toml
# users/mary/config.toml
[app]
theme = "cyborg"              # Dark UI
markdown_theme = "flatly"     # Light content
```

## Usage

1. Start the server:
```bash
python run.py
```

The server will run on `http://localhost:5001` by default.

2. Access the following endpoints:
   - `/` - Dashboard (requires authentication)
   - `/add` - Add new links (requires authentication)
   - `/links` - View user's links or all links (admin) (requires authentication)
   - `/edit_link/<short_code>` - Edit existing links (requires authentication + ownership/admin)
   - `/settings` - Configure themes and application settings (requires authentication)
   - `/users` - User management (admin only)
   - `/auth/register` - Add new users (admin only)
   - `/profile` - User profile management (requires authentication)
   - `/<short_code>` - Access shortened links (public)
   - `/auth/login` - Login page
   - `/auth/logout` - Logout endpoint

### Authentication

The application supports both administrator single-password mode and modern multi-user authentication:

#### Multi-User Mod
- Users log in with username and password
- Each user has isolated data in `users/{username}/`
- Admin users can manage other users and access all data
- User switching allows admins to view other users' contexts

#### Administrator Mode
- Leave username blank and enter the admin password
- Uses `TRUNK8_ADMIN_PASSWORD` environment variable (defaults to "admin")
- Automatically creates admin user and migrates to multi-user structure

#### Security Configuration
- Set a custom admin password using the `TRUNK8_ADMIN_PASSWORD` environment variable
- Set a secure secret key using the `TRUNK8_SECRET_KEY` environment variable for session security
- You can set both using a `.env` file in the root folder
- Public links remain accessible without authentication
- Session-based authentication with configurable timeout (default 30 days with "remember me")

### User Management (Admin Only)

Admins can:
- **Create new users** - Set username, password, display name, and admin privileges
- **View all users** - See user statistics and account information
- **Delete users** - Remove users (except admin user)
- **Switch user context** - View the system from any user's perspective
- **Access all data** - View and manage links from all users

### Adding Links

Visit `/add` to create new links. You can:
- Upload files for direct download (stored in your personal assets folder)
- Create redirect links to external URLs
- Upload Markdown files or enter Markdown text for rendering
- Upload HTML files or enter HTML content for custom web pages

### Editing Links

Visit `/edit_link/<short_code>` to modify existing links. You can:
- Replace files for file links
- Update URLs for redirect links  
- Update Markdown content for markdown links
- Update HTML content for HTML links
- Users can only edit their own links (admins can edit any link)

### Settings

Visit `/settings` to configure application settings. You can:
- Change the UI theme for the main interface
- Set a separate theme for markdown rendering
- Choose from 25+ available Bootswatch themes

### User Profile

Visit `/profile` to manage your account:
- View account information
- Change your password
- See your data storage location
- View account privileges

### Link Types

1. **File Links**:
   - Upload any file to your personal assets directory
   - Files are stored with secure random filenames
   - Automatic MIME type detection
   - Each user has isolated file storage
   - Configurable file size limits (default: 100MB)

2. **Redirect Links**:
   - Provide a target URL
   - Users will be automatically redirected
   - Supports both relative and absolute URLs

3. **Markdown Links**:
   - Upload Markdown files or enter text directly
   - Content is rendered using StrapDown.js
   - Supports GitHub-flavored Markdown
   - Configurable theme separate from main UI theme

4. **HTML Links**:
   - Upload HTML files or enter HTML content directly
   - Raw HTML rendering with full CSS and JavaScript support
   - Perfect for custom web pages, portfolios, and interactive content
   - Auto-detection when HTML files are uploaded to markdown section



## Project Structure

```
trunk8/
├── run.py              # Main entry point
├── config/
│   ├── config.toml     # Admin-level settings (defaults, session config)
│   └── themes.toml     # Available themes with descriptions
├── users/              # User data and management
│   ├── users.toml      # User management data
│   ├── admin/
│   │   ├── links.toml  # Admin's links
│   │   └── assets/     # Admin's files
│   └── {username}/
│       ├── config.toml # User's theme preferences
│       ├── links.toml  # User's links
│       └── assets/     # User's files
├── pyproject.toml      # Project dependencies
├── uv.lock            # Dependency lock file
├── Dockerfile         # Docker deployment configuration
├── app/               # Application package
│   ├── __init__.py    # Application factory
│   ├── auth/          # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── decorators.py  # Multi-user auth decorators
│   │   └── routes.py      # Login, logout, register, user switching
│   ├── links/         # Links management blueprint
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py      # Multi-user link operations
│   │   └── utils.py       # Per-user link utilities
│   ├── main/          # Main routes blueprint
│   │   ├── __init__.py
│   │   └── routes.py      # Dashboard, settings, user management
│   ├── utils/         # Utilities
│   │   ├── __init__.py
│   │   ├── config_loader.py  # Multi-user config management
│   │   └── user_manager.py   # User management utilities (NEW)
│   ├── static/        # Static assets (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/     # HTML templates
│       ├── login.html       # Multi-user login
│       ├── register.html    # User registration (NEW)
│       ├── users.html       # User management (NEW)
│       ├── profile.html     # User profile (NEW)
│       ├── index.html       # Multi-user dashboard
│       └── ...             # Other templates updated for multi-user
└── debug/             # Debug utilities (optional)
```

## Security Considerations

### Multi-User Security
- **Data Isolation** - Each user's data is completely isolated from others
- **Permission Checks** - Users can only access their own data (admins can access all)
- **Secure Authentication** - Password hashing and secure session management
- **Admin Controls** - Proper privilege escalation and user management controls

### General Security
- Set a strong `TRUNK8_ADMIN_PASSWORD` environment variable
- Set the `TRUNK8_SECRET_KEY` environment variable in production
- User directories are properly secured with file permissions
- Consider implementing rate limiting
- Input validation and sanitization across all user inputs
- Secure file handling with random filenames
- Automatic cleanup of expired links and associated files

## Git Configuration

If you want to keep this as a git repository but prevent your local configuration and data files from being overwritten during git operations, run the following command:

```bash
git config merge.ours.driver true
```

This sets up a merge driver that will keep your local versions of configuration files (`config/config.toml`, `users/users.toml`, and user-specific `links.toml` files) during merges and pulls, allowing you to maintain your custom settings and user data while still receiving updates to the codebase.

## Development

The application uses type hints and follows Python best practices. Key components:

- `run.py`: Main entry point that creates and runs the Flask application
- `app/__init__.py`: Application factory with blueprint registration and multi-user setup
- `app/auth/`: Authentication blueprint with multi-user login, user management, and switching
- `app/links/`: Link management blueprint with user-isolated CRUD operations
- `app/main/`: Main application routes including dashboard, settings, and user management
- `app/utils/`: Utility modules including multi-user configuration loader and user manager
- `templates/`: HTML templates using Jinja2 with multi-user context
- User directories: `users/{username}/` for isolated data storage
- Configuration files: `config/config.toml`, `config/themes.toml`, `users/users.toml`
- Per-user data files: `users/{username}/links.toml`, `users/{username}/assets/`
- `pyproject.toml`: Project dependencies and metadata
- `Dockerfile`: Docker deployment configuration

### Key Multi-User Components

- `UserManager` - Handles user authentication, creation, and management
- `ConfigLoader` - Extended to support per-user data loading and context switching
- Authentication decorators - Support both user and admin permission checking
- User switching - Allows admins to view system from any user's perspective


## API Endpoints

### Public
- `GET /{short_code}` - Access any user's public link

### Authentication
- `GET /auth/login` - Login page (supports both administrator and multi-user mode)
- `POST /auth/login` - Process login
- `GET /auth/logout` - Logout
- `GET /auth/register` - User registration form (admin only)
- `POST /auth/register` - Create new user (admin only)
- `GET /auth/switch-user/{username}` - Switch to user context (admin only)
- `GET /auth/switch-back` - Return to admin context

### User Management (Admin Only)
- `GET /users` - List all users
- `GET /users/{username}` - View user details
- `POST /users/{username}/delete` - Delete user

### User Profile
- `GET /profile` - View/edit user profile
- `POST /profile` - Update profile (password change)

### Links (User/Admin)
- `GET /links` - List user's links (or all links for admin)
- `GET /add` - Add link form
- `POST /add` - Create new link
- `GET /edit_link/{short_code}` - Edit link form
- `POST /edit_link/{short_code}` - Update link
- `POST /delete_link/{short_code}` - Delete link

### Settings
- `GET /settings` - Application settings
- `POST /settings` - Update settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask for the web framework
- TOML for configuration management
- StrapDown.js for Markdown rendering
- Bootstrap for the UI framework
- The Python community for various tools and libraries
