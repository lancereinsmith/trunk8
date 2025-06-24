# Backup and Restore

Trunk8 provides comprehensive backup and restore functionality to help you protect your links and files. This feature allows you to create complete backups of your data and restore them when needed.

## Features

- **Complete Backup**: Backs up all your links configuration and associated files
- **ZIP Format**: Creates standard ZIP files that are portable and secure
- **Metadata Tracking**: Includes backup metadata with timestamps and creator information
- **Selective Restore**: Choose to merge with existing data or replace it completely
- **Admin Support**: Administrators can backup and restore data for any user
- **Cross-Platform**: Works across different systems and installations

## Creating a Backup

### For Regular Users

1. **Navigate to Backup**: Click on the "Backup" dropdown in the navigation menu
2. **Select "Create Backup"**: Choose the backup creation option
3. **Download**: Click "Create & Download Backup" to generate and download your backup ZIP file

### For Administrators

1. **Navigate to Backup**: Click on the "Backup" dropdown in the navigation menu
2. **Select "Create Backup"**: Choose the backup creation option
3. **Choose User**: Select which user's data to backup from the dropdown
4. **Download**: Click "Create & Download Backup" to generate the backup

## Backup Contents

Each backup ZIP file contains:

- **`links.toml`**: Your complete links configuration
- **`assets/`**: Directory containing all your uploaded files
- **`backup_metadata.toml`**: Backup information including:
    - Creation timestamp
    - Target user
    - Creator information
    - Trunk8 version

## Restoring a Backup

### Basic Restore Process

1. **Navigate to Restore**: Click "Backup" → "Restore Backup" in the navigation
2. **Select File**: Choose your backup ZIP file
3. **Choose Restore Mode**: Select merge or replace mode
4. **Upload**: Click "Restore Backup" to process the file

### Restore Modes

#### Merge Mode (Recommended)
- **Safe Option**: Preserves your existing data
- **Conflict Resolution**: Backup data takes precedence for duplicate link codes
- **Additive**: Adds backup links to your existing collection
- **File Handling**: Overwrites files with same names

#### Replace Mode (Caution Required)
- **Complete Replacement**: Deletes ALL existing links and files
- **Fresh Start**: Restores only the backup data
- **Irreversible**: Cannot be undone
- **Use Case**: Clean restoration or disaster recovery

## Security Considerations

### Backup Security
- **File Protection**: Store backup files in secure locations
- **Access Control**: Backup files contain all your data and files
- **Regular Backups**: Create backups regularly for data protection
- **Version Control**: Keep multiple backup versions

### Restore Safety
- **Verification**: Verify backup file integrity before restoring
- **Test Restores**: Test restore process in non-production environments
- **Backup Before Restore**: Create a backup before restoring (especially for replace mode)

## Administrative Features

### Multi-User Backup
Administrators can:

- Create backups for any user
- Restore backups to any user account
- Cross-user data migration
- Bulk user data management

### User Management
- **User Selection**: Choose source and target users for operations
- **Permission Validation**: Automatic permission checking
- **Audit Trail**: Backup metadata tracks administrative actions

## Best Practices

### Regular Backups
- **Schedule**: Create backups regularly (weekly/monthly)
- **Automation**: Consider automating backup creation
- **Storage**: Store backups in multiple secure locations
- **Testing**: Periodically test restore functionality

### Disaster Recovery
- **Complete Backups**: Always backup both links and files
- **Documentation**: Document your backup and restore procedures
- **Recovery Plan**: Have a clear disaster recovery plan
- **Multiple Copies**: Keep backups in different locations

### Data Migration
- **User Transfer**: Use backup/restore for moving data between users
- **System Migration**: Transfer data between Trunk8 installations
- **Selective Migration**: Use merge mode for partial data transfers

## Troubleshooting

### Common Issues

#### Backup Creation Failed
- **Disk Space**: Ensure sufficient disk space for ZIP creation
- **Permissions**: Check file system permissions
- **Large Files**: Very large files may cause timeouts

#### Restore Failed
- **File Format**: Ensure backup file is a valid ZIP
- **Corrupted Backup**: Re-download or use a different backup file
- **Disk Space**: Ensure sufficient space for restoration
- **File Conflicts**: Check for file permission issues

#### Permission Errors
- **User Context**: Ensure proper user authentication
- **Admin Rights**: Verify admin permissions for cross-user operations
- **File Access**: Check file system permissions

### Error Messages

- **"Invalid backup file"**: ZIP file is corrupted or not a Trunk8 backup
- **"Missing links.toml"**: Backup file structure is invalid
- **"Permission denied"**: Insufficient rights for the operation
- **"User not found"**: Target user doesn't exist in the system

## API Integration

The backup functionality integrates with Trunk8's authentication system:

- **Authentication Required**: All backup operations require login
- **Session Management**: Uses existing user sessions
- **Permission Checking**: Automatic authorization validation
- **Admin Privileges**: Special handling for administrative users

## File Format Specification

### Backup ZIP Structure
```
backup_file.zip
├── links.toml              # User's links configuration
├── assets/                 # User's uploaded files
│   ├── file1.txt
│   ├── image.png
│   └── document.pdf
└── backup_metadata.toml    # Backup information
```

### Metadata Format
```toml
[backup_info]
created_by = "admin"
target_user = "username"
created_at = "2024-01-15T10:30:00"
trunk8_version = "1.0"
```

## Future Enhancements

Planned improvements include:
  
- **Scheduled Backups**: Automatic backup creation
- **Incremental Backups**: Only backup changed files
- **Cloud Storage**: Direct backup to cloud services
- **Encryption**: Optional backup file encryption
- **Compression Options**: Different compression levels 