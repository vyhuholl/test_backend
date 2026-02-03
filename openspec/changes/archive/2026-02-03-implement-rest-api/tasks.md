## 1. Project Setup

- [x] 1.1 Create project directory structure (app/api, app/services, app/models, etc.)
- [x] 1.2 Update pyproject.toml with additional dependencies if needed
- [x] 1.3 Configure ruff and pytest settings in pyproject.toml
- [x] 1.4 Create .env.example file with API_KEY variable

## 2. Database Layer

- [x] 2.1 Create SQLAlchemy base model in app/models/base.py
- [x] 2.2 Create Activity model with self-referential parent relationship
- [x] 2.3 Create Building model with address, latitude, longitude fields
- [x] 2.4 Create Organisation model with name and building relationship
- [x] 2.5 Create OrganisationPhone model for multiple phone numbers
- [x] 2.6 Create OrganisationActivity junction table for M2M relationship
- [x] 2.7 Create database.py with SQLAlchemy engine and session factory
- [x] 2.8 Write tests for all models

## 3. Migrations

- [x] 3.1 Initialize Alembic configuration
- [x] 3.2 Create initial migration for all models
- [x] 3.3 Configure Alembic to use SQLAlchemy 2.0 style
- [x] 3.4 Write tests for migration up/down

## 4. Seed Data

- [x] 4.1 Create seed data script with sample activities (3-level hierarchy)
- [x] 4.2 Create seed data script with sample buildings
- [x] 4.3 Create seed data script with sample organisations
- [x] 4.4 Add seed data to migration or create separate loader

## 5. Service Layer

- [x] 5.1 Create activity_service.py with hierarchy traversal methods
- [x] 5.2 Create building_service.py with CRUD operations
- [x] 5.3 Create organisation_service.py with search and filter methods
- [x] 5.4 Implement Haversine formula for distance calculations
- [x] 5.5 Implement geospatial search (radius and rectangular area)
- [x] 5.6 Implement recursive activity search
- [x] 5.7 Implement name search with partial matching
- [x] 5.8 Write tests for all service methods

## 6. API Layer

- [x] 6.1 Create Pydantic schemas for request/response models
- [x] 6.2 Create dependencies.py with API key authentication
- [x] 6.3 Create organisations.py routes endpoint
- [x] 6.4 Create buildings.py routes endpoint
- [x] 6.5 Create activities.py routes endpoint
- [x] 6.6 Implement GET /organisations/{id} endpoint
- [x] 6.7 Implement GET /organisations/by-building/{building_id} endpoint
- [x] 6.8 Implement GET /organisations/by-activity/{activity_id} endpoint
- [x] 6.9 Implement GET /organisations/search endpoint with geospatial and name filters
- [x] 6.10 Implement GET /buildings endpoint
- [x] 6.11 Implement GET /activities endpoint
- [x] 6.12 Add proper error handling and HTTP status codes
- [x] 6.13 Write tests for all API endpoints

## 7. FastAPI Application

- [x] 7.1 Create main.py with FastAPI app factory
- [x] 7.2 Configure CORS settings
- [x] 7.3 Register all route modules
- [x] 7.4 Add OpenAPI documentation metadata
- [x] 7.5 Create startup and shutdown events for database connection

## 8. Dockerization

- [x] 8.1 Create Dockerfile with multi-stage build
- [x] 8.2 Create .dockerignore file
- [x] 8.3 Create docker-compose.yml (optional, for easy local development)
- [x] 8.4 Test Docker build and run

## 9. Documentation

- [x] 9.1 Update README.md with project description
- [x] 9.2 Add installation instructions (uv setup)
- [x] 9.3 Add running instructions (local and Docker)
- [x] 9.4 Document API endpoints with examples
- [x] 9.5 Document API documentation locations:
    - OpenAPI JSON: /openapi.json
    - Swagger UI: /docs
    - ReDoc: /redoc
- [x] 9.6 Add environment variables documentation

## 10. Quality Assurance

- [x] 10.1 Run ruff linting and fix all issues
- [x] 10.2 Run ruff-format and ensure code is properly formatted
- [x] 10.3 Run pytest and verify 80%+ code coverage
- [x] 10.4 Test API endpoints manually via Swagger UI
- [x] 10.5 Verify Docker container runs correctly
- [x] 10.6 Verify all migrations work correctly

## 11. Final Verification

- [x] 11.1 Verify all requirements from project.md are met
- [x] 11.2 Verify activity hierarchy max 3 levels constraint
- [x] 11.3 Verify API key authentication works
- [x] 11.4 Verify all responses are in JSON format
- [x] 11.5 Verify all code runs via `uv run` command
