# test_backend

A Django REST Framework backend service built with constitutional governance principles.

## Project Governance

This project follows a constitutional framework that defines immutable principles for code quality, testing, user experience, and performance. All development must comply with these principles.

📋 **[Read the Constitution](.specify/memory/constitution.md)** (v1.0.0)

### Core Principles

1. **Code Quality Excellence** - PEP 8, type hints, comprehensive documentation, code reviews
2. **Testing Standards & Reliability** - 80%+ coverage, comprehensive automated testing
3. **User Experience Consistency** - Consistent APIs, clear errors, proper status codes
4. **Performance Requirements** - <200ms response times, optimized queries, rate limiting

## Tech Stack

- Python 3.12+
- Django 6.0+
- Django REST Framework 3.16+
- bcrypt (password hashing)
- PyJWT (authentication)

## Development Setup

```bash
# Install dependencies
uv sync

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy .

# Start development server
python manage.py runserver
```

## Project Structure

```
test_backend/
├── .specify/              # Constitutional governance & templates
│   ├── memory/
│   │   └── constitution.md   # Project constitution (v1.0.0)
│   └── templates/         # Specification templates
├── specs/                 # Feature specifications
│   └── 001-custom-auth-system/  # Custom authentication and authorization system
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Authentication and Authorization System

### Overview

This project implements a custom authentication and authorization system with Role-Based Access Control (RBAC). The system manages user identity, session handling, and granular permission-based resource access without relying on framework defaults.

### Key Features

- **User Management**: Registration, login, logout, profile updates, and soft deletion
- **Session Handling**: JWT-based authentication with token expiration and blacklisting
- **Role-Based Access Control**: Flexible permission system with roles, permissions, and resource mappings
- **Security**: bcrypt password hashing, rate limiting, proper HTTP status codes (401/403)

### Access Control Structure

The RBAC system follows a hierarchical model:

```
User → UserRole → Role → AccessRoleRules → BusinessElement
                              ↓
                    [permission flags]
```

#### Database Tables

**users** - User accounts with authentication credentials
- Fields: id, first_name, last_name, middle_name, email, password_hash, is_active, created_at, updated_at, last_login_at
- Soft deletion via `is_active` flag

**roles** - Named roles (admin, manager, user, guest)
- Fields: id, name, description, created_at, updated_at
- Examples: admin, user, moderator, guest

**business_elements** - Application resources/objects to be accessed
- Fields: id, name, description, created_at
- Examples: users, products, shops, orders, documents, projects

**access_roles_rules** - Access control rules mapping roles to elements with granular permissions
- Fields: id, role_id (FK), element_id (FK), and permission flags:
  - `read_permission` - Can view individual resource
  - `read_all_permission` - Can list/view all resources
  - `create_permission` - Can create new resources
  - `update_permission` - Can update own resources
  - `update_all_permission` - Can update any resource
  - `delete_permission` - Can delete own resources
  - `delete_all_permission` - Can delete any resource

**user_roles** - Junction table linking users to roles
- Fields: id, user_id (FK), role_id (FK), assigned_at, assigned_by (FK)

#### Permission Check Flow

1. Request arrives with JWT token
2. System extracts user ID from token
3. System queries user's roles via `user_roles` table
4. System queries `access_roles_rules` filtered by roles and requested business element
5. System checks if any rule grants the required permission flag
6. System grants access (200) or denies (403 Forbidden)

#### HTTP Status Codes

- **401 Unauthorized**: Authentication required or token invalid/expired
- **403 Forbidden**: User authenticated but lacks required permission
- **200 OK**: Request successful with appropriate permissions

#### Example Access Rules

For **documents** business element:

| Role | read_permission | read_all | create | update | update_all | delete | delete_all |
|------|----------------|----------|--------|--------|-----------|--------|-----------|
| admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| moderator | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| user | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| guest | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

#### Default Test Users

The system includes seed data for testing:

```
Admin:     admin@example.com / Admin123
User:      user@example.com / User123
Moderator: moderator@example.com / Mod123
```

#### Security Features

- **Password Hashing**: bcrypt with 12+ salt rounds
- **Token Management**: JWT with 24-hour expiration
- **Rate Limiting**: 5 login attempts per minute per IP
- **Token Blacklist**: Logout invalidates tokens immediately
- **Soft Deletion**: Deactivated users cannot login but data is retained

For detailed API documentation and implementation details, see [specs/001-custom-auth-system/spec.md](specs/001-custom-auth-system/spec.md).

## Contributing

Before contributing, please:

1. Read the [Constitution](.specify/memory/constitution.md) to understand project principles
2. Use the specification templates in `.specify/templates/` for planning
3. Ensure all changes meet constitutional requirements:
   - Include type hints and documentation
   - Write tests with 80%+ coverage
   - Follow API consistency patterns
   - Meet performance targets

## Standards Checklist

Every pull request must:

- [ ] Pass all linting (Ruff/Flake8) and type checking (mypy)
- [ ] Include type hints for all public interfaces
- [ ] Have docstrings for all public APIs
- [ ] Include unit tests (80%+ coverage)
- [ ] Include integration tests for API endpoints
- [ ] Follow consistent JSON response structure
- [ ] Use correct HTTP status codes
- [ ] Optimize database queries (no N+1)
- [ ] Include performance tests for critical paths
- [ ] Have code review approval

## License

[Your License Here]

## Documentation

- [Constitution](.specify/memory/constitution.md) - Project governance principles
- [Planning Template](.specify/templates/plan-template.md) - Technical planning guide
- [Spec Template](.specify/templates/spec-template.md) - Feature specification guide
- [Tasks Template](.specify/templates/tasks-template.md) - Task breakdown guide
