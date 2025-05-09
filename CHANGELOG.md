# Changelog

## [0.1.0] - 2025-05-09
### Added
- Initial Flask app setup with SQLite databases (`states.db`, `past_results.db`).
- Flask-Admin interface for CRUD operations on database tables.
- Multi-database support with separate sessions.
- Basic home page and database check route.

### Fixed
- Application context issue for `past_results.db` engine initialization.