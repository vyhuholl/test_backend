## 1. Project Setup

- [ ] 1.1 Create project directory structure (app/api, app/services, app/models, etc.)
- [ ] 1.2 Update pyproject.toml with additional dependencies if needed
- [ ] 1.3 Configure ruff and pytest settings in pyproject.toml
- [ ] 1.4 Create .env.example file with API_KEY variable

## 2. Database Layer

- [ ] 2.1 Create SQLAlchemy base model in app/models/base.py
- [ ] 2.2 Create Activity model with self-referential parent relationship
- [ ] 2.3 Create Building model with address, latitude, longitude fields
- [ ] 2.4 Create Organisation model with name and building relationship
- [ ] 2.5 Create OrganisationPhone model for multiple phone numbers
- [ ] 2.6 Create OrganisationActivity junction table for M2M relationship
- [ ] 2.7 Create database.py with SQLAlchemy engine and session factory
- [ ] 2.8 Write tests for all models

## 3. Migrations

- [ ] 3.1 Initialize Alembic configuration
- [ ] 3.2 Create initial migration for all models
- [ ] 3.3 Configure Alembic to use SQLAlchemy 2.0 style
- [ ] 3.4 Write tests for migration up/down

## 4. Seed Data

- [ ] 4.1 Create seed data script with sample activities (3-level hierarchy)
- [ ] 4.2 Create seed data script with sample buildings
- [ ] 4.3 Create seed data script with sample organisations
- [ ] 4.4 Add seed data to migration or create separate loader

## 5. Service Layer

- [ ] 5.1 Create activity_service.py with hierarchy traversal methods
- [ ] 5.2 Create building_service.py with CRUD operations
- [ ] 5.3 Create organisation_service.py with search and filter methods
- [ ] 5.4 Implement Haversine formula for distance calculations
- [ ] 5.5 Implement geospatial search (radius and rectangular area)
- [ ] 5.6 Implement recursive activity search
- [ ] 5.7 Implement name search with partial matching
- [ ] 5.8 Write tests for all service methods

## 6. API Layer

- [ ] 6.1 Create Pydantic schemas for request/response models
- [ ] 6.2 Create dependencies.py with API key authentication
- [ ] 6.3 Create organisations.py routes endpoint
- [ ] 6.4 Create buildings.py routes endpoint
- [ ] 6.5 Create activities.py routes endpoint
- [ ] 6.6 Implement GET /organisations/{id} endpoint
- [ ] 6.7 Implement GET /organisations/by-building/{building_id} endpoint
- [ ] 6.8 Implement GET /organisations/by-activity/{activity_id} endpoint
- [ ] 6.9 Implement GET /organisations/search endpoint with geospatial and name filters
- [ ] 6.10 Implement GET /buildings endpoint
- [ ] 6.11 Implement GET /activities endpoint
- [ ] 6.12 Add proper error handling and HTTP status codes
- [ ] 6.13 Write tests for all API endpoints

## 7. FastAPI Application

- [ ] 7.1 Create main.py with FastAPI app factory
- [ ] 7.2 Configure CORS settings
- [ ] 7.3 Register all route modules
- [ ] 7.4 Add OpenAPI documentation metadata
- [ ] 7.5 Create startup and shutdown events for database connection

## 8. Dockerization

- [ ] 8.1 Create Dockerfile with multi-stage build
- [ ] 8.2 Create .dockerignore file
- [ ] 8.3 Create docker-compose.yml (optional, for easy local development)
- [ ] 8.4 Test Docker build and run

## 9. Documentation

- [ ] 9.1 Update README.md with project description
- [ ] 9.2 Add installation instructions (uv setup)
- [ ] 9.3 Add running instructions (local and Docker)
- [ ] 9.4 Document API endpoints with examples
- [ ] 9.5 Document API documentation locations:
    - OpenAPI JSON: /openapi.json
    - Swagger UI: /docs
    - ReDoc: /redoc
- [ ] 9.6 Add environment variables documentation

## 10. Quality Assurance

- [ ] 10.1 Run ruff linting and fix all issues
- [ ] 10.2 Run ruff-format and ensure code is properly formatted
- [ ] 10.3 Run pytest and verify 80%+ code coverage
- [ ] 10.4 Test API endpoints manually via Swagger UI
- [ ] 10.5 Verify Docker container runs correctly
- [ ] 10.6 Verify all migrations work correctly

## 11. Final Verification

- [ ] 11.1 Verify all requirements from project.md are met
- [ ] 11.2 Verify activity hierarchy max 3 levels constraint
- [ ] 11.3 Verify API key authentication works
- [ ] 11.4 Verify all responses are in JSON format
- [ ] 11.5 Verify all code runs via `uv run` command
