# Feature Specification: Custom Authentication and Authorization System

**Version:** 1.0.0  
**Date:** 2026-01-08  
**Status:** Draft

## Executive Summary

This specification defines a custom backend authentication and authorization system that implements user management, session handling, and role-based access control (RBAC) without relying on out-of-the-box framework features. The system will enable user registration, login/logout, profile management, soft deletion, and granular permission-based resource access control. It will include mock business objects to demonstrate the permission system in action, with proper HTTP status code handling (401 for unauthenticated, 403 for unauthorized access).

## Constitutional Compliance

This specification adheres to the project constitution (v1.0.0). Each requirement below is mapped to applicable constitutional principles.

## Requirements

### Functional Requirements

| ID | Requirement | Priority | Constitutional Principle |
|----|-------------|----------|--------------------------|
| FR-1 | Users can register with first name, last name, middle name (optional), email, and password (with confirmation) | High | Principle 3: User Experience |
| FR-2 | Users can log in using email and password to create an authenticated session | High | Principle 3: User Experience |
| FR-3 | Users can log out to terminate their authenticated session | High | Principle 3: User Experience |
| FR-4 | Authenticated users can view and update their profile information | High | Principle 3: User Experience |
| FR-5 | Users can perform soft deletion of their account (sets is_active=False, prevents login, but retains data) | Medium | Principle 3: User Experience |
| FR-6 | System identifies authenticated users on subsequent requests after login | High | Principle 4: Performance |
| FR-7 | System implements role-based access control (RBAC) with roles, permissions, and resource mappings | High | Principle 1: Code Quality |
| FR-8 | System returns 401 Unauthorized when user cannot be authenticated | High | Principle 3: User Experience |
| FR-9 | System returns 403 Forbidden when authenticated user lacks permission for requested resource | High | Principle 3: User Experience |
| FR-10 | Admin users can view and modify roles and permissions through dedicated API endpoints | High | Principle 3: User Experience |
| FR-11 | System includes mock business resources (e.g., documents, projects) that respond with access-controlled data or errors | Medium | Principle 2: Testing Standards |
| FR-12 | Password hashing uses bcrypt with appropriate salt rounds | High | Principle 1: Code Quality |
| FR-13 | Authentication tokens (JWT) have expiration and are validated on each request | High | Principle 1: Code Quality |

### Non-Functional Requirements

#### Code Quality (Principle 1)

- Code MUST include type hints for all public interfaces
- Code MUST pass all linting and type checking (Ruff, mypy)
- Documentation MUST be complete before merge
- Cyclomatic complexity MUST stay below 10 per function
- Password handling MUST use bcrypt with minimum 12 salt rounds
- JWT tokens MUST include standard claims (sub, exp, iat)

#### Testing Requirements (Principle 2)

- Minimum 80% code coverage (95% for authentication and authorization logic)
- All API endpoints MUST have integration tests
- Regression tests MUST cover authentication edge cases (expired tokens, invalid credentials, soft-deleted users)
- Performance tests MUST validate response time targets for authentication operations
- Security tests MUST verify password hashing, token validation, and permission checks

#### User Experience (Principle 3)

- API responses MUST follow project JSON structure standards
- Error messages MUST be clear and actionable (e.g., "Invalid email or password" instead of "Authentication failed")
- HTTP status codes MUST be semantically correct (401 for authentication failure, 403 for authorization failure, 400 for validation errors)
- API documentation MUST be updated in OpenAPI/Swagger format
- Password validation MUST provide specific feedback (minimum length, complexity requirements)

#### Performance (Principle 4)

- API endpoints MUST respond within 200ms (95th percentile)
- Database queries MUST be optimized (no N+1, use select_related/prefetch_related)
- Token validation MUST be cached or use efficient lookup mechanisms
- Permission checks MUST be optimized with database indexes
- Rate limiting MUST be implemented for authentication endpoints (5 failed attempts per minute per IP)

## User Stories

### Story 1: User Registration

**As a** new user  
**I want** to register with my name, email, and password  
**So that** I can create an account and access the system

**Acceptance Criteria:**
- [ ] User can submit registration form with first name, last name, middle name (optional), email, password, and password confirmation
- [ ] System validates email format and uniqueness
- [ ] System validates password meets complexity requirements (minimum 8 characters, at least one uppercase, one lowercase, one number)
- [ ] System validates password and password confirmation match
- [ ] System hashes password using bcrypt before storage
- [ ] System returns 201 Created with user profile data (excluding password) on success
- [ ] System returns 400 Bad Request with specific validation errors on failure
- [ ] System assigns default "user" role to new registrants

**Constitutional Notes:**  
Aligns with Principle 1 (secure password hashing), Principle 2 (comprehensive validation testing), and Principle 3 (clear error messages).

### Story 2: User Login

**As a** registered user  
**I want** to log in with my email and password  
**So that** I can access protected resources

**Acceptance Criteria:**
- [ ] User can submit login form with email and password
- [ ] System validates credentials against stored hashed password
- [ ] System generates JWT token with 24-hour expiration on successful authentication
- [ ] System returns 200 OK with token and user profile data (excluding password)
- [ ] System returns 401 Unauthorized with clear error message for invalid credentials
- [ ] System prevents login for soft-deleted users (is_active=False) with appropriate error message
- [ ] System logs failed login attempts for security monitoring
- [ ] System implements rate limiting (5 attempts per minute per IP)

**Constitutional Notes:**  
Aligns with Principle 3 (correct HTTP status codes), Principle 4 (rate limiting), and security best practices.

### Story 3: User Logout

**As an** authenticated user  
**I want** to log out  
**So that** my session is terminated and my account is secure

**Acceptance Criteria:**
- [ ] User can submit logout request with valid authentication token
- [ ] System invalidates the current token (adds to blacklist or revokes)
- [ ] System returns 200 OK with confirmation message
- [ ] Subsequent requests with invalidated token return 401 Unauthorized

**Constitutional Notes:**  
Aligns with Principle 3 (clear confirmation) and security best practices.

### Story 4: Profile Management

**As an** authenticated user  
**I want** to view and update my profile information  
**So that** I can keep my account details current

**Acceptance Criteria:**
- [ ] User can retrieve their profile with GET request (requires authentication)
- [ ] User can update first name, last name, middle name, and email with PUT/PATCH request
- [ ] System validates updated email format and uniqueness
- [ ] System returns 200 OK with updated profile data
- [ ] System returns 401 Unauthorized if user is not authenticated
- [ ] System returns 400 Bad Request with validation errors for invalid updates
- [ ] Password updates require current password verification and separate endpoint

**Constitutional Notes:**  
Aligns with Principle 3 (clear validation feedback) and Principle 4 (optimized queries).

### Story 5: Account Soft Deletion

**As an** authenticated user  
**I want** to delete my account  
**So that** I can remove my access while retaining data integrity

**Acceptance Criteria:**
- [ ] User can submit account deletion request (requires authentication)
- [ ] System sets is_active=False for the user account
- [ ] System immediately invalidates user's current authentication token
- [ ] System logs user out automatically
- [ ] System prevents future login attempts for soft-deleted users
- [ ] System retains user data in database for audit/compliance purposes
- [ ] System returns 200 OK with confirmation message
- [ ] System returns 401 Unauthorized for subsequent requests

**Constitutional Notes:**  
Aligns with Principle 1 (data integrity) and Principle 3 (clear confirmation).

### Story 6: Role-Based Access Control

**As a** system administrator  
**I want** to define roles, permissions, and resource access rules  
**So that** I can control which users can access specific resources

**Acceptance Criteria:**
- [ ] System implements RBAC with roles (e.g., admin, user, moderator), permissions (e.g., read, write, delete), and resources (e.g., documents, projects)
- [ ] Admin users can create, read, update, and delete roles via API
- [ ] Admin users can create, read, update, and delete permissions via API
- [ ] Admin users can assign permissions to roles
- [ ] Admin users can assign roles to users
- [ ] System checks user permissions before granting access to protected resources
- [ ] System returns 403 Forbidden if user lacks required permission
- [ ] System returns 401 Unauthorized if user is not authenticated
- [ ] Changes to roles/permissions take effect immediately for subsequent requests

**Constitutional Notes:**  
Aligns with Principle 1 (clean architecture for RBAC), Principle 3 (correct HTTP status codes), and Principle 4 (efficient permission lookups).

### Story 7: Protected Resource Access

**As an** authenticated user with appropriate permissions  
**I want** to access business resources  
**So that** I can perform my work within the system

**Acceptance Criteria:**
- [ ] System provides mock resources (e.g., documents, projects) with permission requirements
- [ ] User requests to mock resources include authentication token
- [ ] System validates token and checks user permissions for the requested resource
- [ ] System returns resource data with 200 OK if user has required permission
- [ ] System returns 401 Unauthorized if token is missing or invalid
- [ ] System returns 403 Forbidden if user lacks required permission
- [ ] System returns 404 Not Found for non-existent resources (only if user is authenticated and authorized)
- [ ] Mock resources return realistic JSON data structures

**Constitutional Notes:**  
Aligns with Principle 3 (consistent error handling) and Principle 2 (testable mock data).

## API Specification

### Endpoint: POST /api/auth/register

**Description:** Register a new user account

**Request:**
```json
{
  "first_name": "Ivan",
  "last_name": "Petrov",
  "middle_name": "Sergeevich",
  "email": "ivan.petrov@example.com",
  "password": "SecurePass123",
  "password_confirmation": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "uuid-string",
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

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Registration validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email already exists"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters with uppercase, lowercase, and number"
      }
    ]
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: POST /api/auth/login

**Description:** Authenticate user and return JWT token

**Request:**
```json
{
  "email": "ivan.petrov@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": "uuid-string",
      "first_name": "Ivan",
      "last_name": "Petrov",
      "middle_name": "Sergeevich",
      "email": "ivan.petrov@example.com",
      "roles": ["user"]
    }
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": []
  }
}
```

**Error Response (403 Forbidden - Inactive User):**
```json
{
  "error": {
    "code": "ACCOUNT_INACTIVE",
    "message": "Your account has been deactivated",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: POST /api/auth/logout

**Description:** Logout user and invalidate current token

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
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

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: GET /api/auth/profile

**Description:** Retrieve authenticated user's profile

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid-string",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "middle_name": "Sergeevich",
    "email": "ivan.petrov@example.com",
    "is_active": true,
    "roles": ["user"],
    "created_at": "2026-01-08T12:00:00Z",
    "updated_at": "2026-01-08T12:00:00Z"
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: PATCH /api/auth/profile

**Description:** Update authenticated user's profile information

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request:**
```json
{
  "first_name": "Ivan",
  "last_name": "Ivanov",
  "email": "ivan.ivanov@example.com"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "uuid-string",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "middle_name": "Sergeevich",
    "email": "ivan.ivanov@example.com",
    "is_active": true,
    "roles": ["user"],
    "updated_at": "2026-01-08T12:05:00Z"
  },
  "meta": {
    "timestamp": "2026-01-08T12:05:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Profile update validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email already exists"
      }
    ]
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: DELETE /api/auth/profile

**Description:** Soft delete authenticated user's account

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "data": {
    "message": "Account successfully deactivated"
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: GET /api/admin/roles

**Description:** List all roles in the system (admin only)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "name": "admin",
      "description": "System administrator with full access",
      "permissions": [
        {"id": "uuid", "name": "manage_users", "resource": "users", "action": "all"},
        {"id": "uuid", "name": "manage_roles", "resource": "roles", "action": "all"}
      ]
    },
    {
      "id": "uuid-string",
      "name": "user",
      "description": "Standard user with basic access",
      "permissions": [
        {"id": "uuid", "name": "view_documents", "resource": "documents", "action": "read"}
      ]
    }
  ],
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 2
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: POST /api/admin/roles

**Description:** Create a new role (admin only)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request:**
```json
{
  "name": "moderator",
  "description": "Content moderator with review access",
  "permission_ids": ["uuid-1", "uuid-2"]
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "uuid-string",
    "name": "moderator",
    "description": "Content moderator with review access",
    "permissions": [
      {"id": "uuid-1", "name": "review_content", "resource": "content", "action": "review"},
      {"id": "uuid-2", "name": "view_reports", "resource": "reports", "action": "read"}
    ],
    "created_at": "2026-01-08T12:00:00Z"
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: GET /api/admin/permissions

**Description:** List all permissions in the system (admin only)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "uuid-string",
      "name": "view_documents",
      "resource": "documents",
      "action": "read",
      "description": "View document contents"
    },
    {
      "id": "uuid-string",
      "name": "edit_documents",
      "resource": "documents",
      "action": "write",
      "description": "Create and edit documents"
    }
  ],
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 2
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: POST /api/users/{user_id}/roles

**Description:** Assign role to user (admin only)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request:**
```json
{
  "role_id": "uuid-string"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "user_id": "uuid-string",
    "roles": [
      {"id": "uuid-1", "name": "user"},
      {"id": "uuid-2", "name": "moderator"}
    ]
  },
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z"
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to access this resource",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: GET /api/resources/documents

**Description:** List documents (mock endpoint demonstrating permission checking)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Required Permission:** `view_documents` on `documents` resource

**Response (200 OK):**
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

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to view documents",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

### Endpoint: GET /api/resources/projects

**Description:** List projects (mock endpoint demonstrating permission checking)

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Required Permission:** `view_projects` on `projects` resource

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "proj-1",
      "name": "Authentication System",
      "status": "In Progress",
      "created_at": "2026-01-01T10:00:00Z"
    },
    {
      "id": "proj-2",
      "name": "API Gateway",
      "status": "Planning",
      "created_at": "2026-01-07T09:00:00Z"
    }
  ],
  "meta": {
    "timestamp": "2026-01-08T12:00:00Z",
    "total_count": 2
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid authentication token required",
    "details": []
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to view projects",
    "details": []
  }
}
```

**Performance Target:** < 200ms (95th percentile)

## Data Model

### Model: User

```python
class User(models.Model):
    """
    User account with authentication credentials and profile information.
    """
    id: UUID  # Primary key
    first_name: str  # User's first name (max 100 chars)
    last_name: str  # User's last name (max 100 chars)
    middle_name: str | None  # User's middle name (optional, max 100 chars)
    email: str  # Unique email address (max 255 chars)
    password_hash: str  # Bcrypt hashed password
    is_active: bool  # Account active status (default True)
    created_at: datetime  # Account creation timestamp
    updated_at: datetime  # Last update timestamp
    last_login_at: datetime | None  # Last successful login
    
    class Meta:
        indexes = [
            models.Index(fields=['email']),  # Fast email lookup for authentication
            models.Index(fields=['is_active']),  # Filter active users
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]
```

### Model: Role

```python
class Role(models.Model):
    """
    User role defining a collection of permissions.
    """
    id: UUID  # Primary key
    name: str  # Unique role name (max 50 chars, e.g., "admin", "user", "moderator")
    description: str  # Human-readable role description (max 255 chars)
    created_at: datetime  # Role creation timestamp
    updated_at: datetime  # Last update timestamp
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),  # Fast role lookup
        ]
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_role_name'),
        ]
```

### Model: Permission

```python
class Permission(models.Model):
    """
    Permission defining an action on a resource.
    """
    id: UUID  # Primary key
    name: str  # Unique permission name (max 100 chars, e.g., "view_documents")
    resource: str  # Resource type (max 50 chars, e.g., "documents", "projects")
    action: str  # Action type (max 50 chars, e.g., "read", "write", "delete", "all")
    description: str  # Human-readable permission description (max 255 chars)
    created_at: datetime  # Permission creation timestamp
    
    class Meta:
        indexes = [
            models.Index(fields=['resource', 'action']),  # Fast permission lookup
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['resource', 'action'], 
                name='unique_resource_action'
            ),
        ]
```

### Model: UserRole

```python
class UserRole(models.Model):
    """
    Many-to-many relationship between users and roles.
    """
    id: UUID  # Primary key
    user: ForeignKey[User]  # User reference
    role: ForeignKey[Role]  # Role reference
    assigned_at: datetime  # Role assignment timestamp
    assigned_by: ForeignKey[User] | None  # Admin who assigned the role
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),  # Fast user role lookup
            models.Index(fields=['role']),  # Fast role membership lookup
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'], 
                name='unique_user_role'
            ),
        ]
```

### Model: RolePermission

```python
class RolePermission(models.Model):
    """
    Many-to-many relationship between roles and permissions.
    """
    id: UUID  # Primary key
    role: ForeignKey[Role]  # Role reference
    permission: ForeignKey[Permission]  # Permission reference
    assigned_at: datetime  # Permission assignment timestamp
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),  # Fast role permission lookup
            models.Index(fields=['permission']),  # Fast permission role lookup
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'], 
                name='unique_role_permission'
            ),
        ]
```

### Model: TokenBlacklist

```python
class TokenBlacklist(models.Model):
    """
    Blacklisted JWT tokens (for logout functionality).
    """
    id: UUID  # Primary key
    token: str  # JWT token string (hashed for storage)
    user: ForeignKey[User]  # User who owned the token
    blacklisted_at: datetime  # Token blacklist timestamp
    expires_at: datetime  # Original token expiration (for cleanup)
    
    class Meta:
        indexes = [
            models.Index(fields=['token']),  # Fast token lookup
            models.Index(fields=['expires_at']),  # Cleanup expired tokens
        ]
```

## Access Control Structure

The RBAC system follows this hierarchy:

```
User → UserRole → Role → RolePermission → Permission (Resource + Action)
```

### Permission Format

Permissions are defined as combinations of:
- **Resource**: The type of object being accessed (e.g., "documents", "projects", "users", "roles")
- **Action**: The operation being performed (e.g., "read", "write", "delete", "all")

### Example Permission Assignments

**Admin Role:**
- `users:all` - Full access to user management
- `roles:all` - Full access to role management
- `permissions:all` - Full access to permission management
- `documents:all` - Full access to documents
- `projects:all` - Full access to projects

**User Role:**
- `documents:read` - Can view documents
- `projects:read` - Can view projects

**Moderator Role:**
- `documents:read` - Can view documents
- `documents:write` - Can create/edit documents
- `projects:read` - Can view projects

### Permission Check Algorithm

1. Extract user from authenticated token
2. Load all user's roles (via UserRole)
3. Load all permissions for those roles (via RolePermission)
4. Check if any permission matches the required resource and action
5. Grant access if match found, deny otherwise

### Seed Data for Testing

The system will include seed data for demonstration:

**Users:**
- Admin user: `admin@example.com` / `Admin123` (role: admin)
- Regular user: `user@example.com` / `User123` (role: user)
- Moderator: `moderator@example.com` / `Mod123` (role: moderator)

**Roles:**
- `admin` - Full system access
- `user` - Basic read access
- `moderator` - Read and write access to content

**Permissions:**
- `users:all`, `users:read`, `users:write`
- `roles:all`, `roles:read`, `roles:write`
- `permissions:all`, `permissions:read`
- `documents:read`, `documents:write`, `documents:delete`
- `projects:read`, `projects:write`, `projects:delete`

## Testing Specification

### Unit Tests

- [ ] Test user registration with valid data
- [ ] Test user registration with duplicate email
- [ ] Test user registration with invalid password
- [ ] Test user registration with mismatched password confirmation
- [ ] Test password hashing uses bcrypt with correct rounds
- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test login with inactive user account
- [ ] Test JWT token generation includes correct claims
- [ ] Test JWT token expiration validation
- [ ] Test token blacklist on logout
- [ ] Test profile update with valid data
- [ ] Test profile update with duplicate email
- [ ] Test soft deletion sets is_active to False
- [ ] Test soft deletion invalidates token
- [ ] Test permission checking algorithm
- [ ] Test role assignment to users
- [ ] Test permission assignment to roles

### Integration Tests

- [ ] Test complete registration flow (POST /api/auth/register)
- [ ] Test complete login flow (POST /api/auth/login)
- [ ] Test authenticated request with valid token
- [ ] Test authenticated request with expired token (401)
- [ ] Test authenticated request with blacklisted token (401)
- [ ] Test logout flow (POST /api/auth/logout)
- [ ] Test profile retrieval (GET /api/auth/profile)
- [ ] Test profile update (PATCH /api/auth/profile)
- [ ] Test account soft deletion (DELETE /api/auth/profile)
- [ ] Test admin can list roles (GET /api/admin/roles)
- [ ] Test non-admin cannot list roles (403)
- [ ] Test admin can create role (POST /api/admin/roles)
- [ ] Test admin can assign role to user (POST /api/users/{id}/roles)
- [ ] Test access to mock documents with permission (200)
- [ ] Test access to mock documents without permission (403)
- [ ] Test access to mock documents without authentication (401)
- [ ] Test rate limiting on login endpoint

### Performance Tests

- [ ] Benchmark registration endpoint < 200ms
- [ ] Benchmark login endpoint < 200ms
- [ ] Benchmark profile retrieval < 200ms
- [ ] Benchmark permission check < 50ms
- [ ] Test system under 100 concurrent authentication requests
- [ ] Verify no N+1 queries in permission checking
- [ ] Test token validation caching effectiveness

### Security Tests

- [ ] Verify passwords are never returned in API responses
- [ ] Verify password hashes use bcrypt with minimum 12 rounds
- [ ] Verify JWT tokens include expiration claims
- [ ] Verify expired tokens are rejected
- [ ] Verify blacklisted tokens are rejected
- [ ] Verify rate limiting prevents brute force attacks
- [ ] Verify SQL injection protection on all inputs
- [ ] Verify XSS protection on text fields

## Security Considerations

### Authentication Security

- **Password Storage**: All passwords are hashed using bcrypt with 12+ salt rounds before storage. Plain-text passwords are never stored.
- **Token Management**: JWT tokens include standard claims (sub, exp, iat) and expire after 24 hours. Tokens are blacklisted upon logout.
- **Rate Limiting**: Login endpoint is rate-limited to 5 attempts per minute per IP address to prevent brute force attacks.
- **Session Invalidation**: Soft-deleted users have their tokens immediately blacklisted and cannot log in.

### Authorization Security

- **Permission Checks**: All protected endpoints verify user authentication and authorization before processing requests.
- **Principle of Least Privilege**: New users are assigned the basic "user" role by default with minimal permissions.
- **Admin Protection**: Admin-only endpoints verify user has admin role before allowing access to role/permission management.

### Data Validation and Sanitization

- **Input Validation**: All user inputs are validated for format, length, and content before processing.
- **SQL Injection Protection**: All database queries use parameterized queries or ORM methods.
- **XSS Protection**: Text fields are sanitized to prevent cross-site scripting attacks.
- **Email Validation**: Email addresses are validated for proper format and uniqueness.

### Audit and Monitoring

- **Failed Login Logging**: Failed authentication attempts are logged for security monitoring.
- **Token Blacklist Cleanup**: Expired tokens are periodically removed from blacklist to prevent table bloat.
- **Role Assignment Tracking**: Role assignments track which admin assigned the role and when.

## Rollout Plan

### Phase 1: Core Authentication (Week 1-2)

**Deliverables:**
- User model with registration, login, logout
- Password hashing with bcrypt
- JWT token generation and validation
- Profile retrieval and update
- Soft deletion functionality
- Token blacklist for logout
- Basic integration tests

**Success Criteria:**
- All authentication endpoints functional
- 80%+ test coverage for auth module
- All security tests passing
- Performance targets met (<200ms)

### Phase 2: Authorization System (Week 3-4)

**Deliverables:**
- Role, Permission, UserRole, RolePermission models
- Admin endpoints for role/permission management
- Permission checking middleware/decorator
- User role assignment functionality
- Comprehensive RBAC tests
- Documentation of access control structure

**Success Criteria:**
- Complete RBAC implementation
- Admin can manage roles and permissions via API
- Permission checks return correct 401/403 errors
- 95%+ test coverage for authorization module
- README.md includes RBAC structure documentation

### Phase 3: Mock Resources and Integration (Week 5)

**Deliverables:**
- Mock document and project endpoints
- Permission-based access control on mock resources
- Seed data for testing (users, roles, permissions)
- Complete API documentation (OpenAPI/Swagger)
- End-to-end integration tests
- Performance optimization

**Success Criteria:**
- Mock endpoints demonstrate working RBAC
- Seed data allows immediate system demonstration
- All integration tests passing
- Performance benchmarks met
- Complete API documentation published

## Success Metrics

- [ ] All functional requirements (FR-1 through FR-13) implemented
- [ ] All constitutional principles satisfied
- [ ] Test coverage ≥ 80% (95% for authentication and authorization logic)
- [ ] Performance targets achieved (<200ms for all endpoints)
- [ ] API documentation complete in OpenAPI/Swagger format
- [ ] Code review passed with no critical issues
- [ ] Security audit passed (password hashing, token validation, rate limiting)
- [ ] RBAC structure documented in README.md
- [ ] Seed data enables full system demonstration
- [ ] All linting and type checking passing (Ruff, mypy)

## Dependencies

### External Libraries
- **bcrypt**: Password hashing (minimum 12 salt rounds)
- **PyJWT**: JWT token generation and validation
- **Django REST Framework**: API framework (already in project)

### Database
- PostgreSQL or SQLite for development
- Migrations for all models (User, Role, Permission, UserRole, RolePermission, TokenBlacklist)

### Infrastructure
- Rate limiting mechanism (Django Ratelimit or similar)
- Token blacklist storage (database table)
- Periodic cleanup job for expired blacklisted tokens

## Assumptions

1. **Authentication Method**: System uses JWT tokens for stateless authentication rather than session-based authentication for scalability.
2. **Token Expiration**: Default token lifetime is 24 hours; users must re-authenticate after expiration.
3. **Password Requirements**: Minimum 8 characters with at least one uppercase, one lowercase, and one number.
4. **Email Verification**: Email verification is NOT required for this initial implementation (can be added later).
5. **Password Reset**: Password reset functionality is NOT included in this specification (can be added later).
6. **Multi-Factor Authentication**: MFA is NOT included in this specification (can be added later).
7. **Permission Wildcards**: The "all" action grants full access to a resource (read, write, delete).
8. **Default Role**: New users automatically receive the "user" role with basic read permissions.
9. **Admin Creation**: First admin user is created via database seed/migration (not through registration endpoint).
10. **Mock Resources**: Mock endpoints return static/hardcoded data; no actual business logic or database tables are created.

## Open Questions

No critical unresolved questions remain. All assumptions documented above.

## Appendix

### Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-08 | Initial specification | AI Agent |

### References

- Constitution v1.0.0 (.specify/memory/constitution.md)
- Django REST Framework Documentation
- JWT RFC 7519
- OWASP Authentication Cheat Sheet
- OWASP Authorization Cheat Sheet
- bcrypt Password Hashing

### RBAC Structure Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                 │
│  - id, email, password_hash, is_active                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (many-to-many via UserRole)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                         Role                                 │
│  - id, name, description                                     │
│  Examples: admin, user, moderator                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (many-to-many via RolePermission)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      Permission                              │
│  - id, name, resource, action, description                  │
│  Examples: documents:read, projects:write, users:all        │
└─────────────────────────────────────────────────────────────┘

Permission Check Flow:
1. Request arrives with JWT token
2. Extract user_id from token
3. Query: UserRole → get all role_ids for user
4. Query: RolePermission → get all permission_ids for roles
5. Query: Permission → get all permissions (resource, action)
6. Check if required (resource, action) exists in user's permissions
7. Grant (200) or Deny (403) access
```

### Example Permission Matrix

| Role | documents:read | documents:write | projects:read | projects:write | users:all | roles:all |
|------|----------------|-----------------|---------------|----------------|-----------|-----------|
| admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| moderator | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| user | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ |
