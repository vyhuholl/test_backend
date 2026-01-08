# Technical Plan: Custom Authentication and Authorization System

**Date:** 2026-01-08  
**Author:** AI Agent  
**Status:** Approved

## Overview

This plan outlines the implementation of a custom authentication and authorization system for the test_backend Django application. The system provides user management (registration, login, profile management, soft deletion), JWT-based stateless authentication, and role-based access control (RBAC) with granular permissions on business resources. The implementation uses Django 6.0+, Django REST Framework 3.16+, PyJWT 2.10+, and bcrypt 5.0+ with SQLite as the database.

## Constitution Check

This plan has been validated against the project constitution (v1.0.0). Compliance with core principles:

- **Code Quality Excellence:** All code will include type hints, comprehensive docstrings (Google style), pass Ruff/mypy checks with zero errors, maintain cyclomatic complexity below 10, and undergo mandatory code review before merge.

- **Testing Standards & Reliability:** Minimum 80% code coverage overall, 95% for authentication and authorization logic. All API endpoints include integration tests, performance benchmarks, and security tests. Test fixtures used throughout.

- **User Experience Consistency:** Standardized JSON response format (data/error/meta pattern), semantically correct HTTP status codes (401 for auth failures, 403 for authorization failures), clear actionable error messages, complete OpenAPI documentation.

- **Performance Requirements:** API endpoints respond within 200ms (95th percentile), database queries optimized with select_related/prefetch_related to prevent N+1 queries, appropriate indexes on all foreign keys and frequently queried fields, rate limiting on authentication endpoints (5 failed login attempts per minute per IP).

## Architecture

### System Components

**New Django Apps:**

1. **`authentication/`** - User registration, login, logout, profile management, JWT token generation/validation, password hashing
2. **`authorization/`** - RBAC implementation, role management, permission checking, business element management
3. **`resources/`** - Mock business resources (documents, projects) demonstrating permission-based access control
4. **`core/`** - Shared utilities (custom exception handlers, response wrappers, authentication backends, permission classes)

**Modified Components:**

- `config/settings.py` - Add custom apps, configure DRF settings, JWT secret configuration
- `config/urls.py` - Include app URL patterns

### Data Models

**New Models (see data-model.md for complete details):**

1. **User** (authentication/models.py)
   - Fields: id (UUID), first_name, last_name, middle_name (nullable), email (unique), password_hash, is_active, created_at, updated_at, last_login_at
   - Indexes: email (unique), is_active
   
2. **Role** (authorization/models.py)
   - Fields: id (UUID), name (unique), description, created_at, updated_at
   - Indexes: name (unique)
   
3. **BusinessElement** (authorization/models.py)
   - Fields: id (UUID), name (unique), description, created_at
   - Indexes: name (unique)
   
4. **AccessRoleRules** (authorization/models.py)
   - Fields: id (UUID), role (FK), element (FK), read_permission, read_all_permission, create_permission, update_permission, update_all_permission, delete_permission, delete_all_permission, created_at
   - Indexes: (role, element) composite unique, role (FK index), element (FK index)
   
5. **UserRole** (authorization/models.py)
   - Fields: id (UUID), user (FK), role (FK), assigned_at, assigned_by (FK nullable)
   - Indexes: (user, role) composite unique, user (FK index), role (FK index)
   
6. **TokenBlacklist** (authentication/models.py)
   - Fields: id (UUID), token_hash (unique), user (FK), blacklisted_at, expires_at
   - Indexes: token_hash (unique), expires_at

**Migrations Strategy:**

- Create initial migrations for all models using `uv run manage.py makemigrations`
- Apply migrations with `uv run python manage.py migrate`
- Create data migration for seed data (default roles, business elements, admin user, sample access rules)
- SQLite-compatible design (avoid PostgreSQL-specific features), use UUIDs for primary keys
- Enable foreign key constraints in SQLite via settings

### API Design

**Endpoint Groups (see contracts/openapi.yaml for complete contracts):**

1. **Authentication (`/api/auth/`)**
   - POST `/register` - Register new user (201 Created, 400 validation errors)
   - POST `/login` - Authenticate and get JWT token (200 OK with token, 401 invalid credentials, 403 inactive account)
   - POST `/logout` - Invalidate token (200 OK, 401 if not authenticated)
   - GET `/profile` - Get authenticated user profile (200 OK, 401 if not authenticated)
   - PATCH `/profile` - Update profile (200 OK with updated data, 400 validation errors, 401 if not authenticated)
   - DELETE `/profile` - Soft delete account (200 OK, 401 if not authenticated)

2. **Admin (`/api/admin/`) - Requires admin role**
   - GET `/roles` - List all roles (200 OK, 403 if not admin)
   - POST `/roles` - Create new role (201 Created, 403 if not admin)
   - GET `/business-elements` - List business elements (200 OK, 403 if not admin)
   - POST `/business-elements` - Create business element (201 Created, 403 if not admin)
   - GET `/access-rules` - List access rules (200 OK, 403 if not admin)
   - POST `/access-rules` - Create access rule (201 Created, 403 if not admin)
   - POST `/users/{id}/roles` - Assign role to user (200 OK, 403 if not admin)

3. **Resources (`/api/resources/`) - Permission-based access**
   - GET `/documents` - List documents (200 OK if has read_all_permission on documents, 403 if no permission, 401 if not authenticated)
   - POST `/documents` - Create document (201 Created if has create_permission, 403 if no permission)
   - GET `/projects` - List projects (200 OK if has read_all_permission on projects, 403 if no permission)

**Response Format (Constitutional Principle 3):**

Success:
```json
{
  "data": { /* payload */ },
  "meta": { "timestamp": "ISO8601", "total_count": 100 }
}
```

Error:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [{"field": "name", "message": "specific error"}]
  }
}
```

**Authentication & Authorization:**

- JWT tokens passed via `Authorization: Bearer <token>` header
- Custom DRF authentication class validates JWT and checks blacklist
- Custom DRF permission classes check RBAC rules against AccessRoleRules table
- 401 for authentication failures (missing/invalid/expired/blacklisted tokens)
- 403 for authorization failures (valid token but insufficient permissions)

### Dependencies

**External Libraries (already in pyproject.toml):**

- `django>=6.0.1` - Web framework
- `djangorestframework>=3.16.1` - REST API framework
- `pyjwt>=2.10.1` - JWT token generation/validation
- `bcrypt>=5.0.0` - Password hashing

**Development Dependencies:**

- `ruff>=0.14.10` - Linting and formatting
- `mypy>=1.19.1` - Static type checking
- `pytest` + `pytest-django` + `pytest-cov` (to be added) - Testing framework

**Internal Modules:**

- `core.authentication.JWTAuthentication` - Custom DRF authentication backend
- `core.permissions.RBACPermission` - Custom DRF permission class
- `core.exceptions.CustomExceptionHandler` - Standardized error response handler
- `core.utils.response_wrapper` - Helper functions for data/error/meta responses

## Implementation Strategy

### Phases

**Phase 1: Core Authentication (Week 1-2)**

**Tasks:**
1. Create Django project structure and apps
2. Implement User model with bcrypt password hashing
3. Implement registration endpoint with validation
4. Implement login endpoint with JWT token generation
5. Implement TokenBlacklist model
6. Implement logout endpoint with token blacklisting
7. Create JWTAuthentication class for DRF
8. Implement profile retrieval and update endpoints
9. Implement soft deletion endpoint
10. Write unit and integration tests for authentication flow
11. Create management command for cleanup of expired blacklisted tokens

**Deliverables:**
- User registration, login, logout functional
- JWT tokens generated with correct claims (sub, exp, iat, email)
- Password hashing with bcrypt (12 rounds)
- Token blacklist working
- 95% test coverage for authentication logic
- All endpoints respond < 200ms

**Phase 2: Authorization System (Week 3-4)**

**Tasks:**
1. Implement Role, BusinessElement, AccessRoleRules, UserRole models
2. Create admin endpoints for role management (list, create)
3. Create admin endpoints for business element management
4. Create admin endpoints for access rule management (list, create, update)
5. Create admin endpoint for user role assignment
6. Implement RBACPermission class for permission checking
7. Add permission checking decorator/mixin for views
8. Create data migration with seed data (roles, elements, rules)
9. Write comprehensive RBAC tests (unit + integration)
10. Optimize permission queries with select_related/prefetch_related

**Deliverables:**
- Complete RBAC system with user-specified schema (roles, business_elements, access_roles_rules)
- Admin can manage roles, elements, and access rules via API
- Permission checks return correct 403 errors
- Seed data includes: admin/user/moderator/guest roles, users/documents/projects/orders/shops/products elements
- 95% test coverage for authorization logic
- Permission checks complete in < 50ms

**Phase 3: Mock Resources & Integration (Week 5)**

**Tasks:**
1. Create mock document resource endpoints (list, create)
2. Create mock project resource endpoints (list, create)
3. Apply RBAC permission checks to all mock resource endpoints
4. Create comprehensive seed data (test users with different roles)
5. Generate OpenAPI schema documentation
6. Create Swagger UI and ReDoc endpoints
7. Write end-to-end integration tests
8. Perform performance testing and optimization
9. Implement rate limiting on authentication endpoints
10. Write security tests

**Deliverables:**
- Mock endpoints demonstrate working RBAC
- Seed data: admin@example.com/Admin123, user@example.com/User123, moderator@example.com/Mod123
- Complete OpenAPI documentation accessible at /api/docs/
- All integration tests passing
- Rate limiting: 5 login attempts per minute per IP
- Performance benchmarks met (< 200ms per endpoint)

### Code Quality Measures (Principle 1)

**Type Hints:**
- All function signatures include type hints for parameters and return types
- Use `from typing import` for complex types (Optional, List, Dict, etc.)
- mypy strict mode enabled in CI pipeline

**Documentation:**
- All public classes and methods include Google-style docstrings
- Docstrings include: description, Args, Returns, Raises
- API documentation generated from OpenAPI schema

**Linting/Formatting:**
- Ruff for linting (replaces Flake8, isort, Black)
- Configuration in `pyproject.toml`
- Pre-commit hooks enforce formatting (optional but recommended)
- Max line length: 88 characters

**Code Review:**
- All PRs require approval from at least one other developer
- Review checklist: type hints, tests, documentation, performance, security
- No self-merging allowed

**Complexity:**
- Cyclomatic complexity monitored via Ruff
- Functions exceeding complexity 10 require refactoring or explicit justification
- Break complex functions into smaller helper functions

### Testing Strategy (Principle 2)

**Unit Tests (80% coverage overall, 95% for auth/authz):**

- `authentication/tests/test_models.py` - User model, password hashing, validation
- `authentication/tests/test_services.py` - JWT generation, token validation, blacklist checks
- `authentication/tests/test_views.py` - Registration, login, logout, profile endpoints
- `authorization/tests/test_models.py` - Role, BusinessElement, AccessRoleRules, UserRole models
- `authorization/tests/test_permissions.py` - RBAC permission checking logic
- `authorization/tests/test_views.py` - Admin endpoints for role/permission management
- `resources/tests/test_views.py` - Mock resource endpoints with permission checks
- `core/tests/test_authentication.py` - JWTAuthentication class
- `core/tests/test_permissions.py` - RBACPermission class
- `core/tests/test_utils.py` - Response wrappers, exception handlers

**Integration Tests:**

- Complete registration → login → authenticated request → logout flow
- Permission checks: admin access, user denied access, moderator partial access
- Token expiration and blacklist validation
- Soft deletion flow (account deactivation → login denied)
- Role assignment flow (admin assigns role → user gains permissions)
- Rate limiting enforcement (5 failed logins → 429 error)

**Performance Tests:**

- Benchmark all authentication endpoints (< 200ms target)
- Benchmark permission checks (< 50ms target)
- Test concurrent authentication (100 simultaneous requests)
- Verify no N+1 queries (django-debug-toolbar in dev, query count assertions in tests)

**Security Tests:**

- Passwords never returned in responses
- Password hashes use bcrypt with 12 rounds
- JWT tokens expire after 24 hours
- Expired tokens rejected with 401
- Blacklisted tokens rejected with 401
- Rate limiting prevents brute force
- SQL injection protection (parameterized queries)
- XSS protection (Django's built-in escaping)

**Test Data Management:**

- Use factories (factory_boy or custom) for test data generation
- Fixtures for seed data (roles, elements, test users)
- TransactionTestCase for tests requiring database state
- Mock external dependencies (email services, etc.)

**Coverage Tools:**

- pytest-cov for coverage reports
- CI pipeline fails if coverage drops below 80%
- HTML coverage reports generated for review

### Performance Considerations (Principle 4)

**Response Time Targets:**

- Authentication endpoints: < 200ms (95th percentile)
- Authorization checks: < 50ms
- Mock resource endpoints: < 200ms

**Database Query Optimization:**

- Use `select_related()` for foreign key lookups (User → UserRole → Role)
- Use `prefetch_related()` for reverse FK and M2M (Role → AccessRoleRules → BusinessElement)
- Query optimization in permission checking:
  ```python
  user.userrole_set.select_related('role').prefetch_related(
      'role__accessrolerules_set__element'
  )
  ```
- Indexes on all foreign keys (Django default) and composite indexes on junction tables
- Monitor query count with django-debug-toolbar in development

**Caching Strategy:**

- No caching in initial implementation (keep simple)
- Future enhancement: Cache user permissions (5-minute TTL) with cache invalidation on role/permission changes
- Consider Redis for token blacklist in production (faster than SQLite lookups)

**Background Jobs:**

- Token blacklist cleanup: Daily management command to delete expired tokens
- Run via cron or Celery (cron sufficient for MVP)
- Future: Email sending, audit log processing

**Rate Limiting:**

- Django Ratelimit decorator on authentication views
- Policies:
  - Login: 5 attempts per minute per IP
  - Registration: 10 attempts per hour per IP
  - Authenticated endpoints: 100 requests per minute per user
- Return 429 Too Many Requests with Retry-After header
- Store rate limit counters in cache (in-memory for dev, Redis for production)

## Risk Assessment

### Technical Risks

**Risk 1: JWT Token Security**

- **Issue:** JWT tokens are stateless and cannot be invalidated server-side without blacklist
- **Mitigation:** Implement token blacklist table, short token expiration (24 hours), secure secret key management
- **Impact:** Medium - Blacklist adds database overhead, but acceptable for security

**Risk 2: Permission Check Performance**

- **Issue:** RBAC permission checks require multi-table joins (User → UserRole → Role → AccessRoleRules → BusinessElement)
- **Mitigation:** Use select_related/prefetch_related, composite indexes, consider caching in future
- **Impact:** Low - Query optimization keeps checks under 50ms target

**Risk 3: SQLite Limitations**

- **Issue:** SQLite has limited concurrency, no true foreign key enforcement by default
- **Mitigation:** Enable foreign key constraints in settings, design for PostgreSQL compatibility, test migrations against PostgreSQL
- **Impact:** Low - Acceptable for development, production should use PostgreSQL

**Risk 4: bcrypt Hashing Performance**

- **Issue:** bcrypt intentionally slow (~250ms per hash), adds latency to registration/login
- **Mitigation:** Acceptable trade-off for security, 12 rounds balances security and performance
- **Impact:** Low - Only affects registration and login, not subsequent requests

### Performance Risks

**Risk 1: N+1 Queries in Permission Checks**

- **Concern:** Naive RBAC implementation could cause N+1 queries for user permissions
- **Monitoring:** Use django-debug-toolbar, query count assertions in tests
- **Mitigation:** select_related/prefetch_related in all permission checking code paths

**Risk 2: Token Blacklist Table Growth**

- **Concern:** Blacklist table grows unbounded, slowing lookups
- **Monitoring:** Monitor table size, track cleanup job effectiveness
- **Mitigation:** Daily cleanup job removes expired tokens, index on token_hash

**Risk 3: Rate Limiting Overhead**

- **Concern:** Rate limit checks add latency to every request
- **Monitoring:** Benchmark with rate limiting enabled
- **Mitigation:** Use in-memory cache for rate limit counters, efficient rate limit algorithms

### Security Considerations

**Password Security:**

- Bcrypt with 12 salt rounds (meets constitutional requirement)
- Passwords never logged, never returned in API responses
- Password validation: minimum 8 characters, uppercase, lowercase, number
- Constant-time comparison via bcrypt.checkpw()

**Token Security:**

- JWT secret key stored in environment variables (never in code)
- JWT secret key is loaded from the .env file via `python-dotenv` library (already installed in venv and added to pyproject.toml). Create .env.example file.
- 256-bit cryptographically random secret
- Tokens transmitted via Authorization header only (not URL parameters)
- HTTPS required in production
- Token expiration enforced (24-hour lifetime)
- Blacklist for immediate logout

**Authorization Security:**

- Principle of least privilege: Default "user" role has minimal permissions
- Explicit permission grants required (no wildcards)
- Admin endpoints protected by role checks
- Permission changes take effect immediately
- Audit trail: UserRole tracks who assigned roles

**Input Validation:**

- Django REST Framework serializers for all input validation
- Email format validation
- Password complexity validation
- SQL injection protection via ORM parameterized queries
- XSS protection via Django's auto-escaping

**Rate Limiting:**

- Prevents brute force password attacks
- 5 failed login attempts per minute per IP
- Logged for security monitoring

## Success Criteria

- [x] All constitutional principles satisfied
- [x] Feature specification (FR-1 through FR-13) fully addressed
- [ ] Tests passing with 80%+ overall coverage, 95%+ for auth/authz
- [ ] Performance benchmarks met (< 200ms per endpoint, < 50ms permission checks)
- [ ] Documentation complete (OpenAPI schema, README, docstrings)
- [ ] Code review approved (type hints, complexity checks passed)
- [ ] Security audit passed (password hashing, token validation, rate limiting)
- [ ] Seed data enables immediate system demonstration
- [ ] All linting and type checking passing (Ruff, mypy)

## Timeline

**Phase 1: Core Authentication** - Weeks 1-2 (80 hours)
- Week 1: Models, registration, login, JWT implementation
- Week 2: Logout, profile management, soft deletion, tests

**Phase 2: Authorization System** - Weeks 3-4 (80 hours)
- Week 3: RBAC models, admin endpoints, permission checking
- Week 4: Seed data, tests, query optimization

**Phase 3: Mock Resources & Integration** - Week 5 (40 hours)
- Mock endpoints, OpenAPI docs, integration tests, performance testing

**Total Estimated Effort:** 200 hours (5 weeks at 40 hours/week)

## Open Questions

**All questions resolved.** Key decisions documented in research.md:

- ✅ Framework: Django REST Framework
- ✅ Authentication: PyJWT with custom implementation
- ✅ Password hashing: bcrypt with 12 rounds
- ✅ Database: SQLite (dev), PostgreSQL-compatible design
- ✅ Authorization: RBAC with user-specified schema (roles, business_elements, access_roles_rules)
- ✅ Token revocation: Database-backed blacklist
- ✅ Rate limiting: Django Ratelimit
- ✅ Response format: Standardized data/error/meta JSON pattern

---

**Plan Status:** ✅ **APPROVED** - Ready for implementation

**Related Documents:**
- Feature Specification: `specs/001-custom-auth-system/spec.md`
- Data Model: `specs/001-custom-auth-system/data-model.md`
- API Contracts: `specs/001-custom-auth-system/contracts/openapi.yaml`
- Research & Decisions: `specs/001-custom-auth-system/research.md`
- Quickstart Guide: `specs/001-custom-auth-system/quickstart.md`
