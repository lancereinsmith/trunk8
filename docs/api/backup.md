# Backup API Reference

The backup module provides functionality for creating and restoring user data backups in Trunk8. This module allows users to export their links and assets as ZIP archives and restore them later.

## Module Overview

**Location**: `app/backup/`  
**Blueprint**: `backup_bp`  
**URL Prefix**: `/backup`

## Routes

### Create Backup

**Route**: `/backup/create`  
**Methods**: `GET`, `POST`  
**Authentication**: Required (`@login_required`)

Creates and downloads a backup ZIP file containing the user's data.

#### GET Request
Displays the backup creation form with:

- List of available users (admin only)
- Backup options and information

#### POST Request
Generates and downloads a ZIP backup containing:

- `links.toml` - User's link data
- `config.toml` - User's personal configuration (non-admin users only)  
- `assets/` - All uploaded files and assets
- `backup_metadata.toml` - Backup metadata and creation info

#### Parameters
- `target_user` (POST): Username to backup (admin can backup any user)

#### Response
- **Success**: ZIP file download with filename `trunk8_backup_{username}_{timestamp}.zip`
- **Error**: Flash message and redirect to backup form

#### Permissions
- Users can backup their own data
- Admins can backup any user's data
- Admin backups do not include personal `config.toml` (uses global config)

### Restore Backup

**Route**: `/backup/restore`  
**Methods**: `GET`, `POST`  
**Authentication**: Required (`@login_required`)

Restores user data from an uploaded backup ZIP file.

#### GET Request
Displays the restore form with:

- File upload field
- Restore mode selection (merge/replace)
- Target user selection (admin only)

#### POST Request
Processes uploaded backup file and restores data.

#### Parameters
- `backup_file` (POST): Uploaded ZIP file
- `restore_mode` (POST): `merge` or `replace`
  - `merge`: Combines backup data with existing data (backup takes precedence)
  - `replace`: Completely replaces existing data with backup
- `target_user` (POST): Username to restore to (admin only)

#### Response
- **Success**: Flash message with restore statistics and redirect to links list
- **Error**: Flash message and redirect to restore form

#### Permissions
- Users can restore to their own account
- Admins can restore to any user's account
- Validates target user exists before processing

## Backup File Structure

Backup ZIP files contain the following structure:

```
trunk8_backup_{username}_{timestamp}.zip
├── links.toml              # User's link data
├── config.toml             # User configuration (non-admin only)
├── assets/                 # User's uploaded files
│   ├── file1.pdf
│   ├── image.jpg
│   └── document.md
└── backup_metadata.toml    # Backup metadata
```

### Metadata File Format

```toml
[backup_info]
created_by = "admin"
target_user = "john"
created_at = "2024-12-22T10:30:00"
trunk8_version = "1.0"
```

## Functions

### `create_backup()`

```python
@backup_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_backup() -> Union[str, Response]:
```

Creates and downloads a backup ZIP file containing user's links and assets.

**Parameters**:
- None (uses form data and session)

**Returns**:
- `str`: Rendered template for GET requests
- `Response`: File download for successful POST requests
- `Response`: Redirect for errors

**Raises**:
- Flashes error messages for various failure conditions

### `restore_backup()`

```python
@backup_bp.route("/restore", methods=["GET", "POST"])
@login_required
def restore_backup() -> Union[str, Response]:
```

Restores user data from an uploaded backup ZIP file.

**Parameters**:
- None (uses form data and uploaded files)

**Returns**:
- `str`: Rendered template for GET requests
- `Response`: Redirect after processing POST requests

**Raises**:
- Flashes error messages for invalid files or permissions

## Security Considerations

### File Validation

- Validates ZIP file format before processing
- Uses `secure_filename()` for uploaded files
- Checks file structure and required components

### Permission Checks

- Users can only backup/restore their own data
- Admin privileges required for cross-user operations
- Validates target user existence

### Data Integrity

- Creates temporary files in secure locations
- Atomic operations where possible
- Cleanup of temporary files after processing

## Usage Examples

### Creating a Backup (User)
1. Navigate to `/backup/create`
2. Click "Create Backup" button
3. Download the generated ZIP file

### Creating a Backup (Admin)
1. Navigate to `/backup/create`
2. Select target user from dropdown
3. Click "Create Backup" button  
4. Download the generated ZIP file

### Restoring a Backup
1. Navigate to `/backup/restore`
2. Select backup ZIP file
3. Choose restore mode (merge/replace)
4. Select target user (admin only)
5. Click "Restore Backup" button

## Error Handling

Common error conditions and responses:

| Error | Response |
|-------|----------|
| No file selected | Flash error: "No backup file selected." |
| Invalid ZIP file | Flash error: "Invalid backup file. Please upload a valid zip file." |
| Missing links.toml | Flash error: "Invalid backup file. Missing links.toml." |
| Permission denied | Flash error: "You don't have permission to backup/restore other users' data." |
| User not found | Flash error: "User '{username}' not found." |
| Processing error | Flash error with specific error message |

## Templates

### `backup_create.html`
Form for creating backups with user selection (admin) and backup information.

### `backup_restore.html`  
Form for uploading and restoring backups with restore mode options.

## Dependencies

- `os`, `tempfile` - File system operations
- `zipfile` - ZIP archive handling
- `datetime` - Timestamp generation
- `toml` - Configuration file parsing
- `werkzeug.utils.secure_filename` - Secure file name handling
- `flask` - Web framework components

## Integration

The backup module integrates with:
- **Authentication**: Uses `@login_required` decorator
- **User Management**: Validates users and permissions
- **Configuration**: Accesses user config and links files
- **File System**: Manages user assets and directories

## Best Practices

### For Users
- Create regular backups before making major changes
- Test restore process with non-critical data first
- Keep backup files in secure locations

### For Administrators
- Regular system-wide backups of all users
- Document backup/restore procedures
- Monitor backup file sizes and storage requirements

## Future Enhancements

Potential improvements for the backup system:

- **Scheduled Backups**: Automatic backup creation
- **Cloud Storage**: Direct backup to cloud services
- **Encryption**: Encrypt sensitive backup data 