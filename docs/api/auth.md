# Authentication Module (app.auth)

The authentication module handles user login, logout, registration, and session management with multi-user support.

## Overview

The `app.auth` module provides:

- Multi-user authentication system
- Session management with "remember me" functionality
- User registration for admins
- User switching for administrative purposes
- Administrator single-password mode

## Blueprint Routes

### Authentication Routes

All authentication routes are prefixed with `/auth`:

| Route | Method | Description |
|-------|--------|-------------|
| `/auth/login` | GET, POST | User login page and handler |
| `/auth/logout` | GET | Logout handler |
| `/auth/register` | GET, POST | User registration (admin only) |
| `/auth/switch-user/<username>` | GET | Switch user context (admin only) |
| `/auth/switch-back` | GET | Return to admin context |

## Route Handlers

### login()

```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    """
    Handle user login.

    GET: Display the login form.
    POST: Process login credentials and authenticate user.

    Supports both administrator single-password mode and multi-user mode.

    Returns:
        Union[str, Response]: Either a redirect response on successful login
                             or rendered login template.
    """
```

**Features:**

- Multi-user authentication with username and password
- Administrator single-password mode (username field left blank)
- "Remember me" functionality
- Session management
- Flash message feedback

**POST Data:**

- `username` (optional) - Username for multi-user mode
- `password` (required) - User password
- `remember` (optional) - "Remember me" checkbox

**Authentication Flow:**
1. If username provided: Multi-user authentication via UserManager
2. If no username: Admin mode using `TRUNK8_ADMIN_PASSWORD`
3. Set session variables on success
4. Configure session permanence based on "remember me"

### logout()

```python
@auth_bp.route("/logout")
def logout() -> Response:
    """
    Handle user logout.

    Clears the user's session and redirects to the login page.

    Returns:
        Response: Redirect response to the login page.
    """
```

**Features:**

- Clears all session data
- Provides logout confirmation message
- Redirects to login page

### register()

```python
@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    """
    Handle user registration (admin only).

    GET: Display the registration form (admin only).
    POST: Process user registration (admin only).

    Returns:
        Union[str, Response]: Either a redirect response or rendered registration template.
    """
```

**Features:**

- Admin-only access (requires admin authentication)
- User creation via UserManager
- Input validation and sanitization
- Password confirmation
- Admin privilege assignment

**POST Data:**

- `username` (required) - Unique username (3+ chars, alphanumeric + _ -)
- `password` (required) - Password (4+ chars minimum)
- `confirm_password` (required) - Password confirmation
- `display_name` (optional) - Human-readable name
- `is_admin` (optional) - Admin privileges checkbox

**Validation Rules:**

- Username: 3+ characters, alphanumeric with hyphens and underscores only
- Password: 4+ characters minimum
- Passwords must match
- Username must be unique

### switch_user()

```python
@auth_bp.route("/switch-user/<username>")
def switch_user(username: str) -> Response:
    """
    Switch to another user context (admin only).

    Args:
        username: Username to switch to.

    Returns:
        Response: Redirect response.
    """
```

**Features:**

- Admin-only functionality
- Temporary user context switching
- Preserves admin session
- User existence validation

### switch_back()

```python
@auth_bp.route("/switch-back")
def switch_back() -> Response:
    """
    Switch back to admin user (clear user switching).

    Returns:
        Response: Redirect response.
    """
```

**Features:**

- Returns to original admin context
- Clears user switching session data
- Admin-only access

## Decorators Module

### login_required

```python
def login_required(f):
    """
    Decorator to require authentication for routes.
    
    Checks if user is authenticated and redirects to login if not.
    """
```

**Usage:**
```python
from app.auth.decorators import login_required

@app.route('/protected')
@login_required
def protected_route():
    return "This requires authentication"
```

**Features:**

- Checks session authentication status
- Redirects to login page if not authenticated
- Preserves original URL for post-login redirect

### admin_required

```python
def admin_required(f):
    """
    Decorator to require admin privileges for routes.
    
    Checks if user is authenticated and has admin privileges.
    """
```

**Usage:**
```python
from app.auth.decorators import admin_required

@app.route('/admin-only')
@admin_required
def admin_route():
    return "This requires admin privileges"
```

### User Context Functions

#### get_current_user()

```python
def get_current_user() -> Optional[str]:
    """
    Get the current active username.
    
    Returns the switched user if admin is switching, otherwise the logged-in user.
    """
```

Returns:

- Active user (if admin is switching)
- Logged-in user (normal case)
- None (if not authenticated)

#### get_user_context()

```python
def get_user_context() -> Dict[str, Any]:
    """
    Get user context for templates.
    
    Returns dictionary with user information for template rendering.
    """
```

Returns context with:

- `current_user` - Current username
- `is_admin` - Admin status
- `display_name` - User display name
- `is_switching` - Whether admin is switching users

## Session Structure

Session variables used by the authentication system:

```python
session = {
    'authenticated': bool,      # Whether user is logged in
    'username': str,           # Original logged-in username
    'is_admin': bool,          # Admin privileges
    'display_name': str,       # User display name
    'active_user': str,        # Current active user (for switching)
    'active_display_name': str # Active user display name
}
```

## Authentication Modes

### Multi-User Mode

Standard authentication with username and password:

```python
# Login with username and password
user_data = user_manager.authenticate_user(username, password)
if user_data:
    # Set session variables
    session['authenticated'] = True
    session['username'] = username
    session['is_admin'] = user_data.get('is_admin', False)
```

### Administrator Mode

Administrator authentication with single password:

```python
# Login with password only (no username)
admin_password = os.environ.get('TRUNK8_ADMIN_PASSWORD', 'admin')
if password == admin_password:
    # Set session for admin user
    session['authenticated'] = True
    session['username'] = 'admin'
    session['is_admin'] = True
```

## User Management Integration

The authentication module integrates with the UserManager:

```python
# Initialize user manager
user_manager = UserManager()

# Authenticate user
user_data = user_manager.authenticate_user(username, password)

# Create new user (admin only)
success = user_manager.create_user(username, password, display_name, is_admin)

# Check if user exists
user_data = user_manager.get_user(username)
```

## Security Features

### Password Handling

- Admin password: Environment variable only (never stored)
- User passwords: SHA-256 hashed storage
- Password validation during registration
- Secure session key generation

### Session Security

- Configurable session lifetime
- Secure session cookie settings
- Session data clearing on logout
- CSRF protection (built into Flask-WTF when forms are used)

### Access Control

- Route-level authentication requirements
- Admin privilege checking
- User context isolation
- Secure user switching

## Error Handling

Common error scenarios and responses:

```python
# Invalid credentials
flash("Invalid username or password.", "error")

# Admin access required
flash("Admin access required to register new users.", "error")

# User not found
flash(f"User '{username}' not found.", "error")

# Registration validation errors
flash("Username must be at least 3 characters.", "error")
flash("Passwords do not match.", "error")
```

## Flash Message Categories

The module uses these flash message categories:

- `success` - Successful operations
- `error` - Error conditions
- `info` - Informational messages
- `warning` - Warning messages

## Testing Support

The authentication module supports testing with:

```python
# Test authentication
def test_login(client):
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 302

# Test admin registration
def test_admin_register(authenticated_admin_client):
    response = authenticated_admin_client.post('/auth/register', data={
        'username': 'newuser',
        'password': 'newpass',
        'confirm_password': 'newpass',
        'display_name': 'New User'
    })
    assert response.status_code == 302
```

## Configuration

Authentication configuration is handled via:

- Environment variables: `TRUNK8_ADMIN_PASSWORD`, `TRUNK8_SECRET_KEY`
- Session configuration: `permanent_lifetime_days` in config.toml
- User data: Stored in `users/users.toml`

## Next Steps

- [Links Module](links.md) - Link management with user context
- [User Manager](utils.md#usermanager-class) - User management utilities
- [Main Routes](main.md) - User management interface 