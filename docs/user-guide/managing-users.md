# Managing Users

This guide covers user management functionality for administrators in Trunk8's multi-user environment.

## Overview

Trunk8 supports multi-user functionality where administrators can create, manage, and delete user accounts. Each user has their own isolated data space with separate links and assets.

## User Management Interface

### Accessing User Management

1. Log in as an administrator
2. Navigate to the **Users** page from the main menu
3. View all users and their statistics

### User Information Display

For each user, you can see:

- Username and display name
- Admin status (Admin/User badge)
- Number of links created
- Account creation date
- Total data usage

## Creating Users

### Registration Process

1. Click **Add User** on the Users page
2. Fill in the registration form:
    - **Username**: Unique identifier (3+ characters, letters/numbers/hyphens/underscores only)
    - **Password**: User password (4+ characters minimum)
    - **Display Name**: Human-readable name for the user
    - **Admin Privileges**: Check to grant admin access
3. Click **Register** to create the user

### User Directory Structure

When a user is created, Trunk8 automatically creates:
```
users/
├── username/
│   ├── assets/          # User's uploaded files
│   └── links.toml       # User's link configuration
```

## Deleting Users

### ⚠️ Cascading Deletion Warning

**When you delete a user, ALL of their data is permanently removed, including:**
- User account and authentication
- All user's links (redirect, file, and markdown links)
- All uploaded files and assets
- Entire user directory structure

**This action cannot be undone!**

### Deletion Process

1. Navigate to the **Users** page
2. Find the user you want to delete
3. Click **Delete User** or go to the user's detail page
4. Confirm the deletion in the dialog box
5. The system will:
    - Remove all user links
    - Delete all user files and assets
    - Remove the user directory
    - Remove the user account
    - Log cleanup statistics

### Deletion Preview

Before deleting a user, you can view their data on the user detail page:

- Number of links that will be deleted
- Number of files that will be removed
- Total storage space that will be freed
- List of directories that will be deleted

### Deletion Restrictions

- The **admin** user cannot be deleted
- Only administrators can delete users
- Users cannot delete themselves or other users

### Error Handling

The system handles various error conditions during deletion:

- **Permission Errors**: If files cannot be deleted due to permissions, the user account is still removed
- **Missing Files**: If files are already missing, deletion continues normally
- **Corrupted Data**: If link files are corrupted, cleanup proceeds with warnings
- **Partial Failures**: Any cleanup issues are logged, but user removal continues

## User Switching (Admin Feature)

### Viewing as Another User

Administrators can switch to view the system as any user:

1. Go to the **Users** page or user detail page
2. Click **View as User**
3. The interface will switch to show that user's perspective
4. You'll see their links, assets, and have their permissions
5. Click **Switch Back** to return to admin view

### Benefits of User Switching

- Test user experience without separate login
- Troubleshoot user-specific issues
- Verify user permissions and data isolation
- Assist users with their configuration

## Best Practices

### Before Deleting Users

1. **Backup Important Data**: Export any links or files that should be preserved
2. **Notify the User**: Ensure the user knows their account will be deleted
3. **Review Data**: Check the user detail page to understand what will be lost
4. **Document Reasons**: Keep records of why the account was deleted

### User Account Management

1. **Regular Audits**: Periodically review user accounts and usage
2. **Cleanup Inactive Accounts**: Remove accounts that are no longer needed
3. **Monitor Storage**: Keep track of total system storage usage
4. **Security Reviews**: Regularly review admin privileges

### Data Recovery

- **No Built-in Recovery**: Deleted user data cannot be recovered through the interface
- **Backup Strategy**: Implement regular backups of the entire `users/` directory
- **Export Before Deletion**: Manually backup important user data before deletion

## Security Considerations

### Admin Privileges

- Only grant admin access to trusted users
- Regularly review who has admin privileges
- Consider using separate admin accounts for different purposes

### Data Isolation

- Users cannot access other users' data
- Each user has completely separate storage
- File paths are isolated per user

### Audit Trail

- User creation and deletion are logged
- Cleanup statistics are recorded
- Failed operations are logged with details

## API Integration

The user management functionality is also available through the system's internal APIs:

- `UserManager.create_user()`: Create new users programmatically
- `UserManager.delete_user()`: Delete users with full cleanup
- `UserManager.get_user_deletion_preview()`: Preview deletion impact
- `UserManager.list_users()`: Get all users in the system

For detailed API documentation, see the [API Reference](../api/overview.md). 