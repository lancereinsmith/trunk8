# 🔗 Trunk8 Multi-User Link Shortener and File Host System

<div align="center">
  <img src="app/static/img/trunk8_logo.png" alt="Trunk8 Logo" width="200"/>
  
  <p>
    <a href="https://lancereinsmith.github.io/trunk8/">
      <img src="https://img.shields.io/badge/📖_Full_Documentation-blue?style=for-the-badge" alt="Documentation">
    </a>
  </p>
  
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
    <a href="https://github.com/lancereinsmith/trunk8">
      <img src="https://img.shields.io/github/v/tag/lancereinsmith/trunk8?label=version&color=green" alt="Latest Version">
    </a>
    <a href="https://github.com/lancereinsmith/trunk8/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
    </a>
  </p>
</div>

> **📚 [Complete Documentation](https://lancereinsmith.github.io/trunk8/)** - For detailed setup, configuration, API reference, and deployment guides.

A modern, self-hosted **multi-user** link shortener and file hosting platform built with Flask. Transform long URLs into memorable short codes, host files with secure UUID4 naming, and create beautiful markdown documents with live rendering.

## ✨ Key Features

- 👥 **Multi-User Support** - Individual user accounts with complete data isolation
- 🔗 **Smart Link Shortening** - Convert URLs into clean, memorable short codes  
- 📁 **Secure File Hosting** - Upload and share files with comprehensive metadata tracking
- 📝 **Live Markdown Rendering** - Create and share markdown documents with real-time preview
- 🌐 **Raw HTML Hosting** - Host custom HTML pages with full CSS, JavaScript, and interactive elements
- 🎨 **25+ Themes** - Customizable Bootswatch themes for both UI and markdown rendering
- 🔐 **Advanced Authentication** - Multi-user login with admin privileges and user switching
- ⚡ **Live Configuration** - TOML-based config with automatic reloading
- 🐳 **Docker Ready** - One-command deployment
- ⏱️ **Link Expiration** - Set expiration dates with automatic cleanup

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Quick start with Docker
docker run -p 5001:5001 \
  -e TRUNK8_ADMIN_PASSWORD=your_secure_password \
  -e TRUNK8_SECRET_KEY=your_secret_key \
  ghcr.io/lancereinsmith/trunk8:latest
```

Visit `http://localhost:5001` and log in with:
- **Username**: *(leave blank for admin mode)*
- **Password**: `your_secure_password`

### Option 2: Direct Installation

```bash
# Clone and setup
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Or install with pip
pip install -e .

# Run the application
python run.py
```

Visit `http://localhost:5001` and log in with the default password: `admin`

## 🏗️ Architecture

**Multi-User Data Isolation:**
```
users/
├── users.toml              # User management
├── admin/
│   ├── links.toml          # Admin's links
│   └── assets/             # Admin's files
└── {username}/
    ├── config.toml         # User preferences
    ├── links.toml          # User's links
    └── assets/             # User's files
```

**Link Types:**
- **File Links** - Secure file hosting with UUID4 naming
- **URL Redirects** - Clean short links to external URLs  
- **Markdown Content** - Live-rendered documents with theme support
- **HTML Content** - Custom HTML pages with full CSS, JavaScript, and interactive features

## 📖 Documentation

For comprehensive information, please visit our **[full documentation](https://lancereinsmith.github.io/trunk8/)**:

- **[Quick Start Guide](https://lancereinsmith.github.io/trunk8/getting-started/quickstart/)** - Detailed setup instructions
- **[Docker Deployment](https://lancereinsmith.github.io/trunk8/getting-started/docker/)** - Container deployment guide
- **[Configuration](https://lancereinsmith.github.io/trunk8/configuration/overview/)** - TOML configuration options
- **[User Guide](https://lancereinsmith.github.io/trunk8/user-guide/overview/)** - Using the application
- **[API Reference](https://lancereinsmith.github.io/trunk8/api/overview/)** - Developer documentation
- **[Deployment](https://lancereinsmith.github.io/trunk8/deployment/production/)** - Production deployment

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRUNK8_ADMIN_PASSWORD` | Admin login password | `admin` |
| `TRUNK8_SECRET_KEY` | Session encryption key | *(generated)* |
| `TRUNK8_PORT` | Server port | `5001` |
| `TRUNK8_LOG_LEVEL` | Logging level | `INFO` |

## 🛡️ Security

- Set strong `TRUNK8_ADMIN_PASSWORD` and `TRUNK8_SECRET_KEY` in production
- Each user's data is completely isolated
- Secure file handling with random filenames
- Automatic cleanup of expired content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a Pull Request

See our [Contributing Guide](https://lancereinsmith.github.io/trunk8/development/contributing/) for detailed instructions.

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <strong>Ready to get started?</strong><br>
  <a href="https://lancereinsmith.github.io/trunk8/getting-started/quickstart/">📖 Read the Quick Start Guide</a>
</div>
