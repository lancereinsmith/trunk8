# Changelog

All notable changes to Trunk8 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-01-21

### Added

- **Raw HTML Hosting**: New link type for hosting custom HTML pages with full CSS, JavaScript, and interactive element support
  - Upload `.html` or `.htm` files directly or paste HTML content using built-in editor
  - Auto-detection: HTML files uploaded to markdown section are automatically converted to HTML links
  - Complete HTML document support with embedded CSS, JavaScript, and interactive elements
  - Full feature parity with existing link types (expiration dates, user permissions, admin management)
  - UUID4 filename generation for security with original filename preservation
  - New `html_render.html` template for optimal HTML content display
- **Enhanced Form Handling**: Updated add/edit forms with HTML-specific input options and validation
- **Comprehensive Test Suite**: 346+ new lines of tests covering all HTML functionality including edge cases
  - Tests for JavaScript, CSS, special characters, and Unicode content
  - Integration testing for full lifecycle from creation to deletion
  - Complete Link model support for HTML link types
- **Documentation Expansion**: Complete coverage of HTML link functionality
  - Updated API documentation with HTML link endpoints
  - User guide expansion with detailed examples and best practices
  - Ready-to-use HTML templates and code snippets

### Changed

- **Expanded Link Type Support**: Added HTML to existing file, redirect, and markdown link types
- **Enhanced Link Management**: HTML links display with proper metadata and type indicators
- **Improved Edit Experience**: Seamless switching between file and text input methods for HTML links
- **Form UI/UX**: Cleaner form layouts with better error messaging and real-time validation

### Security

- **File Security**: HTML files stored with secure UUID4 filenames preventing enumeration attacks
- **Access Control**: HTML links maintain user-level permissions and admin oversight
- **File Cleanup**: Automatic deletion of HTML files when links are removed
- **Metadata Preservation**: Original filenames and upload information safely stored

### Technical

- **No Breaking Changes**: All existing links, files, and configurations remain unchanged
- **Backward Compatibility**: All previous functionality preserved
- **Performance**: No impact on existing link types or system performance
- **Backup Compatibility**: HTML links fully supported in backup/restore operations

## [0.5.0] - 2025-06-23

### Added

- **Configurable File Upload Size Limits**: New `max_file_size_mb` configuration option in `config/config.toml` to set maximum file upload sizes (defaults to 100MB)
- **Enhanced File Upload Security**: Implemented UUID4 naming for uploaded files to prevent enumeration attacks while preserving original filenames in metadata
- **Comprehensive File Metadata Tracking**: Added tracking for file size, MIME type, upload date, and other metadata for better file management
- **Per-User Theme Configuration**: Users can now set individual theme preferences that override admin defaults through user-specific config files
- **Port Configuration**: Added `TRUNK8_PORT` environment variable to customize Flask development server port (defaults to 5001)
- **Bootstrap Icons Integration**: Replaced emoji icons with Bootstrap icons for a more consistent and modern UI
- **Backup and Restore Functionality**: Complete backup and restore system for user data, configurations, and links
- **Enhanced Documentation Structure**: Comprehensive API documentation, improved navigation, and better cross-referencing

### Changed

- **File Upload Handling**: Enhanced validation for allowed file types and sizes with improved error messages
- **UI/UX Improvements**: Updated templates with Bootstrap icons and improved visual consistency
- **Documentation Organization**: Restructured documentation with better navigation and enhanced GitHub Pages setup
- **Configuration Management**: Improved theme hierarchy allowing user-specific overrides of admin settings
- **Security Enhancements**: Better file handling security and metadata preservation

### Fixed

- **Documentation Accuracy**: Synchronized all documentation with actual codebase implementation
- **Navigation Structure**: Fixed missing navigation items and improved accessibility
- **File Handling**: Enhanced error handling for file uploads and size limit validation
- **Configuration Loading**: Improved robustness of configuration file handling

### Removed

- **Legacy Data Migration**: Removed outdated legacy support code and related migration functionality
- **Deprecated Features**: Cleaned up unused code and improved codebase maintainability

## [0.4.0] - 2025-06-22

### Added

- **Enhanced Documentation Structure**: Added comprehensive user configuration documentation
- **Improved Navigation**: Added user-config.md to documentation navigation for better accessibility
- **Documentation Review and Accuracy Updates**: Synchronized documentation with actual codebase implementation

### Changed

- **Documentation Organization**: Improved cross-referencing and navigation structure
- **Version Synchronization**: Updated changelog to reflect current version status

### Fixed

- **Missing Navigation Items**: Added previously orphaned documentation files to navigation
- **Version Consistency**: Aligned changelog with pyproject.toml version information

## [0.3.0] - 2025-06-21

### Added

- **Cascading User Deletion**: When a user is deleted, all of their links, assets, and files are now automatically cleaned up
  - Complete removal of user directory structure
  - Deletion of all user links (redirect, file, and markdown types)
  - Cleanup of all uploaded files and assets
  - Detailed logging of cleanup statistics
  - Preview functionality to see what will be deleted before confirming
  - Robust error handling for permission issues and corrupted data
- **Enhanced Route Protection**: Link creation now validates against all built-in routes to prevent conflicts
  - Protection for main routes (`/settings`, `/users`, `/profile`)
  - Protection for link management routes (`/add`, `/links`, `/edit_link`, `/delete_link`)
  - Protection for authentication routes (`/auth/*`, `/login`, `/logout`, `/register`)
  - Protection for system routes and common files (`/static`, `/api`, `favicon.ico`, `robots.txt`)
  - Clear error messages when attempting to use reserved short codes
- Optional dependency groups in `pyproject.toml` for better dependency management
- Separate dependency groups for testing (`test`), documentation (`docs`), and development (`dev`)

### Changed

- **BREAKING**: Refactored dependency structure in `pyproject.toml`
  - Moved pytest dependencies to optional `test` group
  - Moved mkdocs dependencies to optional `docs` group
  - Created convenience `dev` group that includes both test and docs dependencies
  - Runtime dependencies now only include core Flask application requirements
- Updated all documentation to reflect new dependency installation methods
- Installation commands now support `uv sync --group dev` and `pip install .[dev]` for development
- Improved error handling for configuration loading
- Enhanced security documentation
- Migrated to blueprint-based architecture
- Improved file upload security
- Enhanced UI with Bootstrap themes

### Fixed

- Link expiration check on every request
- File cleanup for expired links
- File naming collisions
- Configuration file creation on first run

## [0.2.0] - 2025-06-20

### Added

- Comprehensive documentation using MkDocs
- Unit tests for core functionality
- Docker deployment with uv package manager

### Changed

- Migrated to blueprint-based architecture
- Improved file upload security
- Enhanced UI with Bootstrap themes

### Fixed

- File naming collisions
- Configuration file creation on first run

## [0.1.0] - 2025-06-15

### Added

- Initial release
- Basic link shortening functionality
- File upload support
- TOML-based configuration
- Password protection for admin functions
- Link expiration functionality
- Theme customization via web interface
- Markdown rendering with StrapDown.js
- Session-based authentication
- Automatic configuration reloading
