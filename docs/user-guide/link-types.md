# Link Types

Trunk8 supports four types of links, each serving different purposes. This guide explains each type in detail.

## Overview

| Type | Purpose | Use Case |
|------|---------|----------|
| **Redirect** | URL shortening | Shorten long URLs, create memorable bookmarks |
| **File** | File hosting | Share documents, images, downloads |
| **Markdown** | Content rendering | Host documentation, formatted text |
| **HTML** | Raw HTML hosting | Host pre-formatted web pages, custom layouts |

## Redirect Links

### What They Do

Redirect links forward visitors to another URL. When someone visits your short link, they're automatically redirected to the target URL.

### Creating Redirect Links

1. Choose "Redirect" as link type
2. Enter the target URL (must include `http://` or `https://`)
3. Set optional expiration date

### Example Configuration

```toml
[links.github]
type = "redirect"
url = "https://github.com/lancereinsmith/trunk8"
expiration_date = "2024-12-31T23:59:59"  # Optional
```

### Use Cases

- **Shorten long URLs**: Transform complex URLs into memorable ones
- **Marketing campaigns**: Track different campaign links
- **Temporary shares**: Set expiration for time-limited content
- **Internal bookmarks**: Create easy-to-remember shortcuts

### Best Practices

- Validate target URLs before creating
- Use HTTPS URLs when possible
- Test links after creation
- Monitor for broken external links

## File Links

### What They Do

File links allow you to upload and host files. Visitors can download the file when accessing the link.

### Creating File Links

1. Choose "File" as link type
2. Select file to upload
3. Renamed with UUID4 for security
4. Original filename preserved for download

### File Handling

#### Upload Process
1. File uploaded via web form
2. Assigned UUID4 filename for security
3. Original filename stored in metadata
4. MIME type automatically detected
5. File size and upload date recorded

#### Security Features
- **UUID4 naming**: Prevents filename guessing attacks
- **Original filename preservation**: Users see familiar names when downloading
- **File type validation**: Configurable allowed extensions
- **Size limits**: Configurable maximum file size (default: 100MB)
- **Metadata tracking**: Upload date, file size, MIME type

### Example Configuration

```toml
[links.report]
type = "file"
path = "9a8f6e4d-2b1c-4d3e-8f7a-6b5c4d3e2f1a.pdf"
original_filename = "Q4-Financial-Report-2024.pdf"
file_size = 2048576
mime_type = "application/pdf"
upload_date = "2024-01-15T10:30:00"
```

### Supported File Types

Enhanced validation supports common types:

- **Documents**: PDF, DOC, DOCX, TXT, RTF, ODT
- **Images**: JPG, JPEG, PNG, GIF, WEBP, BMP, SVG
- **Archives**: ZIP, RAR, 7Z, TAR, GZ
- **Spreadsheets**: XLS, XLSX, ODS, CSV
- **Presentations**: PPT, PPTX, ODP
- **Audio/Video**: MP3, WAV, MP4, AVI, MKV, MOV
- **Code**: PY, JS, HTML, CSS, JSON, XML, MD

### Use Cases

- **Document sharing**: Reports, presentations, guides
- **Media distribution**: Images, videos, audio
- **Software downloads**: Installers, packages
- **Data files**: Datasets, exports

### Best Practices

- Set expiration for sensitive files
- Monitor disk usage
- Regular cleanup of old files
- Use descriptive short codes
- Consider file size impact

## Markdown Links

### What They Do

Markdown links render markdown content as formatted HTML using StrapDown.js. Perfect for hosting documentation or formatted text.

### Creating Markdown Links

Two methods:

1. **Upload markdown file**
    - Select `.md` file
    - Content stored with UUID4 filename

2. **Enter markdown directly**
    - Type/paste in textarea
    - Content saved to UUID4 file

### File Handling

Like file links, markdown files use:
- UUID4 filenames for security
- Original filename preservation
- Upload metadata tracking

### Rendering Features

Powered by StrapDown.js:
- GitHub-flavored markdown
- Syntax highlighting
- Tables support
- Task lists
- Automatic table of contents

### Example Configuration

```toml
[links.readme]
type = "markdown"
path = "f7e6d5c4-b3a2-9180-fedc-ba9876543210.md"
original_filename = "README.md"
upload_date = "2024-01-15T14:30:00"
```

### Markdown Syntax Examples

#### Headers
```
# Heading 1
## Heading 2
### Heading 3
```

#### Text Formatting
```
**Bold text** and *italic text*
~~Strikethrough text~~
`inline code`
```

#### Lists
```
- Bullet list
- Another item
  - Nested item

1. Numbered list
2. Second item
   1. Nested numbered
```

#### Links and Images
```
[Link text](https://example.com)
![Image alt text](image-url.jpg)
```

#### Code Blocks
Use three backticks followed by the language name:

    ```python
    def hello():
        print("Hello, World!")
    ```

#### Tables
```
| Column 1 | Column 2 |
|----------|----------|
| Data     | Here     |
| More     | Data     |
```

#### Blockquotes
```
> This is a blockquote
> It can span multiple lines
```

### Theme Customization

Markdown can use a different theme than the main UI:

```toml
[app]
theme = "darkly"          # Main UI theme
markdown_theme = "united" # Markdown rendering theme
```

### Use Cases

- **Documentation**: User guides, API docs
- **Announcements**: Formatted notices
- **Knowledge base**: How-to articles
- **Meeting notes**: Shared formatted notes
- **Changelogs**: Version history

### Best Practices

- Preview before saving
- Use consistent formatting
- Include table of contents for long documents
- Test links and images
- Consider mobile rendering

## HTML Links

### What They Do

HTML links render raw HTML content directly in the browser. Perfect for hosting pre-formatted web pages, custom layouts, or content that requires specific styling and interactivity.

### Creating HTML Links

Two methods:

1. **Upload HTML file**
    - Select `.html` or `.htm` file
    - Content stored with UUID4 filename
    - Auto-detected when uploaded to markdown section

2. **Enter HTML directly**
    - Type/paste in textarea
    - Content saved to UUID4 file

### File Handling

Like file and markdown links, HTML files use:
- UUID4 filenames for security
- Original filename preservation
- Upload metadata tracking

### Rendering Features

Raw HTML rendering with full support for:
- Custom CSS styling
- JavaScript functionality
- Embedded media
- Interactive elements
- Complete HTML documents

### Example Configuration

```toml
[links.webpage]
type = "html"
path = "a1b2c3d4-e5f6-7890-abcd-ef1234567890.html"
original_filename = "custom-page.html"
upload_date = "2024-01-15T14:30:00"
```

### HTML Content Examples

#### Basic HTML Page
```html
<!DOCTYPE html>
<html>
<head>
    <title>My Custom Page</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #007bff; color: white; padding: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to My Page</h1>
    </div>
    <p>This is custom HTML content!</p>
</body>
</html>
```

#### Interactive Elements
```html
<button onclick="alert('Hello!')">Click Me</button>
<script>
    console.log('JavaScript is working!');
</script>
```

### Auto-Detection Feature

HTML files are automatically detected when:
- Uploading `.html` or `.htm` files to the markdown section
- File extension is `.html` or `.htm`
- Link type automatically changes from markdown to HTML

### Use Cases

- **Custom web pages**: Landing pages with specific branding
- **Interactive content**: Forms, calculators, demos
- **Portfolio pieces**: Showcase designs or prototypes
- **Presentations**: HTML-based slide shows
- **Widgets**: Embedded tools or utilities
- **Rich media**: Complex layouts with CSS/JS

### Best Practices

- Embed all CSS and Javascript into one HTML file since only a single file is served
- For graphics and other assets, consider hosting these separately using Trunk8 short codes
- Keep file sizes reasonable
- Consider mobile responsiveness

### Security Considerations

- HTML content is rendered as-is
- JavaScript executes in user's browser
- Be cautious with external resources
- Consider Content Security Policy implications

## Security Enhancements

### File Security Features

All uploaded files (file, markdown, and HTML types) benefit from enhanced security:

#### UUID4 Naming
- Files stored with cryptographically secure UUIDs
- Example: `f47ac10b-58cc-4372-a567-0e02b2c3d479.pdf`
- Prevents enumeration attacks

#### Metadata Preservation
- Original filenames preserved for user experience
- Download names match original filenames
- Upload timestamps for audit trails

#### File Validation
- Configurable file type restrictions
- MIME type detection and validation
- File size limits to prevent abuse

### Example Security Flow

1. **Upload**: User uploads `Confidential-Report.pdf`
2. **Processing**: 
    - Generates UUID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf`
    - Stores metadata: original name, size, date, MIME type
    - Validates file type and size
3. **Storage**: File saved with UUID name
4. **Download**: User sees `Confidential-Report.pdf` when downloading
5. **Security**: Actual file path remains hidden

## Choosing the Right Type

### Decision Matrix

| If you need to... | Use this type |
|-------------------|---------------|
| Shorten a URL | Redirect |
| Share a downloadable file | File |
| Display formatted content | Markdown |
| Host custom web pages | HTML |
| Host an image for download | File |
| Create a readable document | Markdown |
| Build interactive content | HTML |
| Forward to external site | Redirect |
| Host with custom styling | HTML |

### Type Comparison

| Feature | Redirect | File | Markdown | HTML |
|---------|----------|------|----------|------|
| Storage needed | Minimal | Variable | Small | Small-Medium |
| Bandwidth usage | None | High | Low | Low-Medium |
| Content editable | URL only | Replace file | Full content | Full content |
| Preview available | No | No | Yes | Yes |
| SEO friendly | No | No | Yes | Yes |
| Security features | None | UUID4, validation | UUID4, validation | UUID4, validation |
| Custom styling | No | No | Limited | Full |
| JavaScript support | No | No | No | Yes |
| Interactive elements | No | No | No | Yes |

## Advanced Features

### Expiration Handling

All link types support expiration:

```toml
[links.temporary]
type = "redirect"
url = "https://example.com"
expiration_date = "2024-06-30T23:59:59"
```

When expired:
- Link returns 404
- Configuration removed
- Files deleted (if applicable)

## File Management

### File Metadata

Enhanced file links store comprehensive metadata:

- **original_filename**: User-friendly name for downloads
- **file_size**: Size in bytes for storage monitoring
- **mime_type**: Detected MIME type for proper serving
- **upload_date**: ISO timestamp for audit trails

## Troubleshooting

### Redirect Issues
- Ensure URL includes protocol
- Check for URL encoding issues
- Verify target site allows hotlinking

### File Problems
- Check disk space
- Verify file permissions
- Confirm upload size limits

### Markdown Rendering
- Validate markdown syntax
- Check for unsupported features
- Test in different browsers

## Next Steps

- [Create your first link](managing-links.md)
- [Customize themes](themes.md)
- [Configure settings](settings.md)
- [Learn about security](../deployment/security.md) 