# Frequently Asked Questions

## General Questions

### What is Trunk8?

Trunk8 is a self-hosted link shortener and file hosting platform built with Flask. It allows you to create short, memorable URLs that redirect to longer URLs, host files for download, or render markdown content.

### Why should I use Trunk8 instead of a commercial service?

- **Privacy**: Your data stays on your servers
- **Control**: No usage limits or restrictions
- **Customization**: Modify to fit your needs
- **Cost**: No monthly fees or subscriptions
- **Reliability**: Not dependent on third-party services

### What are the system requirements?

- Python 3.12 or higher
- 512MB RAM minimum (1GB recommended)
- 1GB disk space (plus space for uploaded files)
- Any OS that supports Python (Linux, macOS, Windows)

## Installation

### How do I install Trunk8?

See the [Installation Guide](../getting-started/installation.md) for detailed instructions. The quickest method:

```bash
git clone https://github.com/lancereinsmith/trunk8.git
cd trunk8
uv sync  # or uv sync --extra dev for development
python run.py
```

### Can I use pip instead of uv?

Yes! While we recommend uv for faster dependency installation, pip works fine:

```bash
pip install -e .
```

### How do I run Trunk8 with Docker?

```bash
docker run -p 5001:5001 ghcr.io/lancereinsmith/trunk8:latest
```

See the [Docker Guide](../getting-started/docker.md) for more details.

## Configuration

### Where are the configuration files?

Configuration files are in the application root:

- `config/config.toml` - Application settings
- `users/{username}/links.toml` - Per-user link data storage
- `users/users.toml` - User management data
- `config/themes.toml` - Available themes

### How do I change the admin password?

Set the `TRUNK8_ADMIN_PASSWORD` environment variable:

```bash
export TRUNK8_ADMIN_PASSWORD="your-secure-password"
```

Or create a `.env` file:

```text
TRUNK8_ADMIN_PASSWORD=your-secure-password
```

### Can I change the port for the development server?

Yes, use the `TRUNK8_PORT` environment variable:

```bash
export TRUNK8_PORT=8080
python run.py
```

Or in a `.env` file:

```env
TRUNK8_PORT=8080
```

You can also modify `run.py` directly:

```python
if __name__ == "__main__":
    app.run(debug=True, port=8080)  # Change port here
```

For production with Gunicorn:

```bash
gunicorn run:app --bind 0.0.0.0:8080
```

### How do I enable HTTPS?

Use a reverse proxy like Nginx with SSL certificates. See the [Production Deployment](../deployment/production.md) guide.

## Usage

### What link types are supported?

1. **Redirect** - Forward to another URL
2. **File** - Serve uploaded files
3. **Markdown** - Render markdown as HTML

### Can I use special characters in short codes?

Short codes support:

- Letters (a-z, A-Z)
- Numbers (0-9)
- Hyphens (-)
- Underscores (_)

Avoid spaces and special characters.

### How do I set link expiration?

When creating or editing a link, set the "Expiration Date" field. Expired links are automatically deleted.

### What file types can I upload?

Trunk8 accepts all file types by default. The MIME type is automatically detected for proper browser handling.

### Is there a file size limit?

Yes, the file size limit is configurable in `config/config.toml`:

```toml
[app]
max_file_size_mb = 100  # Default: 100MB
```

**Important**: If you're using Nginx as a reverse proxy, you **must** also configure Nginx to allow larger uploads. The default Nginx limit is only 1MB, which will cause 413 errors for larger files.

**Fix Nginx 413 errors**:

1. Edit your Nginx configuration file (e.g., `/etc/nginx/sites-available/trunk8`)
2. Add or update in your `server` block:

   ```nginx
   client_max_body_size 100M;  # Match your max_file_size_mb setting
   ```

3. Test the configuration: `sudo nginx -t`
4. Reload Nginx: `sudo systemctl reload nginx`

Also consider:

- Available disk space
- Browser timeouts for large files
- Network upload speeds

To change the limit, edit `config/config.toml` and restart the application. **Remember to update Nginx as well!**

## Themes

### How many themes are available?

25+ themes from Bootswatch are included. See the full list in [Themes Guide](../user-guide/themes.md).

### Can I use different themes for UI and markdown?

Yes! Set them separately in Settings or `config/config.toml`:

```toml
[app]
theme = "darkly"           # UI theme
markdown_theme = "united"  # Markdown theme
```

### Can I add custom themes?

Currently, custom themes require modifying the source code. Future versions may support custom CSS uploads.

## Troubleshooting

### "Link not found" error

Possible causes:

- Typo in the short code (they're case-sensitive)
- Link has expired
- Link was deleted

### Can't upload files

Check:

- Disk space availability
- Write permissions on `assets/` directory
- Web server upload limits

### Theme changes don't appear

1. Clear browser cache
2. Try incognito/private mode
3. Check for JavaScript errors in console

### Port 5001 already in use

Either:

- Stop the other process: `lsof -i :5001` then `kill <PID>`
- Use a different port (see above)

### Configuration changes not taking effect

- Check TOML syntax for errors
- Verify file permissions
- Look for error messages in terminal

## Security

### Is Trunk8 secure?

Trunk8 includes basic security features:

- Password-protected admin interface
- Session-based authentication
- Secure file naming
- Input validation

For production, also implement:

- HTTPS encryption
- Firewall rules
- Regular updates
- Strong passwords

### How are passwords stored?

The admin password is compared directly from the environment variable. Future versions may add password hashing.

### Are uploaded files public?

Files are accessible to anyone with the link. For sensitive files:

- Use expiration dates
- Monitor access logs (in web server)

## Maintenance

### How do I backup Trunk8?

Backup these files:

- `config/config.toml`
- `links.toml`
- `assets/` directory

```bash
tar -czf trunk8-backup.tar.gz config/config.toml users/
```

### How do I update Trunk8?

```bash
git pull
uv sync  # or uv sync --extra dev for development dependencies
# or pip install -e . --upgrade (pip install -e .[dev] --upgrade for dev dependencies)
```

Always backup before updating!

### How do I monitor Trunk8?

- Application logs: Check terminal output
- Access logs: Configure in web server
- System monitoring: Use tools like Prometheus
- Health checks: Monitor the home page

### Can I migrate from another link shortener?

Manual migration is possible:

1. Export links from old system
2. Convert to TOML format
3. Add to `links.toml`
4. Copy files to `assets/`

## Advanced

### Can I use a database instead of TOML?

Not currently. TOML files work well for most use cases. Database support may be added in future versions.

### Is there an API?

No REST API yet, but you can:

- Modify TOML files programmatically
- Access links directly via URLs
- Extend the code with custom routes

### Can I customize the UI?

Yes, by modifying:

- Templates in `app/templates/`
- CSS in `app/static/css/`
- JavaScript in `app/static/js/`

### How can I contribute?

See the [Contributing Guide](../development/contributing.md):

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Getting Help

### Where can I get support?

- [GitHub Issues](https://github.com/lancereinsmith/trunk8/issues) - Bug reports
- [GitHub Discussions](https://github.com/lancereinsmith/trunk8/discussions) - Questions
- Documentation - You're reading it!

### How do I report a bug?

Create a GitHub issue with:

- Trunk8 version
- Python version
- Operating system
- Steps to reproduce
- Error messages
