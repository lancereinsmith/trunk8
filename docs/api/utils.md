# Utilities Module (app.utils)

The utilities module provides core functionality for configuration management and user administration in Trunk8's multi-user environment.

## Overview

The `app.utils` module contains:

- **ConfigLoader** - TOML configuration management with automatic reloading
- **UserManager** - Multi-user authentication and account management

## ConfigLoader Class

### Overview

```python
class ConfigLoader:
    """
    Manages TOML configuration files with automatic reloading.
    
    Handles application config, user-specific links config, and themes config
    with file modification tracking and automatic reloading.
    """
```

### Initialization

```python
def __init__(self) -> None:
    """Initialize the ConfigLoader with default file paths."""
```

**Default Configuration Files:**

- `config/config.toml` - Application settings
- `config/themes.toml` - Available themes
- User-specific links files based on current user context

### Core Methods

#### load_all_configs()

```python
def load_all_configs(self) -> None:
    """
    Load all configuration files.
    
    Checks modification times and reloads only changed files.
    """
```

**Features:**

- Automatic modification time tracking
- Selective reloading of changed files
- Error handling for missing or corrupt files
- Default value creation

#### set_user_context()

```python
def set_user_context(self, username: Optional[str]) -> None:
    """
    Set the current user context for configuration loading.
    
    Args:
        username: Current active username
    """
```

**Features:**

- User-specific configuration isolation
- Dynamic user switching support
- Admin user context management

#### save_app_config()

```python
def save_app_config(self) -> bool:
    """
    Save application configuration to file.
    
    Returns:
        True if saved successfully, False otherwise.
    """
```

### Configuration Properties

#### app_config

```python
@property
def app_config(self) -> Dict[str, Any]:
    """Get current application configuration."""
```

Structure:
```toml
[app]
theme = "cerulean"
markdown_theme = "cerulean"

[session]
permanent_lifetime_days = 30
```

#### links_config

```python
@property  
def links_config(self) -> Dict[str, Any]:
    """Get current user's links configuration."""
```

Structure:
```toml
[links.shortcode]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"
```

#### themes_config

```python
@property
def themes_config(self) -> Dict[str, Any]:
    """Get available themes configuration."""
```

Structure:
```toml
[themes.cerulean]
name = "Cerulean"
description = "A calm blue sky"
```



### Error Handling

```python
# Configuration loading errors
try:
    config = toml.load(config_file)
except FileNotFoundError:
    # Create default configuration
except toml.TomlDecodeError:
    # Handle invalid TOML syntax
except Exception as e:
    # General error handling
```

## UserManager Class

### Overview

```python
class UserManager:
    """
    Manages user accounts, authentication, and user-specific data access.
    
    Handles user creation, authentication, password management, and provides
    admin functionality to manage all users and their data.
    """
```

### Initialization

```python
def __init__(self, users_file: str = "users/users.toml") -> None:
    """
    Initialize the UserManager.
    
    Args:
        users_file: Path to the users configuration file.
    """
```

### Authentication Methods

#### authenticate_user()

```python
def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user with username and password.
    
    For admin user: password is checked against TRUNK8_ADMIN_PASSWORD environment variable.
    For other users: password is checked against stored hash.
    
    Args:
        username: Username to authenticate.
        password: Plain text password.
        
    Returns:
        User data dict if authenticated, None otherwise.
    """
```

**Authentication Modes:**

1. **Admin User**: Uses `TRUNK8_ADMIN_PASSWORD` environment variable
2. **Regular Users**: Uses SHA-256 hashed passwords stored in users.toml

### User Management Methods

#### create_user()

```python
def create_user(
    self, username: str, password: str, display_name: str, is_admin: bool = False
) -> bool:
    """
    Create a new user.
    
    Args:
        username: Unique username.
        password: Plain text password.
        display_name: Display name for the user.
        is_admin: Whether user has admin privileges.
        
    Returns:
        True if user created successfully, False otherwise.
    """
```

**Creation Process:**

1. Validate username uniqueness
2. Hash password using SHA-256
3. Create user entry in users.toml
4. Create user directory structure
5. Initialize empty links.toml

#### get_user()

```python
def get_user(self, username: str) -> Optional[Dict[str, Any]]:
    """
    Get user data by username.
    
    Args:
        username: Username to retrieve.
        
    Returns:
        User data dict if found, None otherwise.
    """
```

#### list_users()

```python
def list_users(self) -> List[str]:
    """
    Get list of all usernames.
    
    Returns:
        List of usernames.
    """
```

#### is_admin()

```python
def is_admin(self, username: str) -> bool:
    """
    Check if user has admin privileges.
    
    Args:
        username: Username to check.
        
    Returns:
        True if user is admin, False otherwise.
    """
```

### File Path Methods

#### get_user_links_file()

```python
def get_user_links_file(self, username: str) -> str:
    """
    Get path to user's links.toml file.
    
    Args:
        username: Username.
        
    Returns:
        Path to user's links file.
    """
```

#### get_user_assets_dir()

```python
def get_user_assets_dir(self, username: str) -> str:
    """
    Get path to user's assets directory.
    
    Args:
        username: Username.
        
    Returns:
        Path to user's assets directory.
    """
```

### User Deletion

#### delete_user()

```python
def delete_user(self, username: str, requesting_user: str) -> bool:
    """
    Delete a user and all associated data (admin only).
    
    This method performs a cascading deletion that removes:
    - User account from the configuration
    - All user's links
    - All user's uploaded files and assets
    - User's entire directory structure
    
    Args:
        username: Username to delete.
        requesting_user: Username making the request (must be admin).
        
    Returns:
        True if deleted successfully, False otherwise.
    """
```

#### get_user_deletion_preview()

```python
def get_user_deletion_preview(self, username: str) -> Optional[Dict[str, Any]]:
    """
    Get a preview of what will be deleted when a user is removed.
    
    This method provides information about what data will be lost
    without actually performing the deletion.
    
    Args:
        username: Username to preview deletion for.
        
    Returns:
        Dictionary with deletion preview information, or None if user not found.
    """
```

**Preview Information:**

- Number of links to be deleted
- Number of files to be removed
- Total storage space to be freed
- List of directories to be deleted

### Password Management

#### change_password()

```python
def change_password(self, username: str, new_password: str) -> bool:
    """
    Change user password.
    
    Args:
        username: Username.
        new_password: New plain text password.
        
    Returns:
        True if changed successfully, False otherwise.
    """
```

### Internal Methods

#### _hash_password()

```python
def _hash_password(self, password: str) -> str:
    """
    Hash a password using SHA-256.
    
    Args:
        password: Plain text password.
        
    Returns:
        Hashed password string.
    """
```

#### _create_user_directory()

```python
def _create_user_directory(self, username: str) -> None:
    """
    Create user directory structure.
    
    Args:
        username: Username to create directory for.
    """
```

Creates:

- `users/{username}/` directory
- `users/{username}/assets/` directory  
- `users/{username}/links.toml` file

#### _cleanup_user_data()

```python
def _cleanup_user_data(self, username: str) -> Tuple[bool, str, Dict[str, int]]:
    """
    Clean up all user data including links and assets.
    
    Args:
        username: Username to clean up data for.
        
    Returns:
        Tuple of (success, message, cleanup_stats).
        cleanup_stats contains counts of deleted items.
    """
```

## User Data Structure

### users.toml Format

```toml
[users.admin]
is_admin = true
display_name = "Administrator"  
created_at = "2024-01-01T00:00:00"
# password_hash not stored for admin (uses environment variable)

[users.username]
password_hash = "sha256_hash_here"
is_admin = false
display_name = "User Display Name"
created_at = "2024-01-01T00:00:00"
```

### Directory Structure

```
users/
├── users.toml              # User management data
├── admin/
│   ├── links.toml          # Admin's links
│   └── assets/             # Admin's files
└── username/
    ├── links.toml          # User's links
    └── assets/             # User's files
```

## Integration Examples

### Application Factory Integration

```python
# In create_app()
config_loader = ConfigLoader()
user_manager = UserManager()



# Load configurations
config_loader.load_all_configs()

# Make available to app
app.config_loader = config_loader
app.user_manager = user_manager
```

### Request Context Integration

```python
# Before each request
@app.before_request
def load_user_context():
    current_user = get_current_user()
    config_loader.set_user_context(current_user)
    config_loader.load_all_configs()
```

### Authentication Integration

```python
# In login route
user_data = user_manager.authenticate_user(username, password)
if user_data:
    session['authenticated'] = True
    session['username'] = username
    session['is_admin'] = user_data.get('is_admin', False)
```

## Performance Considerations

### Configuration Caching

- File modification time tracking
- Selective reloading of changed files
- In-memory configuration storage
- Efficient TOML parsing

### User Management

- Lazy loading of user data
- Efficient directory operations
- Bulk user operations support
- Optimized file cleanup

## Security Features

### Password Security

- SHA-256 password hashing
- Environment variable for admin password
- No plaintext password storage
- Secure password validation

### Data Isolation

- User-specific directory structure
- Isolated configuration files
- Access control validation
- Admin privilege checking

## Error Handling

### Configuration Errors

```python
# File not found
except FileNotFoundError:
    self._create_default_config()

# Invalid TOML syntax
except toml.TomlDecodeError as e:
    print(f"Invalid TOML syntax: {e}")
    
# Permission errors
except PermissionError:
    print("Permission denied accessing config file")
```

### User Management Errors

```python
# User not found
if username not in users:
    return None

# Admin deletion protection
if username == "admin":
    return False

# Permission validation
if not self.is_admin(requesting_user):
    return False
```

## Testing Support

### Configuration Testing

```python
def test_config_loading():
    config_loader = ConfigLoader()
    config_loader.load_all_configs()
    assert 'app' in config_loader.app_config

def test_user_context():
    config_loader = ConfigLoader()
    config_loader.set_user_context('testuser')
    assert config_loader._current_user == 'testuser'
```

### User Management Testing

```python
def test_user_creation():
    user_manager = UserManager()
    success = user_manager.create_user('testuser', 'password', 'Test User')
    assert success == True

def test_authentication():
    user_manager = UserManager()
    user_data = user_manager.authenticate_user('testuser', 'password')
    assert user_data is not None
```

## Next Steps

- [Application Factory](app.md) - Integration with Flask application
- [Authentication Module](auth.md) - Authentication system usage
- [Links Module](links.md) - Configuration integration 