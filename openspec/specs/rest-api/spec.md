# rest-api Specification

## Purpose
TBD - created by archiving change implement-rest-api. Update Purpose after archive.
## Requirements
### Requirement: Database Models

The system SHALL provide SQLAlchemy ORM models for Organisation, Building, and Activity entities with proper relationships and constraints.

#### Scenario: Activity model with hierarchy
- **WHEN** creating an Activity model
- **THEN** it SHALL have id, name, and optional parent_id fields
- **AND** parent_id SHALL be a foreign key referencing Activity.id
- **AND** the hierarchy SHALL support up to 3 nesting levels

#### Scenario: Building model with geospatial data
- **WHEN** creating a Building model
- **THEN** it SHALL have id, address, latitude, and longitude fields
- **AND** latitude SHALL be a decimal between -90 and 90
- **AND** longitude SHALL be a decimal between -180 and 180

#### Scenario: Organisation model with relationships
- **WHEN** creating an Organisation model
- **THEN** it SHALL have id, name, and building_id fields
- **AND** building_id SHALL be a foreign key referencing Building.id
- **AND** it SHALL support multiple phone numbers
- **AND** it SHALL support multiple activities via junction table

### Requirement: Database Migrations

The system SHALL use Alembic for database migrations and provide an initial migration for all models.

#### Scenario: Initial migration creation
- **WHEN** running Alembic initial migration
- **THEN** all tables SHALL be created (activities, buildings, organisations, organisation_phones, organisation_activities)
- **AND** all foreign key constraints SHALL be established
- **AND** migration SHALL be reversible

#### Scenario: Migration execution
- **WHEN** running migration upgrade
- **THEN** database schema SHALL be updated
- **AND** migration history SHALL be recorded
- **AND** migration downgrade SHALL restore previous state

### Requirement: Seed Data

The system SHALL provide seed data for testing including activities (3-level hierarchy), buildings, and organisations.

#### Scenario: Activity seed data
- **WHEN** loading seed data
- **THEN** at least 5 top-level activities SHALL be created
- **AND** some activities SHALL have children (level 2)
- **AND** some level 2 activities SHALL have children (level 3)
- **AND** no activity SHALL exceed 3 nesting levels

#### Scenario: Building seed data
- **WHEN** loading seed data
- **THEN** at least 3 buildings SHALL be created
- **AND** each building SHALL have valid address, latitude, and longitude

#### Scenario: Organisation seed data
- **WHEN** loading seed data
- **THEN** at least 5 organisations SHALL be created
- **AND** each organisation SHALL be associated with a building
- **AND** each organisation SHALL have at least one phone number
- **AND** each organisation SHALL be associated with at least one activity

### Requirement: API Authentication

The system SHALL require static API key authentication for all endpoints.

#### Scenario: Valid API key
- **WHEN** a request includes valid X-API-Key header
- **THEN** the request SHALL be processed
- **AND** the endpoint SHALL return expected response

#### Scenario: Missing API key
- **WHEN** a request lacks X-API-Key header
- **THEN** the endpoint SHALL return 401 Unauthorized
- **AND** the response SHALL indicate authentication required

#### Scenario: Invalid API key
- **WHEN** a request includes invalid X-API-Key header
- **THEN** the endpoint SHALL return 401 Unauthorized
- **AND** the response SHALL indicate invalid credentials

### Requirement: Organisation Endpoints

The system SHALL provide REST API endpoints for retrieving and searching organisations.

#### Scenario: Get organisation by ID
- **WHEN** GET /organisations/{id} is called with valid ID
- **THEN** the endpoint SHALL return organisation details
- **AND** response SHALL include name, building, activities, and phone numbers
- **AND** response SHALL be in JSON format

#### Scenario: List organisations by building
- **WHEN** GET /organisations/by-building/{building_id} is called
- **THEN** the endpoint SHALL return all organisations in that building
- **AND** response SHALL be in JSON format

#### Scenario: List organisations by activity
- **WHEN** GET /organisations/by-activity/{activity_id} is called
- **THEN** the endpoint SHALL return organisations with that activity
- **AND** results SHALL include organisations from child activities (recursive)

#### Scenario: Search organisations by name
- **WHEN** GET /organisations/search?name={query} is called
- **THEN** the endpoint SHALL return organisations with name containing query
- **AND** search SHALL be case-insensitive
- **AND** response SHALL be in JSON format

#### Scenario: Geospatial radius search
- **WHEN** GET /organisations/search?lat={lat}&lon={lon}&radius={km} is called
- **THEN** the endpoint SHALL return organisations within radius kilometers
- **AND** distance SHALL be calculated using Haversine formula
- **AND** response SHALL be in JSON format

#### Scenario: Geospatial rectangular area search
- **WHEN** GET /organisations/search?min_lat={lat}&max_lat={lat}&min_lon={lon}&max_lon={lon} is called
- **THEN** the endpoint SHALL return organisations within the rectangular area
- **AND** response SHALL be in JSON format

### Requirement: Building Endpoints

The system SHALL provide REST API endpoints for retrieving buildings.

#### Scenario: List all buildings
- **WHEN** GET /buildings is called
- **THEN** the endpoint SHALL return all buildings
- **AND** response SHALL include address, latitude, and longitude
- **AND** response SHALL be in JSON format

### Requirement: Activity Endpoints

The system SHALL provide REST API endpoints for retrieving activities.

#### Scenario: List all activities
- **WHEN** GET /activities is called
- **THEN** the endpoint SHALL return all activities
- **AND** response SHALL include activity hierarchy information
- **AND** response SHALL be in JSON format

### Requirement: Dockerization

The system SHALL provide a Dockerfile for containerizing the application.

#### Scenario: Docker build
- **WHEN** building the Docker image
- **THEN** the build SHALL complete successfully
- **AND** the image SHALL include all dependencies
- **AND** the image SHALL expose port 8000

#### Scenario: Docker run
- **WHEN** running the Docker container
- **THEN** the FastAPI application SHALL start
- **AND** the API SHALL be accessible on port 8000
- **AND** the database SHALL be initialized with seed data

### Requirement: Documentation

The system SHALL provide comprehensive documentation in README.md including project description, Docker instructions, and API documentation locations.

#### Scenario: README project description
- **WHEN** reading README.md
- **THEN** it SHALL describe the project purpose
- **AND** it SHALL list the tech stack
- **AND** it SHALL explain the domain entities

#### Scenario: README Docker instructions
- **WHEN** reading README.md
- **THEN** it SHALL include Docker build command
- **AND** it SHALL include Docker run command
- **AND** it SHALL explain how to access the API in container

#### Scenario: README API documentation locations
- **WHEN** reading README.md
- **THEN** it SHALL document OpenAPI JSON endpoint (/openapi.json)
- **AND** it SHALL document Swagger UI endpoint (/docs)
- **AND** it SHALL document ReDoc endpoint (/redoc)

### Requirement: Code Quality

The system SHALL maintain code quality through linting, formatting, and testing.

#### Scenario: Ruff linting
- **WHEN** running ruff check
- **THEN** no linting errors SHALL be present
- **AND** code SHALL follow PEP-8 standards

#### Scenario: Ruff formatting
- **WHEN** running ruff-format
- **THEN** all code SHALL be formatted with 79 character line length
- **AND** formatting SHALL be consistent across all files

#### Scenario: Test coverage
- **WHEN** running pytest with coverage
- **THEN** coverage SHALL be at least 80%
- **AND** all business logic SHALL be tested
- **AND** all API endpoints SHALL be tested

### Requirement: Response Format

The system SHALL return all API responses in JSON format.

#### Scenario: Successful response
- **WHEN** an API request succeeds
- **THEN** response Content-Type SHALL be application/json
- **AND** response body SHALL be valid JSON

#### Scenario: Error response
- **WHEN** an API request fails
- **THEN** response Content-Type SHALL be application/json
- **AND** response body SHALL include error details

