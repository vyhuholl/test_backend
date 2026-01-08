# Research & Design Decisions

**Feature:** Custom Authentication and Authorization System  
**Date:** 2026-01-08  
**Status:** Completed

## Overview

This document captures research findings, technology evaluations, and design decisions for the custom authentication and authorization system. All technical choices have been validated against the project constitution and evaluated for best practices.

## Technology Stack Decisions

### Decision 1: Django REST Framework for API Layer

**Decision:** Use Django REST Framework (DRF) 3.16.1+ for building REST APIs

**Rationale:**
- Mature, production-tested framework with extensive ecosystem
- Built-in serialization, validation, and request/response handling
- Flexible authentication and permission class system (customizable for our needs)
- Excellent documentation and community support
- Integrates seamlessly with Django ORM
- Supports OpenAPI schema generation for documentation

**Alternatives Considered:**
- **FastAPI:** Modern, high-performance, but would require re-architecting away from Django
- **Plain Django Views:** More control but requires building serialization/validation from scratch
- **Django Ninja:** Newer, but less mature ecosystem and community support

**Best Practices:**
- Use ViewSets for CRUD operations (reduces boilerplate)
- Create custom permission classes for RBAC enforcement
- Use serializers for validation (DRY principle)
- Leverage DRF's exception handling for consistent error responses
- Use `select_related()` and `prefetch_related()` in viewsets to prevent N+1 queries

**References:**
- DRF Official Documentation: https://www.django-rest-framework.org/
- DRF Best Practices: Authentication & Permissions patterns

---

### Decision 2: PyJWT for JWT Token Management

**Decision:** Use PyJWT 2.10.1+ library for JWT token generation and validation

**Rationale:**
- Pure Python implementation (no external dependencies)
- Supports all standard JWT algorithms (HS256, RS256, etc.)
- Actively maintained with regular security updates
- Type-annotated for mypy compatibility
- Lightweight and fast
- Handles token expiration, validation, and claim management

**Alternatives Considered:**
- **python-jose:** More features but heavier dependencies (cryptography library)
- **djangorestframework-simplejwt:** DRF-specific, but we need custom token management
- **authlib:** Full OAuth2 solution, too heavyweight for our needs

**Implementation Approach:**
- Algorithm: HS256 (HMAC with SHA-256)
- Secret key: Stored in environment variables, 256-bit random
- Token lifetime: 24 hours (86400 seconds)
- Claims: `sub` (user_id), `exp` (expiration), `iat` (issued_at), `email`
- Token delivery: Authorization header with Bearer scheme

**Best Practices:**
- Always validate token signature, expiration, and required claims
- Use strong secret keys (256-bit cryptographically random)
- Store secrets in environment variables (never in code)
- Implement token refresh mechanism for long-lived sessions (future enhancement)
- Check token blacklist before granting access
- Use short expiration times to limit window of compromise

**Security Considerations:**
- HS256 is symmetric (same key for sign and verify) - acceptable for single-server apps
- For microservices, consider RS256 (asymmetric) for better key distribution
- Tokens are stateless - blacklist required for logout functionality
- Never include sensitive data in token payload (it's base64-encoded, not encrypted)

**References:**
- PyJWT Documentation: https://pyjwt.readthedocs.io/
- JWT RFC 7519: https://tools.ietf.org/html/rfc7519
- OWASP JWT Cheat Sheet

---

### Decision 3: bcrypt for Password Hashing

**Decision:** Use bcrypt 5.0.0+ library for password hashing with 12 salt rounds

**Rationale:**
- Industry-standard password hashing algorithm
- Built-in salt generation (prevents rainbow table attacks)
- Adaptive algorithm - can increase rounds as hardware improves
- Intentionally slow to prevent brute-force attacks
- Python bcrypt library is well-maintained and widely used
- Constitutional requirement (Principle 1: Code Quality Excellence)

**Alternatives Considered:**
- **Argon2:** Winner of Password Hashing Competition, more secure, but requires C library
- **PBKDF2:** Built into Python, but less resistant to GPU cracking than bcrypt
- **scrypt:** Memory-hard function, but bcrypt is more battle-tested

**Implementation Approach:**
- Salt rounds: 12 (balances security and performance)
- Hash output: Store in User.password_hash field (60 character string)
- Verification: Use bcrypt.checkpw() for constant-time comparison
- Never log or return password or hash in API responses

**Best Practices:**
- Use `bcrypt.gensalt()` to generate cryptographically secure salts
- Use `bcrypt.hashpw()` for hashing during registration
- Use `bcrypt.checkpw()` for verification during login (constant-time comparison)
- 12 rounds provides ~250ms hashing time (acceptable for authentication)
- Consider increasing to 14 rounds in future as hardware improves
- Never reduce rounds below 10 (security floor)

**Performance Impact:**
- Hashing: ~250ms per password (by design - prevents brute force)
- Login latency: Acceptable trade-off for security
- No need to hash on every request (only registration and login)

**References:**
- bcrypt Documentation: https://github.com/pyca/bcrypt
- OWASP Password Storage Cheat Sheet
- How To Safely Store A Password (Coda Hale)

---

### Decision 4: SQLite for Development Database

**Decision:** Use SQLite for development and testing, with PostgreSQL-compatible schema design

**Rationale:**
- Zero configuration required for local development
- User-specified requirement
- Fast for development and testing
- File-based (no server process needed)
- Django ORM abstracts database differences
- Easy to reset/recreate during development

**Alternatives Considered:**
- **PostgreSQL:** Production-grade, but requires server setup for local dev
- **MySQL:** Popular, but more differences with PostgreSQL than SQLite

**Production Migration Path:**
- Design schema to be PostgreSQL-compatible (avoid SQLite-specific features)
- Use Django migrations (database-agnostic)
- Avoid raw SQL queries (use ORM)
- Test migrations against PostgreSQL in staging environment
- Use UUID primary keys (portable across databases)

**Best Practices:**
- Enable foreign key constraints in SQLite (not default)
- Use Django's transaction management (not database-specific)
- Index all foreign keys and frequently queried fields
- Use CharField for enums (not database-specific enum types)
- Test with production database in CI pipeline

**Schema Design Considerations:**
- UUID primary keys (not auto-incrementing integers)
- Explicit indexes on foreign keys
- Composite unique constraints for junction tables
- DateTimeField with auto_now/auto_now_add for timestamps
- TextField with max_length for descriptions (portable)

**References:**
- Django Database Documentation
- SQLite When To Use SQLite
- PostgreSQL Migration Best Practices

---

### Decision 5: Role-Based Access Control (RBAC) Implementation

**Decision:** Implement RBAC using user-provided database schema (roles, business_elements, access_roles_rules)

**Rationale:**
- Granular permission control at resource and action level
- Scalable to multiple roles and resources
- Flexible - can add new permissions without code changes
- Separates users, roles, and permissions (industry standard pattern)
- Matches user's specified database tables

**Alternatives Considered:**
- **Django's Built-in Permissions:** Too tightly coupled to Django models, not flexible enough
- **Attribute-Based Access Control (ABAC):** More complex, overkill for initial implementation
- **Simple Role-Based:** Too coarse-grained (admin vs user only)

**Implementation Architecture:**
```
User → UserRole → Role → AccessRoleRules → BusinessElement
                               ↓
                     [permission flags: read, create, update, delete, etc.]
```

**Permission Flags (from access_roles_rules table):**
- `read_permission`: Can view individual resource
- `read_all_permission`: Can list/view all resources
- `create_permission`: Can create new resources
- `update_permission`: Can update own resources
- `update_all_permission`: Can update any resource
- `delete_permission`: Can delete own resources
- `delete_all_permission`: Can delete any resource

**Permission Check Algorithm:**
1. Authenticate user from JWT token
2. Query UserRole to get user's roles
3. Query AccessRoleRules filtered by roles and requested business element
4. Check if any rule grants the required permission flag
5. Grant access if permission found, deny otherwise (403)

**Best Practices:**
- Cache user permissions (5-minute TTL) to reduce database load
- Use database transactions for role/permission changes
- Invalidate permission cache when roles/rules change
- Log permission denials for security monitoring
- Use composite indexes on (role, element) for fast lookups
- Principle of least privilege: Default "user" role has minimal permissions

**Performance Optimization:**
- Single query with JOINs: User → UserRole → Role → AccessRoleRules → BusinessElement
- Use select_related() and prefetch_related() for efficient queries
- Cache permission check results per request
- Index on (role_id, element_id) in access_roles_rules table

**References:**
- NIST RBAC Standard
- OWASP Authorization Cheat Sheet
- Django Custom Permissions Best Practices

---

### Decision 6: Token Blacklist for Logout

**Decision:** Implement token blacklist table for logout functionality (stateful approach)

**Rationale:**
- JWTs are stateless and cannot be invalidated server-side by design
- Token blacklist allows immediate logout and session termination
- Simple to implement with database table
- Meets security requirement for explicit logout

**Alternatives Considered:**
- **Short Token Lifetimes Only:** Logout wouldn't take effect until expiration (up to 24 hours)
- **Redis Blacklist:** Better performance, but adds dependency
- **Token Refresh Pattern:** More complex, requires two token types

**Implementation Approach:**
- Store SHA-256 hash of token (not plain token) in blacklist
- Include user_id and original expiration timestamp
- Check blacklist on every authenticated request
- Automatic cleanup job removes expired tokens daily
- Index on token_hash for O(1) lookup

**Best Practices:**
- Hash tokens before storing (reduces storage, adds layer of security)
- Include expires_at for efficient cleanup queries
- Run cleanup job daily via management command (cron/Celery)
- Consider Redis for blacklist in production (faster lookups)
- Monitor blacklist table size and cleanup effectiveness

**Performance Considerations:**
- Blacklist check adds ~5-10ms per authenticated request
- Cache frequently checked tokens (negative cache - "not in blacklist")
- Index on token_hash makes lookups efficient
- Cleanup prevents unbounded growth

**References:**
- JWT Revocation Strategies
- Token Blacklist Best Practices

---

### Decision 7: Rate Limiting Strategy

**Decision:** Implement rate limiting on authentication endpoints using Django Ratelimit or DRF throttling

**Rationale:**
- Prevents brute-force password attacks
- Mitigates denial-of-service (DoS) attacks
- Constitutional requirement (Principle 4: Performance Requirements)
- Protects system resources

**Rate Limit Policies:**
- Login endpoint: 5 attempts per minute per IP address
- Registration endpoint: 10 attempts per hour per IP address
- Other authenticated endpoints: 100 requests per minute per user
- Return 429 Too Many Requests with Retry-After header

**Alternatives Considered:**
- **Application-Level:** Django Ratelimit (simple, no external dependencies)
- **Middleware:** DRF Throttling (DRF-specific)
- **Infrastructure-Level:** Nginx/Cloudflare (requires infrastructure changes)

**Implementation Approach:**
- Use Django Ratelimit decorator on authentication views
- Track by IP address for anonymous requests
- Track by user_id for authenticated requests
- Store rate limit state in cache (Redis in production, in-memory for dev)
- Return standard error response with retry timing

**Best Practices:**
- Different limits for different endpoint types
- Log rate limit violations (security monitoring)
- Use cache backend (not database) for rate limit counters
- Include Retry-After header in 429 responses
- Consider CAPTCHA after repeated failures (future enhancement)

**References:**
- OWASP Rate Limiting Guide
- Django Ratelimit Documentation
- DRF Throttling Documentation

---

### Decision 8: Standardized API Response Format

**Decision:** Use consistent JSON structure for all API responses (data/error/meta pattern)

**Rationale:**
- Constitutional requirement (Principle 3: User Experience Consistency)
- Predictable response structure simplifies client integration
- Clear separation of data, metadata, and errors
- Industry best practice for REST APIs

**Response Format:**

**Success Response:**
```json
{
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 100  // for paginated lists
  }
}
```

**Error Response:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {"field": "email", "message": "Field-specific error"}
    ]
  }
}
```

**Implementation Approach:**
- Create custom exception handler in core app
- Create response wrapper utility functions
- Override DRF's default exception handler
- Use serializers for validation error formatting

**Error Codes:**
- `VALIDATION_ERROR`: Input validation failed (400)
- `AUTHENTICATION_REQUIRED`: Missing or invalid token (401)
- `INVALID_CREDENTIALS`: Login failed (401)
- `ACCOUNT_INACTIVE`: User soft-deleted (403)
- `INSUFFICIENT_PERMISSIONS`: No permission for resource (403)
- `NOT_FOUND`: Resource not found (404)
- `RATE_LIMIT_EXCEEDED`: Too many requests (429)
- `INTERNAL_ERROR`: Server error (500)

**Best Practices:**
- Never expose internal error details (stack traces, database errors)
- Use consistent error code naming (UPPER_SNAKE_CASE)
- Include actionable guidance in error messages
- Use HTTP status codes correctly
- Include timestamp in metadata
- Paginated responses include total_count

**References:**
- REST API Design Best Practices
- JSON API Specification
- Google JSON Style Guide

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| API Framework | Django REST Framework 3.16.1+ | Mature, flexible, excellent DRF ecosystem |
| Authentication | PyJWT 2.10.1+ with custom implementation | Lightweight, secure, full control |
| Password Hashing | bcrypt 5.0.0+ (12 rounds) | Industry standard, constitutional requirement |
| Database | SQLite (dev), PostgreSQL-compatible design | User-specified, easy local development |
| Authorization | Custom RBAC with user-provided schema | Granular control, flexible, scalable |
| Token Revocation | Database-backed blacklist | Enables immediate logout |
| Rate Limiting | Django Ratelimit | Prevents brute force, protects resources |
| Response Format | Standardized data/error/meta JSON | Consistent UX, constitutional requirement |

## Research Findings: Best Practices

### Django REST Framework Best Practices

1. **ViewSets for CRUD:** Use ModelViewSet for standard CRUD operations, reduces boilerplate
2. **Serializers for Validation:** Centralize validation logic in serializers, reuse across views
3. **Custom Permission Classes:** Create reusable permission classes for RBAC checks
4. **Pagination:** Always paginate list endpoints (default 50, max 100)
5. **Filtering and Search:** Use django-filter for complex filtering
6. **API Versioning:** Use URL path versioning (`/api/v1/`) for breaking changes
7. **Query Optimization:** Use `select_related()` and `prefetch_related()` in querysets
8. **Exception Handling:** Override DRF exception handler for consistent error responses

### JWT Security Best Practices

1. **Short Expiration:** 24 hours or less for access tokens
2. **HTTPS Only:** Never transmit tokens over HTTP
3. **Secure Storage:** Store secret keys in environment variables
4. **Minimal Claims:** Only include necessary data in token payload
5. **Validate Everything:** Check signature, expiration, issuer, audience on every request
6. **Token Rotation:** Consider refresh tokens for long-lived sessions
7. **Blacklist Support:** Implement revocation mechanism for logout
8. **Algorithm Specification:** Explicitly specify algorithm (don't use "none")

### Password Security Best Practices

1. **Strong Hashing:** bcrypt/Argon2 with appropriate work factor
2. **Never Log Passwords:** Exclude from logs, error messages, responses
3. **Password Requirements:** Minimum length, complexity rules
4. **Rate Limiting:** Prevent brute force attacks
5. **Constant-Time Comparison:** Use bcrypt.checkpw() for verification
6. **No Password Hints:** Don't store hints or reversible formats
7. **Secure Password Reset:** Use time-limited tokens (future enhancement)

### RBAC Implementation Best Practices

1. **Separation of Concerns:** Users, roles, permissions in separate tables
2. **Least Privilege:** Default to minimal permissions
3. **Explicit Grants:** Require explicit permission grants (no wildcards)
4. **Immediate Effect:** Permission changes take effect on next request
5. **Audit Trail:** Log role assignments and permission changes
6. **Performance:** Cache permissions, use database indexes
7. **Flexibility:** Design for adding roles/permissions without code changes

### API Design Best Practices

1. **RESTful Principles:** Use standard HTTP methods and status codes
2. **Consistent Naming:** Use plural nouns for resources (`/users`, `/documents`)
3. **Nested Resources:** For related resources (`/users/{id}/roles`)
4. **Filtering:** Query parameters for filtering (`?role=admin&is_active=true`)
5. **Pagination:** Limit, offset, cursor-based pagination
6. **Error Handling:** Consistent error format with actionable messages
7. **Documentation:** OpenAPI/Swagger schema for all endpoints
8. **Versioning:** Semantic versioning for breaking changes

---

## Open Issues & Future Research

**No critical issues remain.** All technical decisions have been made and validated.

**Future Research Topics (Post-MVP):**
- Email verification service integration (SendGrid, AWS SES)
- Password reset flow with secure token generation
- Multi-factor authentication (TOTP, SMS)
- OAuth2/OpenID Connect for social login
- Refresh token rotation strategy
- Redis caching architecture for production
- Celery task queue for background jobs
- Audit log system for compliance
- Advanced rate limiting with CAPTCHA

---

**Document Status:** ✅ Complete - All research completed, all decisions documented
