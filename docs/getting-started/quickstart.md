# Quick Start

Get up and running with Trunk8 in just a few minutes! This guide assumes you've already [installed Trunk8](installation.md).

## Step 1: Start the Server

Start the Trunk8 development server:

```bash
python run.py
```

The server will start on `http://localhost:5001`. To use a different port, set the `TRUNK8_PORT` environment variable:

```bash
export TRUNK8_PORT=8080
python run.py
```

!!! tip "Production Deployment"
    For production, use Gunicorn instead:
    ```bash
    gunicorn run:app --bind 0.0.0.0:5001
    ```

## Step 2: Log In

1. Navigate to `http://localhost:5001` in your web browser
2. You'll be redirected to the login page
3. Enter the admin password (default: `admin`)

!!! warning "Change Default Password"
    Always set a secure password in production using the `TRUNK8_ADMIN_PASSWORD` environment variable:
    ```bash
    export TRUNK8_ADMIN_PASSWORD="your-secure-password"
    ```

## Step 3: Create Your First Link

### URL Shortening

1. Click **"Add Link"** in the navigation
2. Enter a **Short Code** (e.g., `docs`)
3. Select **"Redirect"** as the link type
4. Enter the **Target URL** (e.g., `https://github.com/lancereinsmith/trunk8`)
5. Click **"Create Link"**

Your shortened link is now available at `http://localhost:5001/docs`!

### File Hosting

1. Click **"Add Link"**
2. Enter a **Short Code** (e.g., `report`)
3. Select **"File"** as the link type
4. Click **"Choose File"** and select a file to upload
5. Click **"Create Link"**

Files are automatically secured with UUID4 naming and stored with comprehensive metadata including file size, MIME type, and upload timestamp. When users download files, they see the original filename while the actual storage uses secure UUIDs to prevent enumeration attacks.

Access your file at `http://localhost:5001/report`.

!!! info "File Security"
    Uploaded files are stored with UUID4 names (e.g., `f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf`) for maximum security while preserving the original filename for user downloads.

### Markdown Rendering

1. Click **"Add Link"**
2. Enter a **Short Code** (e.g., `readme`)
3. Select **"Markdown"** as the link type
4. Either:
    - Upload a `.md` file, or
    - Type/paste markdown content directly
5. Click **"Create Link"**

View your rendered markdown at `http://localhost:5001/readme`.

## Step 4: Manage Your Links

### View All Links

Click **"List Links"** to see all your created links. From here you can:

- View link details
- Edit existing links
- Delete links you no longer need
- See expiration dates

### Edit a Link

1. Click the **"Edit"** button next to any link
2. Modify the link properties:
    - Change the target URL for redirects
    - Upload a new file for file links
    - Update markdown content
    - Set or change expiration dates
3. Click **"Update Link"**

### Set Link Expiration

1. When creating or editing a link, set an **Expiration Date**
2. The link will automatically be deleted after this date
3. Expired links return a "Link not found" page

## Step 5: Customize Themes

1. Click **"Settings"** in the navigation
2. Choose a **UI Theme** from 25+ options
3. Select a **Markdown Theme** (can be different from UI theme)
4. Click **"Save Settings"**

Themes are applied immediately without restarting the server.

## Example Workflows

### Personal Bookmarks

Create easy-to-remember shortcuts for frequently accessed sites:

- `/gh` → Your GitHub profile
- `/mail` → Your email provider
- `/cal` → Your calendar application

### File Sharing

Share files with colleagues using memorable links:

- `/q4-report` → Quarterly report PDF
- `/presentation` → Latest presentation slides
- `/logo` → Company logo files

### Documentation Hub

Host markdown documentation with custom themes:

- `/api-docs` → API documentation
- `/user-guide` → User manual
- `/changelog` → Release notes

## Configuration Files

Trunk8 uses TOML files for configuration, which are automatically created on first run:

### config/config.toml
```toml
[app]
theme = "cerulean"
markdown_theme = "cerulean"

[session]
permanent_lifetime_days = 30
```

### Multi-User Data Files

**users/users.toml** - User management:
```toml
[users.admin]
password_hash = "hashed_password"
is_admin = true
display_name = "Administrator"
```

**users/admin/links.toml** - Admin's links:
```toml
[links.example]
type = "redirect"
url = "https://example.com"

[links.myfile]
type = "file"
path = "f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf"
original_filename = "document.pdf"
file_size = 1048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:30:00"
expiration_date = "2024-12-31T23:59:59"
```

## Tips and Tricks

### Memorable Short Codes

- Use descriptive names: `docs`, `api`, `download`
- Create categories: `proj-alpha`, `proj-beta`
- Use dates for temporary links: `meeting-2024-01`

### Bulk Operations

While Trunk8 doesn't have a built-in bulk import, you can:

1. Edit the appropriate `users/{username}/links.toml` file directly
2. Use the TOML format to copy/paste link configurations  
3. Changes are automatically reloaded (no restart required)

**Note**: Only edit your own user's links file, or the admin can edit any user's file.

### Security Best Practices

1. **Always change the default password**
2. **Use HTTPS in production** (configure via reverse proxy)
3. **Set secure session keys** with `TRUNK8_SECRET_KEY`
4. **Regularly review and clean up old links**
5. **Monitor file uploads** for unusual activity

## Next Steps

- Explore [Link Types](../user-guide/link-types.md) in detail
- Learn about [Configuration Options](../configuration/overview.md)
- Set up [Docker Deployment](docker.md) for production
- Read about [Security Considerations](../deployment/security.md)

## Need Help?

- Check the [User Guide](../user-guide/overview.md) for detailed features
- See the [FAQ](../reference/faq.md) for common questions
- Report issues on [GitHub](https://github.com/lancereinsmith/trunk8/issues) 