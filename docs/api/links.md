# Links Module (app.links)

The links module handles all link management functionality including creation, editing, deletion, and serving of redirect, file, markdown, and HTML links.

## Overview

The `app.links` module provides:

- CRUD operations for shortened links
- Support for redirect, file, markdown, and HTML link types
- File upload and secure storage
- Link expiration and automatic cleanup
- User-specific data isolation

## Blueprint Routes

### Link Management Routes

All link routes handle user context automatically:

| Route | Method | Description |
|-------|--------|-------------|
| `/add` | GET, POST | Add new link |
| `/links` | GET | List all user's links |
| `/edit_link/<code>` | GET, POST | Edit existing link |
| `/delete_link/<code>` | POST | Delete link |
| `/<code>` | GET | Access/redirect to link |

## Models

### Link Class

```python
class Link:
    """
    Represents a shortened link with metadata.
    
    Attributes:
        short_code: Unique identifier for the link
        type: Link type ('redirect', 'file', 'markdown', 'html')
        url: Target URL for redirect links
        path: File path for file/markdown/html links
        expiration_date: Optional expiration timestamp
    """
```

#### Constructor

```python
def __init__(self, short_code: str, link_data: Dict[str, Any]) -> None:
    """
    Initialize a Link object.
    
    Args:
        short_code: Unique identifier for the link
        link_data: Dictionary containing link properties
    """
```

#### Properties

```python
@property
def type(self) -> str:
    """Get link type."""

@property 
def url(self) -> Optional[str]:
    """Get URL for redirect links."""

@property
def path(self) -> Optional[str]:
    """Get file path for file/markdown links."""

@property
def expiration_date(self) -> Optional[str]:
    """Get expiration date string."""
```

#### Methods

```python
def is_expired(self) -> bool:
    """
    Check if link has expired.
    
    Returns:
        True if link has expired, False otherwise.
    """

def to_dict(self) -> Dict[str, Any]:
    """
    Convert link to dictionary representation.
    
    Returns:
        Dictionary with link data.
    """
```

## Route Handlers

### add_link()

```python
@links_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_link() -> Union[str, Response]:
    """
    Handle adding new links.
    
    GET: Display the add link form.
    POST: Process new link creation.
    """
```

**Features:**

- Form validation and sanitization
- Short code uniqueness checking
- File upload handling
- User-specific storage
- Reserved route protection

**POST Data:**

- `short_code` (required) - Unique identifier
- `link_type` (required) - 'redirect', 'file', or 'markdown'
- `url` (for redirects) - Target URL
- `file` (for files) - Uploaded file
- `markdown_content` (for markdown) - Text content
- `expiration_date` (optional) - ISO format date

**Validation:**

- Short code: 1-50 chars, alphanumeric + _ -
- Reserved routes: Protected against conflicts
- File types: All types allowed
- URLs: Basic format validation

### list_links()

```python
@links_bp.route("/links")
@login_required
def list_links() -> str:
    """
    Display all user's links.
    
    Returns:
        Rendered template with links list.
    """
```

**Features:**

- User-specific link filtering
- Expiration status display
- Sortable columns
- Link count statistics

### edit_link()

```python
@links_bp.route("/edit_link/<code>", methods=["GET", "POST"])
@login_required
def edit_link(code: str) -> Union[str, Response]:
    """
    Handle editing existing links.
    
    Args:
        code: Short code of link to edit.
    """
```

**Features:**

- Link existence validation
- Type-specific editing forms
- File replacement handling
- Expiration date updates

### delete_link()

```python
@links_bp.route("/delete_link/<code>", methods=["POST"])
@login_required
def delete_link(code: str) -> Response:
    """
    Handle deleting links.
    
    Args:
        code: Short code of link to delete.
    """
```

**Features:**

- Link existence validation
- Associated file cleanup
- User-specific access control
- Confirmation handling

### serve_link()

```python
@links_bp.route("/<code>")
def serve_link(code: str) -> Union[Response, str]:
    """
    Serve/redirect to a shortened link.
    
    Args:
        code: Short code to resolve.
    """
```

**Features:**

- Public access (no authentication required)
- Multi-user link resolution
- Type-specific handling
- Expiration checking
- 404 handling for missing links

## Utilities Module

### File Operations

```python
def generate_filename() -> str:
    """
    Generate secure filename using UUID.
    
    Returns:
        Random UUID-based filename.
    """

def save_uploaded_file(file, user_assets_dir: str) -> str:
    """
    Save uploaded file with secure filename.
    
    Args:
        file: Uploaded file object
        user_assets_dir: User's assets directory
        
    Returns:
        Generated filename.
    """
```

### Link Validation

```python
def is_valid_short_code(short_code: str) -> bool:
    """
    Validate short code format.
    
    Args:
        short_code: Short code to validate
        
    Returns:
        True if valid, False otherwise.
    """

def is_reserved_route(short_code: str) -> bool:
    """
    Check if short code conflicts with system routes.
    
    Args:
        short_code: Short code to check
        
    Returns:
        True if reserved, False otherwise.
    """
```

### Expiration Management

```python
def check_expired_links(config_loader) -> None:
    """
    Check and remove expired links for current user.
    
    Args:
        config_loader: Configuration loader instance.
    """

def is_link_expired(expiration_date: str) -> bool:
    """
    Check if link has expired.
    
    Args:
        expiration_date: ISO format date string
        
    Returns:
        True if expired, False otherwise.
    """
```

## Link Types

### Redirect Links

Handle URL redirection:

```python
# Creation
{
    'type': 'redirect',
    'url': 'https://example.com',
    'expiration_date': '2024-12-31T23:59:59'  # Optional
}

# Serving
return redirect(link.url)
```

### File Links

Handle file downloads:

```python
# Creation with upload
file = request.files['file']
filename = save_uploaded_file(file, user_assets_dir)
{
    'type': 'file',
    'path': filename,
    'expiration_date': '2024-12-31T23:59:59'  # Optional
}

# Serving
return send_from_directory(user_assets_dir, link.path, as_attachment=True)
```

### Markdown Links

Handle markdown rendering:

```python
# Creation
{
    'type': 'markdown',
    'path': 'content.md',
    'expiration_date': '2024-12-31T23:59:59'  # Optional
}

# Serving
return render_template('markdown_render.html', 
                      markdown_file=link.path,
                      theme=current_markdown_theme)
```

### HTML Links

Handle raw HTML rendering:

```python
# Creation
{
    'type': 'html',
    'path': 'content.html',
    'expiration_date': '2024-12-31T23:59:59'  # Optional
}

# Serving
return render_template('html_render.html', 
                      html_filename=link.path,
                      html_content=html_content)
```

#### Auto-Detection Feature

HTML files are automatically detected when uploaded to markdown section:

```python
# File extension detection
file_ext = Path(original_filename).suffix.lower().lstrip(".")
if file_ext in ["html", "htm"]:
    # HTML file detected - change link type to html
    new_link_data["type"] = "html"
    secure_filename_uuid = f"{uuid.uuid4()}.html"
```

## User Data Isolation

### Directory Structure

```
users/
├── username1/
│   ├── links.toml     # User's links configuration
│   └── assets/        # User's uploaded files
└── username2/
    ├── links.toml
    └── assets/
```

### Access Control

```python
# Get user-specific paths
user_links_file = user_manager.get_user_links_file(current_user)
user_assets_dir = user_manager.get_user_assets_dir(current_user)

# Load user's links only
with open(user_links_file, 'r') as f:
    user_links = toml.load(f)
```

## Error Handling

### Common Errors

```python
# Link not found
return render_template('link_not_found.html'), 404

# Short code already exists
flash(f"Short code '{short_code}' already exists.", "error")

# File upload error
flash("Error uploading file. Please try again.", "error")

# Invalid expiration date
flash("Invalid expiration date format.", "error")
```

### Reserved Routes Protection

Protected system routes:

- `/settings`, `/users`, `/profile`
- `/add`, `/links`, `/edit_link`, `/delete_link`
- `/auth/*`, `/login`, `/logout`, `/register`
- `/static`, `/api`, `favicon.ico`, `robots.txt`

## Security Features

### File Security

- UUID-based filenames prevent enumeration
- Files stored outside web root
- MIME type detection for proper serving
- User-specific storage isolation

### Input Validation

- Short code format validation
- URL format checking
- File type restrictions (configurable)
- Expiration date validation

### Access Control

- User-specific link access
- Public serving without exposing internal structure
- Admin user switching support

## Configuration Integration

### Links Storage

```toml
# users/username/links.toml
[links.example]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"
```

### Application Config

```toml
# config/config.toml
[app]
theme = "cerulean"
markdown_theme = "cerulean"
# Future: max_file_size, allowed_extensions
```

## Testing Support

### Unit Tests

```python
def test_link_creation():
    link = Link('test', {'type': 'redirect', 'url': 'http://example.com'})
    assert link.short_code == 'test'
    assert link.type == 'redirect'
    assert not link.is_expired()

def test_expiration():
    past_date = (datetime.now() - timedelta(days=1)).isoformat()
    link = Link('expired', {
        'type': 'redirect', 
        'url': 'http://example.com',
        'expiration_date': past_date
    })
    assert link.is_expired()
```

### Integration Tests

```python
def test_add_redirect_link(authenticated_client):
    response = authenticated_client.post('/add', data={
        'short_code': 'test',
        'link_type': 'redirect',
        'url': 'https://example.com'
    })
    assert response.status_code == 302

def test_file_upload(authenticated_client):
    data = {
        'short_code': 'testfile',
        'link_type': 'file',
        'file': (io.BytesIO(b"test content"), 'test.txt')
    }
    response = authenticated_client.post('/add', 
                                       data=data,
                                       content_type='multipart/form-data')
    assert response.status_code == 302
```

## Performance Considerations

- Efficient file serving via Flask's send_from_directory
- Configuration caching to avoid repeated TOML parsing
- Lazy loading of user links
- Automatic cleanup of expired links

## Future Enhancements

Planned improvements:

- QR code generation
- Bulk operations
- Database backend option

## Next Steps

- [Authentication Module](auth.md) - User authentication integration
- [Application Factory](app.md) - Application setup and configuration
- [Utilities](utils.md) - Configuration and user management 