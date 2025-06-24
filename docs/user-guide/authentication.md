# Authentication

Trunk8 supports both multi-user authentication and administrator single-password mode.

## Multi-User Authentication

### User Accounts

Trunk8 uses individual user accounts with:

- **Username and password** for each user
- **Isolated data storage** in `users/{username}/` directories
- **Admin privileges** for user management
- **User switching** for admin users

### Login Process

1. Navigate to your Trunk8 instance
2. You'll be redirected to `/auth/login`
3. Enter your **username** and **password**
4. Check "Remember me" to stay logged in for 30 days

### User Types

#### Regular Users
- Can manage their own links and files
- Access to personal dashboard and settings
- Data stored in `users/{username}/`

#### Admin Users
- Can manage their own content
- **User Management** - Create, view, and delete users
- **User Switching** - View system from any user's perspective
- **Global Access** - Can view and edit all users' links

### User Management (Admin Only)

Admin users can:

- **Create new users** at `/auth/register`
- **View all users** at `/users`
- **Switch user context** to help with support
- **Delete users** (except admin user)

## Administrator Single-Password Mode

For administrator access, you can use single-password authentication:

1. Leave the **username field blank**
2. Enter the admin password
3. System automatically creates admin user if needed

### Setting Admin Password

Configure via environment variable:
```bash
export TRUNK8_ADMIN_PASSWORD="your-secure-password"
```

Or in `.env` file:
```
TRUNK8_ADMIN_PASSWORD=your-secure-password
TRUNK8_SECRET_KEY=your-secret-key
```

Default password is `admin` if not configured. **Always change this in production!**

## Session Management

### Session Duration

Sessions last:
- 30 minutes without "Remember me"
- 30 days with "Remember me" checked (configurable)

Configure in `config/config.toml`:
```toml
[session]
permanent_lifetime_days = 7  # Change to 7 days
```

### User Switching (Admin Only)

Admin users can switch to view the system from any user's perspective:

1. Navigate to `/users` 
2. Click "Switch to User" for any user
3. View their dashboard and links
4. Click "Switch Back" to return to admin view

### Logging Out

Click "Logout" in the navigation to end your session immediately.

## Security Best Practices

### For Multi-User Systems

1. **Strong Passwords for All Users**
    - Minimum 12 characters
    - Mix of letters, numbers, symbols
    - Unique passwords for each user

2. **Admin Account Security**
    - Use secure admin password
    - Limit admin privileges
    - Regular password rotation

3. **User Account Management**
    - Remove unused accounts
    - Regular access audits
    - Monitor user activity

### General Security

1. **Environment Security**
    - Use HTTPS in production
    - Restrict admin access by IP
    - Enable rate limiting

2. **Data Protection**
    - Each user's data is isolated
    - Files stored with secure names
    - Regular backups of user data

## Troubleshooting

### Can't Log In

Check:

- Correct username and password (case-sensitive)
- Account hasn't been deleted by admin
- System is in correct authentication mode

### Forgot Password

**For Regular Users:**

1. Contact admin user
2. Admin can reset password via user management

**For Admin User:**

1. Access server directly
2. Set new password via `TRUNK8_ADMIN_PASSWORD`
3. Restart application

### User Not Found

If username doesn't exist:

1. Check spelling (case-sensitive)
2. Contact admin to create account
3. Use admin mode if admin password is known

### Session Issues

If session expires:

1. You'll be redirected to login
2. Enter credentials again
3. Previous work is preserved


## Public vs Admin Access

### Public Access (No Auth Required)
- Accessing short links (`/shortcode`)
- Downloading files
- Viewing markdown content

### Admin Access (Auth Required)
- Creating new links (`/add`)
- Editing links (`/edit_link/code`)
- Deleting links
- Viewing all links (`/links`)
- Changing settings (`/settings`) 

## Next Steps

- Learn about [User Management](managing-links.md)
- Explore [Multi-User Features](../user-guide/overview.md)
- Configure [Settings](../user-guide/settings.md)
