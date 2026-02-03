# Change: Implement REST API for Organisations, Buildings, Activities Catalogue

## Why

The project requires a complete REST API implementation to serve as a backend test assignment. This API will provide a comprehensive directory system for organisations, buildings, and activities with geospatial search capabilities, demonstrating clean code practices, proper testing, and adherence to Python conventions.

## What Changes

- **Database Structure**: Create SQLAlchemy models for Organisation, Building, and Activity entities with proper relationships
- **Migrations**: Set up Alembic for database migrations and create initial migration
- **Test Data**: Add seed data for testing organisations, buildings, and activities
- **API Endpoints**: Implement FastAPI endpoints for:
  - List organisations by building
  - List organisations by activity (recursive)
  - Geospatial search (radius and rectangular area)
  - List all buildings
  - Get organisation by ID
  - Search organisations by name (partial match)
- **Dockerization**: Create Dockerfile for containerizing the application
- **Documentation**: Update README.md with project description, Docker instructions, and API documentation locations (OpenAPI, Swagger, ReDoc)

## Impact

- **Affected specs**: New `rest-api` capability
- **Affected code**:
  - New database models in `app/models/`
  - New API routes in `app/api/`
  - New service layer in `app/services/`
  - Alembic migrations in `alembic/versions/`
  - Dockerfile in project root
  - README.md documentation updates
- **Breaking changes**: None (new implementation)
