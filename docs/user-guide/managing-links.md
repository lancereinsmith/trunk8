# Managing Links

This guide covers creating, editing, and managing links in Trunk8.

## Creating Links

### Access the Add Link Page

1. Log in to Trunk8
2. Click "Add Link" in the navigation
3. Fill out the link form

### Link Properties

#### Short Code
- Unique identifier for your link
- Examples: `docs`, `report-2024`, `team-photo`
- Allowed characters: letters, numbers, hyphens, underscores
- Case-sensitive (use lowercase for consistency)

#### Link Type
Choose from four types:

1. **Redirect** - Forwards to another URL
2. **File** - Serves a downloadable file
3. **Markdown** - Renders markdown as HTML
4. **HTML** - Renders raw HTML content

#### Expiration Date (Optional)
- Set when the link should expire
- Format: `YYYY-MM-DD HH:MM:SS`
- Expired links are automatically deleted

### Type-Specific Fields

#### For Redirect Links
- **Target URL**: Full URL including `http://` or `https://`
- Examples:
    - `https://github.com/lancereinsmith/trunk8`
    - `https://example.com/very/long/url/that/needs/shortening`

#### For File Links
- **Choose File**: Select file to upload
- All file types supported
- Files are renamed for security
- Original filename preserved in download

#### For Markdown Links
Two options:

1. **Upload .md file**: Select a markdown file
2. **Enter text**: Type/paste markdown directly

#### For HTML Links
Two options:

1. **Upload .html file**: Select an HTML file
2. **Enter HTML**: Type/paste HTML content directly

!!! note "Auto-Detection"
    HTML files uploaded to the markdown section are automatically detected and rendered as HTML.

## Viewing Links

### List All Links

1. Click "List Links" in navigation
2. View all links in a table with:
    - Short code
    - Link type
    - Target/content preview
    - Expiration status
    - Action buttons

### Link Information

Each link shows:

- **Type icon**: 🔗 (redirect), 📁 (file), 📝 (markdown), 💻 (HTML)
- **Short code**: Click to visit link
- **Target**: URL, filename, markdown preview, or HTML preview
- **Expires**: Expiration date or "Never"

## Editing Links

### Access Edit Page

1. From the links list, click "Edit" button
2. Or navigate to `/edit_link/shortcode`

### What _Cannot_ Be Edited:
- Short code (delete and recreate instead)

### What _Can_ Be Edited

#### Redirect Links
- Target URL

#### File Links
- Upload a replacement file
- Original file is deleted

#### Markdown Links
- Edit markdown content
- Upload new markdown file

#### HTML Links
- Edit HTML content
- Upload new HTML file

#### All Link Types
- Expiration date

### Saving Changes

1. Make your modifications
2. Click "Update Link"
3. Confirmation message appears

## Deleting Links

### Delete Process

1. From links list, click "Delete" button
2. Confirm deletion in popup
3. Link and associated files are removed

### What Gets Deleted

- Link data from your user's `links.toml` file
- Uploaded files (for file/markdown/HTML types)
- Cannot be recovered - backup first!

## Bulk Operations

### Direct TOML Editing

For bulk operations, edit your user's `links.toml` file directly (located at `users/{username}/links.toml`):

```toml
# Add multiple redirects
[links.github]
type = "redirect"
url = "https://github.com/lancereinsmith/trunk8"

[links.docs]
type = "redirect"
url = "https://trunk8.readthedocs.io"

[links.demo]
type = "redirect"
url = "https://demo.trunk8.com"
```

After editing:

1. Save the file
2. Trunk8 reloads automatically
3. No restart required

### Bulk Import Script

Create a Python script for bulk imports:

```python
import toml

# Load existing links (use appropriate user directory)
with open('users/admin/links.toml', 'r') as f:
    config = toml.load(f)

# Add new links
new_links = {
    'link1': {'type': 'redirect', 'url': 'https://example1.com'},
    'link2': {'type': 'redirect', 'url': 'https://example2.com'},
}

for code, data in new_links.items():
    config['links'][code] = data

# Save
with open('users/admin/links.toml', 'w') as f:
    toml.dump(config, f)
```

## Organization Strategies

### Naming Conventions

Use prefixes for organization:

- `doc-api` - API documentation
- `doc-user` - User guide
- `file-report` - Report download
- `temp-meeting` - Temporary link

### Categories

Group related links:
```toml
# Team Resources
[links.team-handbook]
[links.team-calendar]
[links.team-directory]

# Project Alpha
[links.alpha-spec]
[links.alpha-demo]
[links.alpha-repo]
```

### Temporary Links

For time-sensitive content:

1. Set expiration date
2. Links auto-delete after expiring

## Search and Filter

### Finding Links

Currently manual, but you can:

1. Use browser's find (Ctrl/Cmd + F)
2. Search in user's `links.toml` file

### Future Enhancements

Planned features:
- Search by short code
- Filter by type
- Sort by clicking column headers
- Sort by expiration
- Tag system

## Best Practices

### Do's

- ✅ Use descriptive short codes
- ✅ Set expiration for temporary content
- ✅ Organize with naming conventions
- ✅ Regular backups of user `links.toml` files
- ✅ Test links after creation

### Don'ts

- ❌ Use spaces in short codes
- ❌ Create duplicate codes
- ❌ Upload sensitive files without expiration
- ❌ Use special characters (except `-` and `_`)
- ❌ Forget to backup before bulk changes

## Troubleshooting

### Link Not Working

1. Check short code spelling
2. Verify link hasn't expired
3. Ensure target URL is valid
4. Check file still exists

### Can't Edit Link

- Ensure you're logged in
- Check file permissions on server
- Verify user's `links.toml` isn't corrupted

### Bulk Import Failed

- Validate TOML syntax
- Check for duplicate short codes
- Ensure file permissions allow writing

## Advanced Usage

### Programmatic Access

Access links directly:
```python
import toml

# Read links
with open('users/admin/links.toml', 'r') as f:
    links = toml.load(f)['links']

# Count by type
by_type = {}
for code, data in links.items():
    link_type = data.get('type', 'unknown')
    by_type[link_type] = by_type.get(link_type, 0) + 1

print(f"Total links: {len(links)}")
print(f"By type: {by_type}")
```

### Custom Integrations

Create shortcuts or bookmarklets:
```javascript
// Bookmarklet to create Trunk8 link
javascript:(function(){
  const url = encodeURIComponent(window.location.href);
  window.open('https://trunk8.example.com/add?url=' + url);
})();
```

## Next Steps

- Learn about [Link Types](link-types.md) in detail
- Explore [Theme Customization](themes.md)
- Configure [Settings](settings.md) 