# Changelog

All notable changes to Trunk8 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Installation commands now support `uv sync --extra dev` and `pip install .[dev]` for development
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