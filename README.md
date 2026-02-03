# Organisations REST API

A REST API for organisations, buildings, and activities catalogue with geospatial search capabilities.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0
- Alembic
- SQLite
- Pydantic
- uv (package manager)

## Domain Entities

### Activities
Hierarchical activities catalogue with up to 3 nesting levels. Examples:
- Healthcare (Level 1)
  - Hospitals (Level 2)
    - Clinics (Level 3)
- Education (Level 1)
  - Schools (Level 2)
    - Universities (Level 3)
- Retail (Level 1)
  - Supermarkets (Level 2)
- Technology (Level 1)
  - Software (Level 2)
    - Startups (Level 3)
- Finance (Level 1)
  - Banks (Level 2)
    - Insurance (Level 3)

### Buildings
Physical locations with addresses and geospatial coordinates.

### Organisations
Organisations located in buildings, with multiple phone numbers and associated activities.

## Installation

### Prerequisites
- Python 3.12 or higher
- uv package manager

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd test_backend
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set your API key
   ```

## Running the Application

### Local Development
1. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

2. Seed the database:
   ```bash
   uv run python scripts/seed_data.py
   ```

3. Start the FastAPI server:
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker

#### Build the Docker image:
```bash
docker build -t organisations-api .
```

#### Run the Docker container:
```bash
docker run -p 8000:8000 -e DATABASE_URL="sqlite+aiosqlite:///./organisations.db" -e API_KEY="your-api-key" organisations-api
```

## API Documentation

The API provides interactive documentation at the following endpoints:

- **OpenAPI JSON**: /openapi.json
- **Swagger UI**: /docs
- **ReDoc**: /redoc

## API Endpoints

### Organisations
- `GET /organisations/{id}` - Get organisation by ID
- `GET /organisations/by-building/{building_id}` - List organisations by building
- `GET /organisations/by-activity/{activity_id}` - List organisations by activity (includes descendants)
- `GET /organisations/search` - Search organisations by name and/or geospatial criteria

### Buildings
- `GET /buildings` - List all buildings

### Activities
- `GET /activities` - List all activities (flat list)
- `GET /activities/tree` - Get activities as hierarchical tree

## Authentication

All API endpoints require an `X-API-Key` header. Set the API key in the `.env` file or pass it as an environment variable.

Example request:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/organisations
```

## Search Examples

### Search by name:
```bash
curl -H "X-API-Key: your-api-key" "http://localhost:8000/organisations/search?name=Tech"
```

### Geospatial radius search:
```bash
curl -H "X-API-Key: your-api-key" "http://localhost:8000/organisations/search?lat=55.7558&lon=37.6173&radius=10"
```

### Geospatial area search:
```bash
curl -H "X-API-Key: your-api-key" "http://localhost:8000/organisations/search?min_lat=55.0&max_lat=56.0&min_lon=37.0&max_lon=38.0"
```

## Development

### Code Quality
Run linting and formatting:
```bash
uv run ruff check .
uv run ruff format .
```

### Testing
Run tests with coverage:
```bash
uv run pytest --cov=app --cov-report=html
```

## License

This project is a test assignment for backend developer position.
