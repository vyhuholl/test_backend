# Project Context

## Purpose

This is a REST API for the "Organisations, Buildings, Activities" catalogue. The API provides a comprehensive directory system that allows users to:

- Browse and search organisations by various criteria
- View organisation details including contact information and activities
- Filter organisations by building or activity type
- Perform geospatial searches to find organisations within a specific radius or rectangular area
- Navigate a hierarchical activity classification system (up to 3 levels deep)

The API serves as a backend test assignment for a backend developer position, demonstrating clean code practices, proper testing, and adherence to Python conventions.

## Tech Stack

- **Python**: >=3.12
- **Web Framework**: FastAPI (>=0.128.0)
- **Data Validation**: Pydantic (>=2.12.5)
- **Database**: SQLite
- **ORM**: SQLAlchemy (>=2.0.46)
- **Migrations**: Alembic (>=1.18.3)
- **Testing**: pytest (>=9.0.2), pytest-cov (>=7.0.0)
- **Code Quality**: ruff (>=0.14.14), ruff-format
- **Package Management**: uv

## Project Conventions

### Code Style

- Adhere to PEP-8 standards
- Write clean and readable code
- Use ruff for linting
- Use ruff-format for code formatting with line length of 79 characters
- All Python code must be run via `uv run` command
- Tests must be written before implementation (TDD approach)
- Aim for at least 80% code coverage

### Architecture Patterns

- **Standard CRUD API patterns** for all endpoints
- **Simple service layer** pattern for business logic separation
- **Repository pattern** may be used for data access abstraction
- **Dependency injection** via FastAPI's dependency system
- **Layered architecture**:
  - API layer (FastAPI routes/endpoints)
  - Service layer (business logic)
  - Data access layer (SQLAlchemy models)

### Testing Strategy

- Write tests first (Test-Driven Development)
- Use pytest as the testing framework
- Use pytest-cov for code coverage reporting
- Target minimum 80% code coverage
- Test all business logic, edge cases, and API endpoints
- Mock external dependencies where appropriate

### Git Workflow

- Use **conventional commits** format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `test:` for test-related changes
  - `refactor:` for code refactoring
  - `chore:` for maintenance tasks

### API Authentication

- Static API key authentication for all endpoints
- All responses must be in JSON format

## Domain Context

### Entities

#### Organisation
Represents an organization card in the catalogue with the following attributes:

- **name**: Organization name (e.g., "ООО Рога и Копыта")
- **phone_numbers**: Multiple phone numbers (e.g., "2-222-222", "3-333-333", "8-923-666-13-13")
- **building**: One-to-many relationship - an organization is located in exactly one building
- **activities**: Many-to-many relationship - an organization can engage in multiple activities

#### Building
Contains information about a specific building with the following attributes:

- **address**: Full address (e.g., "г. Москва, ул. Ленина 1, офис 3")
- **latitude**: Geographic coordinate (latitude)
- **longitude**: Geographic coordinate (longitude)

#### Activity
Classifies organization activities in a hierarchical structure:

- **name**: Activity name
- **parent**: Optional parent activity for hierarchical structure
- **Maximum nesting level**: 3 levels deep

Example activity tree:
```
- Еда
  - Мясная продукция
  - Молочная продукция
- Автомобили
  - Грузовые
  - Легковые
    - Запчасти
    - Аксессуары
```

### API Endpoints

1. **List organisations by building** - Get all organisations in a specific building
2. **List organisations by activity** - Get all organisations related to a specific activity
3. **Geospatial search** - Find organisations within a given radius or rectangular area from a point
4. **List buildings** - Get all buildings
5. **Get organisation by ID** - Retrieve detailed information about a specific organisation
6. **Search by activity (recursive)** - Search organisations by activity, including all child activities in the hierarchy
7. **Search by name** - Find organisations by name (partial match)

## Important Constraints

- Activity hierarchy limited to maximum 3 nesting levels
- All API responses must be in JSON format
- Static API key authentication required for all endpoints
- Minimum 80% test coverage required
- All Python code must be executed via `uv run`
- Code must pass ruff linting and formatting checks

## External Dependencies

None currently. The project uses a local SQLite database and does not integrate with external services or APIs.
