# Quickstart Guide: Custom Authentication & Authorization System

**Version:** 1.0.0  
**Last Updated:** 2026-01-08

## Overview

This guide will help you get the custom authentication and authorization system up and running in under 15 minutes. You'll be able to:

- ✅ Register and authenticate users
- ✅ Test role-based access control (RBAC)
- ✅ Explore the API with pre-seeded data
- ✅ Understand the RBAC structure

---

## Prerequisites

- Python 3.12+
- uv package manager installed
- SQLite (included with Python)
- Git (for cloning the repository)

---

## Quick Setup (5 minutes)

### 1. Clone and Navigate to Project

```bash
cd /path/to/test_backend
```

### 2. Verify Dependencies

Check that all dependencies are in `pyproject.toml`:

```bash
cat pyproject.toml
```

You should see:
- `django>=6.0.1`
- `djangorestframework>=3.16.1`
- `pyjwt>=2.10.1`
- `bcrypt>=5.0.0`

### 3. Initialize Django Project (First Time Only)

```bash
# Create Django project structure
uv run django-admin startproject config .

# Create apps
uv run python manage.py startapp authentication
uv run python manage.py startapp authorization
uv run python manage.py startapp resources
uv run python manage.py startapp core
```

### 4. Run Database Migrations

```bash
# Create database and apply migrations
uv run python manage.py migrate

# Apply custom auth/authz migrations (when implemented)
uv run python manage.py makemigrations authentication
uv run python manage.py makemigrations authorization
uv run python manage.py migrate
```

### 5. Load Seed Data

```bash
# Create test users, roles, and permissions
uv run python manage.py loaddata seed_data
```

This creates:
- **Admin User:** `admin@example.com` / `Admin123`
- **Regular User:** `user@example.com` / `User123`
- **Moderator:** `moderator@example.com` / `Mod123`
- Default roles: admin, user, moderator, guest
- Default business elements: users, documents, projects, orders, shops, products
- Pre-configured access rules

### 6. Start Development Server

```bash
uv run python manage.py runserver
```

Server will start at `http://localhost:8000`

---

## Testing the API (10 minutes)

### 1. Register a New User

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ivan",
    "last_name": "Petrov",
    "middle_name": "Sergeevich",
    "email": "ivan.petrov@example.com",
    "password": "SecurePass123",
    "password_confirmation": "SecurePass123"
  }'
```

**Expected Response (201 Created):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "middle_name": "Sergeevich",
    "email": "ivan.petrov@example.com",
    "is_active": true,
    "roles": ["user"],
    "created_at": "2026-01-08T12:00:00Z"
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

### 2. Login and Get JWT Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan.petrov@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "first_name": "Ivan",
      "last_name": "Petrov",
      "email": "ivan.petrov@example.com",
      "roles": ["user"]
    }
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Save the token for subsequent requests:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. Get User Profile

**Request:**
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "middle_name": "Sergeevich",
    "email": "ivan.petrov@example.com",
    "is_active": true,
    "roles": ["user"],
    "created_at": "2026-01-08T12:00:00Z",
    "updated_at": "2026-01-08T12:00:00Z",
    "last_login_at": "2026-01-08T12:01:00Z"
  },
  "meta": {
    "timestamp": "2026-01-08T12:01:00Z"
  }
}
```

### 4. Update Profile

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ivan",
    "last_name": "Ivanov"
  }'
```

### 5. Test RBAC: Access Documents (Regular User)

**Request:**
```bash
curl -X GET http://localhost:8000/api/resources/documents \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "doc-1",
      "title": "Project Requirements",
      "author": "Admin User",
      "created_at": "2026-01-01T10:00:00Z"
    },
    {
      "id": "doc-2",
      "title": "Technical Specification",
      "author": "Tech Lead",
      "created_at": "2026-01-05T14:30:00Z"
    }
  ],
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 2
  }
}
```

✅ **Success!** Regular users have `read_all_permission` on documents.

### 6. Test RBAC: Try to Access Admin Endpoint (Should Fail)

**Request:**
```bash
curl -X GET http://localhost:8000/api/admin/roles \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": []
  }
}
```

❌ **Expected Failure!** Regular users don't have admin permissions.

### 7. Login as Admin

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123"
  }'
```

**Save admin token:**
```bash
export ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 8. Access Admin Endpoint with Admin Token

**Request:**
```bash
curl -X GET http://localhost:8000/api/admin/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "name": "admin",
      "description": "System administrator with full access to all resources"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "name": "user",
      "description": "Standard user with basic read access"
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "name": "moderator",
      "description": "Content moderator with read and write access"
    }
  ],
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 3
  }
}
```

✅ **Success!** Admin users can access admin endpoints.

### 9. Assign Moderator Role to User

**Request:**
```bash
# Get the user ID and moderator role ID from previous responses
curl -X POST http://localhost:8000/api/admin/users/550e8400-e29b-41d4-a716-446655440000/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "990e8400-e29b-41d4-a716-446655440000"
  }'
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "roles": [
      {"id": "880e8400-e29b-41d4-a716-446655440000", "name": "user"},
      {"id": "990e8400-e29b-41d4-a716-446655440000", "name": "moderator"}
    ]
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

Now the user has both "user" and "moderator" roles!

### 10. Test Logout

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "data": {
    "message": "Successfully logged out"
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Verify token is blacklisted:**
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

✅ **Success!** Token is invalidated after logout.

---

## Understanding RBAC Structure

### Default Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **admin** | System administrator | All permissions on all elements |
| **user** | Standard user | Read-only on documents, projects |
| **moderator** | Content moderator | Read/write on documents, projects |
| **guest** | Limited guest | Read-only on public documents |

### Business Elements (Resources)

- `users` - User accounts
- `documents` - Document resources
- `projects` - Project resources
- `orders` - Order records
- `shops` - Shop listings
- `products` - Product catalog

### Permission Flags

Each role-element combination has these permission flags:

| Flag | Description | Example |
|------|-------------|---------|
| `read_permission` | View individual item | GET /api/resources/documents/123 |
| `read_all_permission` | List/view all items | GET /api/resources/documents |
| `create_permission` | Create new items | POST /api/resources/documents |
| `update_permission` | Update own items | PATCH /api/resources/documents/123 (own) |
| `update_all_permission` | Update any item | PATCH /api/resources/documents/* (any) |
| `delete_permission` | Delete own items | DELETE /api/resources/documents/123 (own) |
| `delete_all_permission` | Delete any item | DELETE /api/resources/documents/* (any) |

### Permission Check Flow

```
Request → Authenticate JWT Token → Load User's Roles → Load Role Permissions → Check Required Permission → Grant or Deny
```

---

## Pre-Seeded Test Accounts

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| admin@example.com | Admin123 | admin | Full system access |
| user@example.com | User123 | user | Read-only access |
| moderator@example.com | Mod123 | moderator | Read/write access |

---

## API Documentation

### Interactive API Docs

Visit these URLs after starting the server:

- **Swagger UI:** `http://localhost:8000/api/docs/swagger/`
- **ReDoc:** `http://localhost:8000/api/docs/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/docs/openapi.json`

### Key Endpoints Summary

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout and blacklist token
- `GET /api/auth/profile` - Get current user profile
- `PATCH /api/auth/profile` - Update profile
- `DELETE /api/auth/profile` - Soft delete account

#### Admin (requires admin role)
- `GET /api/admin/roles` - List roles
- `POST /api/admin/roles` - Create role
- `GET /api/admin/business-elements` - List business elements
- `GET /api/admin/access-rules` - List access rules
- `POST /api/admin/access-rules` - Create access rule
- `POST /api/admin/users/{id}/roles` - Assign role to user

#### Resources (permission-based)
- `GET /api/resources/documents` - List documents
- `POST /api/resources/documents` - Create document
- `GET /api/resources/projects` - List projects

---

## Common Tasks

### View Current User's Permissions

```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

Check the `roles` array in the response.

### Create New Access Rule

```bash
curl -X POST http://localhost:8000/api/admin/access-rules \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "880e8400-e29b-41d4-a716-446655440000",
    "element_id": "aa0e8400-e29b-41d4-a716-446655440000",
    "read_permission": true,
    "read_all_permission": true,
    "create_permission": false,
    "update_permission": false,
    "delete_permission": false
  }'
```

### Soft Delete Account

```bash
curl -X DELETE http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

This sets `is_active=False` and prevents future logins while retaining data.

---

## Testing

### Run All Tests

```bash
uv run python manage.py test
```

### Run Authentication Tests Only

```bash
uv run python manage.py test authentication
```

### Run Authorization Tests Only

```bash
uv run python manage.py test authorization
```

### Run with Coverage

```bash
uv run pytest --cov=. --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

---

## Troubleshooting

### Issue: "Authentication token is invalid"

**Solution:** Token may have expired (24-hour lifetime) or been blacklisted. Login again to get a fresh token.

### Issue: "403 Forbidden" on endpoint

**Solution:** Your role doesn't have the required permission. Check your roles with `GET /api/auth/profile`.

### Issue: "Rate limit exceeded"

**Solution:** You've made too many requests. Wait 60 seconds and try again.

### Issue: Database migrations fail

**Solution:**
```bash
# Delete database and start fresh
rm db.sqlite3
uv run python manage.py migrate
uv run python manage.py loaddata seed_data
```

### Issue: Import errors for custom apps

**Solution:** Make sure apps are added to `INSTALLED_APPS` in `config/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'authentication',
    'authorization',
    'resources',
    'core',
]
```

---

## Next Steps

1. **Explore the API:** Try all endpoints with different roles
2. **Read the Spec:** See `spec.md` for complete requirements
3. **Review Data Model:** See `data-model.md` for entity details
4. **Check API Contracts:** See `contracts/openapi.yaml` for full API schema
5. **Implement Features:** Follow `plan.md` for implementation guidance

---

## Development Workflow

### 1. Make Changes

Edit files in `authentication/`, `authorization/`, `resources/`, or `core/` apps.

### 2. Create Migrations

```bash
uv run python manage.py makemigrations
```

### 3. Apply Migrations

```bash
uv run python manage.py migrate
```

### 4. Run Tests

```bash
uv run python manage.py test
```

### 5. Lint Code

```bash
uv run ruff check .
uv run mypy .
```

### 6. Format Code

```bash
uv run ruff format .
```

---

## Security Reminders

- ✅ Never commit JWT secret keys to version control
- ✅ Use HTTPS in production
- ✅ Rotate JWT secrets periodically
- ✅ Monitor failed login attempts
- ✅ Keep dependencies updated
- ✅ Run security audits before production deployment

---

## Support & Resources

- **Spec Document:** `specs/001-custom-auth-system/spec.md`
- **Implementation Plan:** `specs/001-custom-auth-system/plan.md`
- **Data Model:** `specs/001-custom-auth-system/data-model.md`
- **API Contracts:** `specs/001-custom-auth-system/contracts/openapi.yaml`
- **Research Decisions:** `specs/001-custom-auth-system/research.md`

---

**Happy coding! 🚀**
