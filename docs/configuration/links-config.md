# Links Data Storage (users/{username}/links.toml)

Each user's link data is stored in their own `links.toml` file located at `users/{username}/links.toml`. This is a data file, not a configuration file - it contains the actual links managed by each user.

## Multi-User File Structure

```
users/
├── users.toml              # User management data
├── admin/
│   ├── links.toml          # Admin user's links
│   └── assets/             # Admin user's files
├── john/
│   ├── links.toml          # John's links
│   └── assets/             # John's files
└── mary/
    ├── links.toml          # Mary's links
    └── assets/             # Mary's files
```

## Per-User Link File Structure

Each user's `links.toml` file follows the same format:

```toml
# Redirect link
[links.homepage]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-12-31T23:59:59"  # Optional

# File link (with UUID4 security and metadata)
[links.document]
type = "file"
path = "f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf"
original_filename = "Q4-Financial-Report-2024.pdf"
file_size = 2048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:30:00"
expiration_date = "2024-12-31T23:59:59"  # Optional

# Markdown link (file upload with UUID4)
[links.readme]
type = "markdown"
path = "9a8f6e4d-2b1c-4d3e-8f7a-6b5c4d3e2f1a.md"
original_filename = "project-readme.md"
upload_date = "2024-01-10T14:20:30"

# Markdown link (inline content)
[links.notes]
type = "markdown"
content = "# My Notes\n\nThis is inline markdown content."
```

## Data Isolation

### User Access Control
- **Regular users** can only access their own `users/{username}/links.toml` file
- **Admin users** can access all users' link files
- Web interface enforces these permissions automatically

### File Permissions
```bash
# Secure user data files
chmod 600 users/users.toml
chmod -R 600 users/*/links.toml
chmod -R 755 users/*/assets/
```

## Link Properties

### Required Properties

#### type
**Values**: `"redirect"`, `"file"`, `"markdown"`  
**Description**: Determines how the link behaves

#### type-specific properties
- **redirect**: Requires `url`
- **file**: Requires `path`
- **markdown**: Requires `path`

### Optional Properties

#### expiration_date
**Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)  
**Description**: When the link expires and is automatically deleted

## Link Types

### Redirect Links

Forward visitors to another URL:

```toml
[links.github]
type = "redirect"
url = "https://github.com/lancereinsmith/trunk8"

[links.docs]
type = "redirect"
url = "https://trunk8.readthedocs.io"
expiration_date = "2024-12-31T23:59:59"
```

### File Links

Serve downloadable files with UUID4 security and metadata:

```toml
[links.report]
type = "file"
path = "7f3e4a89-1234-5678-9abc-def012345678.pdf"
original_filename = "Annual-Report-2024.pdf"
file_size = 1048576
mime_type = "application/pdf"
upload_date = "2024-01-15T09:30:00"

[links.presentation]
type = "file"
path = "8a9b7c6d-5432-1098-fedc-ba9876543210.pptx"
original_filename = "Q1-Results-Presentation.pptx"
file_size = 2097152
mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
upload_date = "2024-02-01T14:20:00"
expiration_date = "2024-06-30T23:59:59"
```

### Markdown Links

Render markdown as HTML (file upload with UUID4):

```toml
[links.readme]
type = "markdown"
path = "9e8f7d6c-5b4a-3921-0edc-1a2b3c4d5e6f.md"
original_filename = "project-readme.md"
upload_date = "2024-01-10T10:15:00"

[links.changelog]
type = "markdown"
path = "1a2b3c4d-5e6f-7890-abcd-ef1234567890.md"
original_filename = "changelog-v2.md"
upload_date = "2024-01-20T16:45:00"
```

## Complete Example

```toml
# Company links
[links.home]
type = "redirect"
url = "https://company.com"

[links.blog]
type = "redirect"
url = "https://blog.company.com"

# Documents
[links.handbook]
type = "file"
path = "a1b2c3d4-e5f6-7890-1234-567890abcdef.pdf"
original_filename = "employee-handbook-2024.pdf"
file_size = 3145728
mime_type = "application/pdf"
upload_date = "2024-01-01T09:00:00"

[links.policies]
type = "markdown"
path = "b2c3d4e5-f6a7-8901-2345-678901bcdef0.md"
original_filename = "company-policies.md"
upload_date = "2024-01-01T09:30:00"

# Temporary links
[links.meeting-notes]
type = "markdown"
path = "c3d4e5f6-a7b8-9012-3456-789012cdef01.md"
original_filename = "meeting-2024-01-15.md"
upload_date = "2024-01-15T14:00:00"
expiration_date = "2024-01-31T23:59:59"

[links.temp-download]
type = "file"
path = "d4e5f6a7-b8c9-0123-4567-890123def012.zip"
original_filename = "temp-file-12345.zip"
file_size = 1572864
mime_type = "application/zip"
upload_date = "2024-01-20T10:00:00"
expiration_date = "2024-01-20T12:00:00"
```

## Short Code Guidelines

### Naming Conventions

**Allowed characters**:

- Letters: `a-z`, `A-Z`
- Numbers: `0-9`
- Hyphens: `-`
- Underscores: `_`

**Best practices**:

- Use lowercase for consistency
- Use hyphens for readability
- Keep them short but descriptive

**Good examples**:

- `docs`
- `api-guide`
- `q4-report`
- `team-photo-2024`

**Bad examples**:

- `my link` (spaces not allowed)
- `link@company` (special characters)
- `../../etc/passwd` (security risk)
- `a` (too short, not descriptive)

### Organization Patterns

#### By Category
```toml
# Documentation
[links.docs-api]
[links.docs-user]
[links.docs-admin]

# Files
[links.file-report]
[links.file-presentation]
[links.file-download]
```

#### By Date
```toml
[links.report-2024-01]
[links.report-2024-02]
[links.meeting-2024-01-15]
```

#### By Project
```toml
[links.project-alpha-spec]
[links.project-alpha-code]
[links.project-beta-docs]
```

## Manual Editing

### Adding Links

Add new link sections:

```toml
# Existing links...

# Add new link
[links.new-link]
type = "redirect"
url = "https://example.com"
```

### Updating Links

Modify properties directly:

```toml
[links.existing]
type = "redirect"
url = "https://old-url.com"  # Change to new URL
# url = "https://new-url.com"
```

### Deleting Links

Remove the entire section:

```toml
# Delete this entire block
# [links.old-link]
# type = "file"
# path = "b4c5d6e7-f8a9-0123-4567-89abcdef0123.pdf"
# original_filename = "old-file.pdf"
# file_size = 1048576
# mime_type = "application/pdf"
# upload_date = "2024-01-01T10:00:00"
```

## Bulk Operations

### Import Script

Create multiple links programmatically:

```python
import toml
from datetime import datetime, timedelta

# Load existing links (admin example)
with open('users/admin/links.toml', 'r') as f:
    config = toml.load(f)

# Add multiple redirects
urls = {
    'google': 'https://google.com',
    'github': 'https://github.com',
    'stackoverflow': 'https://stackoverflow.com'
}

for code, url in urls.items():
    config['links'][code] = {
        'type': 'redirect',
        'url': url
    }

# Save
with open('users/admin/links.toml', 'w') as f:
    toml.dump(config, f)
```

### Export Script

Export links to CSV:

```python
import toml
import csv

# Load links (admin example)
with open('users/admin/links.toml', 'r') as f:
    links = toml.load(f)['links']

# Export to CSV
with open('links_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Short Code', 'Type', 'Target', 'Expires'])
    
    for code, data in links.items():
        target = data.get('url') or data.get('path', '')
        expires = data.get('expiration_date', 'Never')
        writer.writerow([code, data['type'], target, expires])
```

### Cleanup Script

Remove expired links:

```python
import toml
from datetime import datetime

# Load links (admin example)
with open('users/admin/links.toml', 'r') as f:
    config = toml.load(f)

# Find expired links
now = datetime.now()
expired = []

for code, data in config['links'].items():
    if 'expiration_date' in data:
        exp_date = datetime.fromisoformat(data['expiration_date'])
        if exp_date < now:
            expired.append(code)

# Remove expired
for code in expired:
    print(f"Removing expired link: {code}")
    del config['links'][code]

# Save
with open('users/admin/links.toml', 'w') as f:
    toml.dump(config, f)
```

## Validation

### TOML Syntax

Validate file syntax:

```bash
python -m toml users/admin/links.toml
```

### Link Validation

Check for issues:

```python
import toml
import os

with open('users/admin/links.toml', 'r') as f:
    links = toml.load(f)['links']

for code, data in links.items():
    # Check required fields
    if 'type' not in data:
        print(f"Error: {code} missing type")
    
    # Check type-specific fields
    if data.get('type') == 'redirect' and 'url' not in data:
        print(f"Error: {code} missing url")
    
    if data.get('type') in ['file', 'markdown'] and 'path' not in data:
        print(f"Error: {code} missing path")
    
    # Check file existence (for file and markdown links)
    if 'path' in data:
        # Files are stored in user-specific assets directories
        # This example assumes checking admin user's files
        full_path = os.path.join('users', 'admin', 'assets', data['path'])
        if not os.path.exists(full_path):
            print(f"Warning: {code} file not found: {full_path}")
```

## Advanced Examples

### Time-Limited Campaign

```toml
[links.summer-sale]
type = "redirect"
url = "https://shop.example.com/summer-sale"
expiration_date = "2024-08-31T23:59:59"

[links.summer-banner]
type = "file"
path = "e5f6a7b8-c9d0-1234-5678-901234ef0123.jpg"
original_filename = "summer-sale-banner.jpg"
file_size = 524288
mime_type = "image/jpeg"
upload_date = "2024-06-01T12:00:00"
expiration_date = "2024-08-31T23:59:59"
```

### Documentation Hub

```toml
[links.docs]
type = "redirect"
url = "https://docs.example.com"

[links.api-reference]
type = "markdown"
path = "f6a7b8c9-d0e1-2345-6789-012345f01234.md"
original_filename = "api-reference.md"
upload_date = "2024-01-05T11:00:00"

[links.user-guide]
type = "file"
path = "a7b8c9d0-e1f2-3456-7890-123456f01235.pdf"
original_filename = "user-guide-v2.pdf"
file_size = 4194304
mime_type = "application/pdf"
upload_date = "2024-01-10T15:30:00"

[links.changelog]
type = "markdown"
path = "b8c9d0e1-f2a3-4567-8901-234567f01236.md"
original_filename = "changelog.md"
upload_date = "2024-01-15T16:45:00"
```

### Multi-Language Support

```toml
[links.guide-en]
type = "file"
path = "c9d0e1f2-a3b4-5678-9012-345678f01237.pdf"
original_filename = "guide-english.pdf"
file_size = 2097152
mime_type = "application/pdf"
upload_date = "2024-01-20T10:00:00"

[links.guide-es]
type = "file"
path = "d0e1f2a3-b4c5-6789-0123-456789f01238.pdf"
original_filename = "guide-spanish.pdf"
file_size = 2228224
mime_type = "application/pdf"
upload_date = "2024-01-20T10:15:00"

[links.guide-fr]
type = "file"
path = "e1f2a3b4-c5d6-7890-1234-56789af01239.pdf"
original_filename = "guide-french.pdf"
file_size = 2359296
mime_type = "application/pdf"
upload_date = "2024-01-20T10:30:00"
```

## Troubleshooting

### Common Issues

#### Duplicate Short Codes

TOML doesn't allow duplicate keys:
```toml
[links.test]  # First definition
type = "redirect"
url = "https://example1.com"

[links.test]  # ERROR: Duplicate!
type = "redirect"
url = "https://example2.com"
```

#### Invalid Characters

Fix special characters:
```toml
# Bad
[links.my link]  # Spaces not allowed

# Good
[links.my-link]
```

#### Missing Required Fields

Each link needs required fields:
```toml
# Bad
[links.broken]
type = "redirect"
# Missing url!

# Good
[links.working]
type = "redirect"
url = "https://example.com"
```

### File Path Issues

#### Relative vs Absolute

```toml
# UUID4 filename (recommended - automatically generated)
[links.doc]
type = "file"
path = "f2a3b4c5-d6e7-8901-2345-6789abcdef01.pdf"
original_filename = "document.pdf"
file_size = 1048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:00:00"

# Absolute paths (avoid - security risk)
[links.doc2]
type = "file"
path = "/home/user/document.pdf"  # DON'T DO THIS - security risk
```

#### Case Sensitivity

File paths are case-sensitive on Linux/Mac:
```toml
[links.image]
type = "file"
path = "a3b4c5d6-e7f8-9012-3456-789abcdef012.JPG"  # Must match exact filename
original_filename = "Photo.JPG"
file_size = 2097152
mime_type = "image/jpeg"
upload_date = "2024-01-15T12:00:00"
```

## Best Practices

### Backup Strategy

```bash
# Before major changes
cp users/admin/links.toml users/admin/links.toml.backup-$(date +%Y%m%d)

# Regular backups
0 3 * * * cp /path/to/users/admin/links.toml /backups/admin-links-$(date +\%Y\%m\%d).toml
```

### Documentation

Add comments for clarity:

```toml
# Marketing Campaign - Summer 2024
[links.summer-promo]
type = "redirect"
url = "https://promo.example.com/summer"
expiration_date = "2024-08-31T23:59:59"  # End of summer

# Internal Tools
[links.hr-portal]
type = "redirect"
url = "https://hr.internal.company.com"
# No expiration - permanent link
```

## Security Considerations

### Path Traversal

Never allow user input directly:
```toml
# Dangerous - could access system files
[links.danger]
type = "file"
path = "../../../etc/passwd"  # DON'T DO THIS

# Safe - use validated filenames
[links.safe]
type = "file"
path = "7f3e4a89-1234-5678-9abc-def012345678.pdf"
```

### URL Validation

Validate redirect URLs:
```python
from urllib.parse import urlparse

def is_safe_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https']
```

### Access Control

- Keep user `links.toml` files readable only by app
- Don't expose file paths publicly
- Regular security audits


## Next Steps

- Learn about [App Configuration](app-config.md)
- Understand [Themes](themes-config.md)
- Explore [Link Management](../user-guide/managing-links.md)
- Review [Security](../deployment/security.md) 