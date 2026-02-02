## Context

This is a new REST API implementation for a backend developer test assignment. The API serves as a catalogue for organisations, buildings, and activities with geospatial search capabilities. The project uses Python 3.12+, FastAPI, SQLAlchemy, SQLite, and Alembic for migrations.

### Constraints

- Activity hierarchy limited to maximum 3 nesting levels
- Static API key authentication for all endpoints
- Minimum 80% test coverage required
- All Python code must be executed via `uv run`
- Code must pass ruff linting and formatting checks (79 character line length)
- Test-Driven Development (TDD) approach required

## Goals / Non-Goals

### Goals

- Create a clean, maintainable REST API following Python best practices
- Implement all required endpoints with proper error handling
- Provide comprehensive API documentation via OpenAPI/Swagger/ReDoc
- Ensure containerization via Docker for easy deployment
- Achieve at least 80% code coverage with tests
- Follow TDD principles (write tests before implementation)

### Non-Goals

- User authentication beyond static API key
- Real-time data synchronization
- Caching layer (can be added later if needed)
- Advanced search features beyond geospatial and name matching
- Multi-tenant support

## Decisions

### Database Schema

**Decision**: Use SQLAlchemy ORM with declarative base for all models.

**Rationale**:
- SQLAlchemy is already specified in project dependencies
- ORM provides type safety and easier migrations
- Declarative base is the recommended SQLAlchemy 2.0 pattern

**Models**:
- `Activity`: id, name, parent_id (self-referential for hierarchy)
- `Building`: id, address, latitude, longitude
- `Organisation`: id, name, building_id (FK to Building)
- `OrganisationPhone`: id, organisation_id (FK to Organisation), phone_number
- `OrganisationActivity`: id, organisation_id (FK), activity_id (FK) - M2M junction table

### API Architecture

**Decision**: Layered architecture with API, Service, and Data Access layers.

**Rationale**:
- Separation of concerns improves testability
- Service layer isolates business logic from FastAPI specifics
- Repository pattern for data access abstraction

**Structure**:
```
app/
├── api/
│   ├── __init__.py
│   ├── dependencies.py  # API key auth, DB session
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── organisations.py
│   │   ├── buildings.py
│   │   └── activities.py
│   └── schemas.py  # Pydantic models for request/response
├── services/
│   ├── __init__.py
│   ├── organisation_service.py
│   ├── building_service.py
│   └── activity_service.py
├── models/
│   ├── __init__.py
│   ├── base.py  # SQLAlchemy declarative base
│   ├── activity.py
│   ├── building.py
│   └── organisation.py
├── database.py  # SQLAlchemy engine and session factory
└── main.py  # FastAPI app factory
```

### Geospatial Search

**Decision**: Implement Haversine formula for distance calculations within the service layer.

**Rationale**:
- SQLite doesn't have native spatial functions
- Haversine is simple and sufficient for the use case
- Can be replaced with PostGIS if migrating to PostgreSQL later

**Implementation**:
- Service method to calculate distance between two points
- Query filter for radius search (distance <= radius)
- Query filter for rectangular area (lat/lon bounds)

### Activity Hierarchy

**Decision**: Use adjacency list pattern with self-referential foreign key.

**Rationale**:
- Simple and efficient for shallow hierarchies (max 3 levels)
- Easy to query with recursive CTEs or multiple joins
- No need for nested set or materialized path patterns

**Implementation**:
- `Activity.parent_id` nullable FK to `Activity.id`
- Service method to get all descendants (recursive query)
- Validation to ensure max 3 levels on insert

### Authentication

**Decision**: Static API key via FastAPI dependency.

**Rationale**:
- Specified in project requirements
- Sufficient for a test assignment
- Easy to implement and test

**Implementation**:
- Environment variable `API_KEY`
- Dependency checks `X-API-Key` header
- Returns 401 Unauthorized if missing or invalid

### Dockerization

**Decision**: Multi-stage Dockerfile for production-ready image.

**Rationale**:
- Smaller final image size
- Separates build and runtime dependencies
- Follows Docker best practices

**Implementation**:
- Stage 1: Build stage with uv for dependency resolution
- Stage 2: Runtime stage with minimal Python image
- Expose port 8000
- Use gunicorn for production (or uvicorn for development)

### API Documentation

**Decision**: Use FastAPI's built-in OpenAPI support with Swagger UI and ReDoc.

**Rationale**:
- FastAPI generates OpenAPI schema automatically
- Swagger UI and ReDoc are included by default
- No additional dependencies needed

**Implementation**:
- Document all endpoints with docstrings
- Add response models to route decorators
- Enable interactive documentation at `/docs` (Swagger) and `/redoc` (ReDoc)

### Testing Strategy

**Decision**: pytest with fixtures for database and test client.

**Rationale**:
- pytest is specified in project dependencies
- Fixtures provide reusable test setup
- Supports async testing for FastAPI

**Implementation**:
- Fixture for in-memory SQLite database
- Fixture for FastAPI test client
- Separate test files per module
- Coverage reporting via pytest-cov

## Risks / Trade-offs

### Risks

1. **SQLite limitations**: No native spatial functions, concurrent write limitations
   - **Mitigation**: Use Haversine for distance calculations; SQLite is sufficient for test assignment

2. **Activity hierarchy validation**: Need to ensure max 3 levels
   - **Mitigation**: Add validation in service layer and tests

3. **Geospatial query performance**: Full table scan for radius searches
   - **Mitigation**: Add indexes on lat/lon columns; acceptable for test data size

### Trade-offs

1. **Simplicity vs. Performance**: Using simple patterns instead of optimizations
   - **Rationale**: Test assignment prioritizes clean code over performance

2. **SQLite vs. PostgreSQL**: SQLite chosen for simplicity
   - **Rationale**: No external dependencies required; easier to run in Docker

3. **Static API key vs. OAuth**: Static key chosen for simplicity
   - **Rationale**: Sufficient for test assignment; OAuth would be overkill

## Migration Plan

### Implementation Steps

1. Set up project structure and dependencies
2. Create SQLAlchemy models
3. Configure Alembic for migrations
4. Create initial migration
5. Write tests for models
6. Implement service layer with tests
7. Implement API layer with tests
8. Add seed data
9. Create Dockerfile
10. Update README.md
11. Verify 80%+ code coverage

### Rollback

- Delete all created files
- Restore original README.md
- Remove Dockerfile
- No database rollback needed (fresh implementation)

## Open Questions

- Should the seed data be loaded via Alembic migration or a separate script?
- What should be the default API key value for development?
- Should the Docker image include test data or load it at runtime?
