# User Guide Overview

Welcome to the Trunk8 User Guide! This comprehensive guide will help you master all features of Trunk8, from basic link shortening to advanced configuration.

## What is Trunk8?

Trunk8 is a self-hosted link shortener and file hosting platform that gives you complete control over your shortened URLs and hosted files. Unlike commercial services, Trunk8 runs on your own infrastructure, ensuring privacy and customization.

## Core Concepts

### Links

In Trunk8, a "link" is any shortened URL that maps a short code to content. Links can be:

- **Redirects** - Forward users to another URL
- **Files** - Serve uploaded files for download
- **Markdown** - Render markdown content as HTML

### Short Codes

Short codes are the unique identifiers in your URLs:

- Example: In `http://trunk8.com/docs`, `docs` is the short code
- Can contain letters, numbers, hyphens, and underscores
- Case-sensitive (though lowercase is recommended)
- Must be unique across all users in your Trunk8 instance and not conflict with reserved words

### Authentication

Trunk8 uses password-based authentication to protect administrative functions:

- Public users can access links without authentication
- Administrators must log in to create, edit, or delete links
- Sessions persist for 30 days by default (configurable)

## User Interface Overview

### Navigation Bar

The navigation bar provides quick access to all features:

- **Home** - Welcome page with quick stats
- **Add Link** - Create new shortened links
- **List Links** - View and manage all links
- **Backup/Restore** - Create and restore data backups
- **Settings** - Configure themes and preferences
- **Logout** - End your session

### Dashboard

The home page displays:

- Total number of active links
- Quick actions for common tasks
- System status information

## Common Workflows

### Creating a Short Link

1. Navigate to "Add Link"
2. Choose a memorable short code
3. Select the link type
4. Provide the content (URL, file, or markdown)
5. Optionally set an expiration date
6. Click "Create Link"

### Sharing Links

Once created, links are immediately accessible:

- Copy the full URL from the success page
- Share via email, chat, or social media
- Links work without authentication

### Managing Links

From the "All Links" page:

- **Copy** - Click a short code to copy URL to the clipboard
- **Visit** - Visit a particular link in a new browser tab
- **Edit** - Update link properties
- **Delete** - Remove links permanently

## Features in Detail

### Link Types

Trunk8 supports three primary link types:

#### Redirect Links

- Shortening long URLs
- Creating memorable bookmarks
- Tracking frequently shared links

#### File Links

- Sharing documents
- Hosting images
- Distributing downloads

#### Markdown Links

- Quick documentation
- Formatted announcements
- Rich content sharing

### Expiration Dates

Set links to automatically expire:

- Temporary file shares
- Time-limited promotions
- Event-specific content

### Theme Customization

Personalize Trunk8's appearance:

- 25+ built-in themes
- Separate themes for UI and markdown
- Instant preview without restart

## Best Practices

### Naming Conventions

Create consistent, memorable short codes:

✅ **Good Examples:**

- `team-roster`
- `q4-report`
- `api-docs`

❌ **Avoid:**

- `link1`, `link2` (not descriptive)
- `MyFile` (inconsistent casing)
- Special characters (except `-` and `_`)

### Organization Strategies

#### By Category
- `docs-` prefix for documentation
- `file-` prefix for downloads
- `temp-` prefix for temporary links

#### By Date
- `2024-01-meeting`
- `2024-q1-results`
- `2024-holiday-party`

#### By Project
- `project-alpha-spec`
- `project-beta-demo`
- `project-gamma-results`

### Security Considerations

1. **Regular Password Changes** - Update admin password periodically
2. **Link Audits** - Review and remove old links
3. **Sensitive Content** - Consider expiration dates for confidential files
4. **Access Logs** - Monitor server logs for unusual activity

## Troubleshooting

### Common Issues

#### "Link not found"
    - Check the short code spelling
- Verify the link hasn't expired
- Ensure you're using the correct domain

#### Can't upload files
- Check file size limits
- Verify file type is allowed
- Ensure adequate disk space

#### Theme not applying
- Clear browser cache
- Try a different browser
- Check for JavaScript errors

### Getting Help

If you encounter issues:

1. Check the [FAQ](../reference/faq.md)
2. Review error messages carefully
3. Search [GitHub Issues](https://github.com/lancereinsmith/trunk8/issues)
4. Create a detailed bug report

## Next Steps

Explore specific features in detail:

- [Authentication](authentication.md) - Security and session management
- [Managing Links](managing-links.md) - CRUD operations
- [Link Types](link-types.md) - Deep dive into each type
- [Backup and Restore](backup-restore.md) - Data protection and recovery
- [Themes](themes.md) - Customization options
- [Settings](settings.md) - Configuration interface 