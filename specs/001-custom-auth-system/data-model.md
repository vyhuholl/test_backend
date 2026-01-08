# Data Model Specification

**Feature:** Custom Authentication and Authorization System  
**Date:** 2026-01-08  
**Version:** 1.0.0

## Overview

This document defines all database entities, relationships, validation rules, and state transitions for the custom authentication and authorization system. The data model follows Django ORM conventions and is optimized for PostgreSQL/SQLite compatibility.

---

## Entity-Relationship Diagram

```
┌──────────────────┐
│      User        │
│  (authentication)│
└────────┬─────────┘
         │ 1
         │
         │ M (via UserRole)
         ▼
┌──────────────────┐         ┌────────────────────┐
│    UserRole      │────────▶│       Role         │
│   (junction)     │   M:1   │  (authorization)   │
└──────────────────┘         └──────────┬─────────┘
                                        │ 1
                                        │
                                        │ M (via AccessRoleRules)
                                        ▼
┌──────────────────┐         ┌─────────────────────┐
│ AccessRoleRules  │────────▶│  BusinessElement    │
│  (permissions)   │   M:1   │   (resources)       │
└──────────────────┘         └─────────────────────┘

┌──────────────────┐
│ TokenBlacklist   │
│ (authentication) │
└────────┬─────────┘
         │ M:1
         │
         ▼
    ┌────────┐
    │  User  │
    └────────┘
```

---

## Entities

### 1. User (apps/authentication/models.py)

**Purpose:** Stores user account information, credentials, and profile data.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique user identifier |
| `first_name` | CharField(100) | Required, Not blank | User's first name |
| `last_name` | CharField(100) | Required, Not blank | User's last name |
| `middle_name` | CharField(100) | Nullable, Blank | User's middle name (optional) |
| `email` | EmailField(255) | Required, Unique, Indexed | User's email (login identifier) |
| `password_hash` | CharField(255) | Required | bcrypt hashed password |
| `is_active` | BooleanField | Default=True, Indexed | Account active status (soft delete flag) |
| `created_at` | DateTimeField | Auto_now_add=True | Account creation timestamp |
| `updated_at` | DateTimeField | Auto_now=True | Last profile update timestamp |
| `last_login_at` | DateTimeField | Nullable | Last successful login timestamp |

**Validation Rules:**
- `email`: Valid email format (Django EmailValidator), unique across all users
- `first_name`: Length 1-100 characters, no special validation
- `last_name`: Length 1-100 characters, no special validation
- `middle_name`: Length 0-100 characters (optional)
- `password_hash`: Set via bcrypt.hashpw(), never set directly
- Password (at registration): Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number

**Indexes:**
- `email` (unique index) - Fast authentication lookups
- `is_active` (index) - Filter active users efficiently

**Relationships:**
- One-to-Many with `UserRole` (user can have multiple roles)
- One-to-Many with `TokenBlacklist` (user can have multiple blacklisted tokens)

**Business Rules:**
- Email must be unique (case-insensitive comparison)
- Inactive users (is_active=False) cannot authenticate
- Password hash uses bcrypt with 12 salt rounds minimum
- Soft deletion sets `is_active=False` (data retained for audit)
- `last_login_at` updated on each successful login

**State Transitions:**
```
[New User]
    ↓ register()
[Active User] ⟷ authenticate() ⟶ [Authenticated Session]
    ↓ soft_delete()
[Inactive User] (cannot authenticate)
```

**Example:**
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "middle_name": "Sergeevich",
    "email": "ivan.petrov@example.com",
    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7kM3kXRtYS",
    "is_active": true,
    "created_at": "2026-01-08T12:00:00Z",
    "updated_at": "2026-01-08T12:00:00Z",
    "last_login_at": "2026-01-08T14:30:00Z"
}
```

---

### 2. TokenBlacklist (apps/authentication/models.py)

**Purpose:** Tracks invalidated JWT tokens for logout functionality.

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique blacklist entry identifier |
| `token_hash` | CharField(64) | Required, Unique, Indexed | SHA-256 hash of JWT token |
| `user` | ForeignKey(User) | CASCADE, Indexed | User who owned the token |
| `blacklisted_at` | DateTimeField | Auto_now_add=True | When token was blacklisted |
| `expires_at` | DateTimeField | Required, Indexed | Original token expiration time |

**Validation Rules:**
- `token_hash`: Must be 64-character SHA-256 hex string
- `expires_at`: Must be future timestamp when created

**Indexes:**
- `token_hash` (unique index) - O(1) blacklist lookups
- `expires_at` (index) - Efficient cleanup of expired entries
- `user` (foreign key index) - User's blacklisted tokens

**Relationships:**
- Many-to-One with `User` (user can have multiple blacklisted tokens)

**Business Rules:**
- Token hash computed as SHA-256 of full JWT string
- Entries automatically cleaned up after `expires_at` (daily job)
- Blacklist check required on every authenticated request
- Blacklisting token immediately invalidates it

**Example:**
```python
{
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "token_hash": "5d41402abc4b2a76b9719d911017c592ae986e5c8e2a6d4c8f7b3e9a1c0d5e4f",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "blacklisted_at": "2026-01-08T15:00:00Z",
    "expires_at": "2026-01-09T12:00:00Z"
}
```

---

### 3. Role (apps/authorization/models.py)

**Purpose:** Defines user roles in the system (admin, user, moderator, guest).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique role identifier |
| `name` | CharField(50) | Required, Unique, Indexed | Role name (lowercase) |
| `description` | TextField(255) | Required | Human-readable role description |
| `created_at` | DateTimeField | Auto_now_add=True | Role creation timestamp |
| `updated_at` | DateTimeField | Auto_now=True | Last update timestamp |

**Validation Rules:**
- `name`: 1-50 characters, lowercase, alphanumeric + underscore, unique
- `description`: 1-255 characters
- `name` should follow convention: admin, user, moderator, guest, manager, etc.

**Indexes:**
- `name` (unique index) - Fast role lookups by name

**Relationships:**
- One-to-Many with `UserRole` (role can be assigned to multiple users)
- One-to-Many with `AccessRoleRules` (role can have multiple permission rules)

**Business Rules:**
- Default roles created in seed migration: admin, user, moderator, guest
- Role names are immutable after creation (update description only)
- Cannot delete role if assigned to any user (prevent orphaned assignments)
- New users automatically assigned "user" role

**Predefined Roles:**

| Role | Description | Default Permissions |
|------|-------------|---------------------|
| `admin` | System administrator | All permissions on all elements |
| `user` | Standard user | Read-only on documents, projects |
| `moderator` | Content moderator | Read/write on documents, projects |
| `guest` | Limited guest access | Read-only on public documents |

**Example:**
```python
{
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "name": "admin",
    "description": "System administrator with full access to all resources",
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
}
```

---

### 4. BusinessElement (apps/authorization/models.py)

**Purpose:** Defines application resources/objects that can be accessed (users, documents, projects, etc.).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique element identifier |
| `name` | CharField(100) | Required, Unique, Indexed | Element name (lowercase, plural) |
| `description` | TextField(255) | Required | Human-readable element description |
| `created_at` | DateTimeField | Auto_now_add=True | Element creation timestamp |

**Validation Rules:**
- `name`: 1-100 characters, lowercase, alphanumeric + underscore, unique
- `description`: 1-255 characters
- `name` should follow convention: users, documents, projects, orders, products, etc.

**Indexes:**
- `name` (unique index) - Fast element lookups by name

**Relationships:**
- One-to-Many with `AccessRoleRules` (element can have multiple access rules)

**Business Rules:**
- Default elements created in seed migration: users, documents, projects, orders, shops, products
- Element names are immutable after creation
- Cannot delete element if referenced in any access rule
- Elements represent logical resources (may not correspond to database tables)

**Predefined Elements:**

| Element | Description | Example Operations |
|---------|-------------|-------------------|
| `users` | User accounts | Create, read, update, delete users |
| `documents` | Document resources | Read, create, update, delete documents |
| `projects` | Project resources | Read, create, update, delete projects |
| `orders` | Order records | Read, create, update, delete orders |
| `shops` | Shop listings | Read, create, update, delete shops |
| `products` | Product catalog | Read, create, update, delete products |

**Example:**
```python
{
    "id": "880e8400-e29b-41d4-a716-446655440000",
    "name": "documents",
    "description": "Document management system - create, view, edit, delete documents",
    "created_at": "2026-01-08T10:00:00Z"
}
```

---

### 5. AccessRoleRules (apps/authorization/models.py)

**Purpose:** Maps roles to business elements with granular permission flags (RBAC core table).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique rule identifier |
| `role` | ForeignKey(Role) | CASCADE, Indexed | Role this rule applies to |
| `element` | ForeignKey(BusinessElement) | CASCADE, Indexed | Element this rule controls |
| `read_permission` | BooleanField | Default=False | Can read/view individual resource |
| `read_all_permission` | BooleanField | Default=False | Can list/view all resources |
| `create_permission` | BooleanField | Default=False | Can create new resources |
| `update_permission` | BooleanField | Default=False | Can update own resources |
| `update_all_permission` | BooleanField | Default=False | Can update any resource |
| `delete_permission` | BooleanField | Default=False | Can delete own resources |
| `delete_all_permission` | BooleanField | Default=False | Can delete any resource |
| `created_at` | DateTimeField | Auto_now_add=True | Rule creation timestamp |

**Validation Rules:**
- `role` and `element` combination must be unique
- At least one permission flag should be True (warn if all False)

**Indexes:**
- `(role, element)` composite unique index - Fast permission lookups
- `role` (foreign key index) - Find all rules for a role
- `element` (foreign key index) - Find all rules for an element

**Constraints:**
- Unique constraint: (role, element)

**Relationships:**
- Many-to-One with `Role` (multiple rules per role)
- Many-to-One with `BusinessElement` (multiple rules per element)

**Business Rules:**
- One rule per (role, element) pair
- `*_all_permission` flags imply ownership-independent access
- Non-`*_all` flags imply ownership-dependent access (e.g., update own documents only)
- Permission changes take effect immediately (no caching across requests)
- Admin role typically has all `*_all_permission` flags set to True

**Permission Semantics:**

| Flag | Meaning | Example |
|------|---------|---------|
| `read_permission` | View individual resource by ID | GET /api/resources/documents/123 |
| `read_all_permission` | List and view all resources | GET /api/resources/documents |
| `create_permission` | Create new resource | POST /api/resources/documents |
| `update_permission` | Update owned resources | PATCH /api/resources/documents/123 (own) |
| `update_all_permission` | Update any resource | PATCH /api/resources/documents/* (any) |
| `delete_permission` | Delete owned resources | DELETE /api/resources/documents/123 (own) |
| `delete_all_permission` | Delete any resource | DELETE /api/resources/documents/* (any) |

**Example:**
```python
{
    "id": "990e8400-e29b-41d4-a716-446655440000",
    "role_id": "770e8400-e29b-41d4-a716-446655440000",  # admin
    "element_id": "880e8400-e29b-41d4-a716-446655440000",  # documents
    "read_permission": true,
    "read_all_permission": true,
    "create_permission": true,
    "update_permission": true,
    "update_all_permission": true,
    "delete_permission": true,
    "delete_all_permission": true,
    "created_at": "2026-01-08T10:00:00Z"
}
```

---

### 6. UserRole (apps/authorization/models.py)

**Purpose:** Junction table linking users to their assigned roles (many-to-many relationship).

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Default=uuid4() | Unique assignment identifier |
| `user` | ForeignKey(User) | CASCADE, Indexed | User being assigned the role |
| `role` | ForeignKey(Role) | CASCADE, Indexed | Role being assigned |
| `assigned_at` | DateTimeField | Auto_now_add=True | When role was assigned |
| `assigned_by` | ForeignKey(User) | SET_NULL, Nullable | Admin who assigned the role |

**Validation Rules:**
- `user` and `role` combination must be unique
- `assigned_by` must be an admin user (if not null)

**Indexes:**
- `(user, role)` composite unique index - Prevent duplicate assignments
- `user` (foreign key index) - Find user's roles
- `role` (foreign key index) - Find role members

**Constraints:**
- Unique constraint: (user, role)

**Relationships:**
- Many-to-One with `User` (via user field) - User receiving role
- Many-to-One with `Role` - Role being assigned
- Many-to-One with `User` (via assigned_by field) - Admin who assigned role

**Business Rules:**
- User can have multiple roles (accumulative permissions)
- New users automatically assigned "user" role (created in registration)
- Cannot remove last role from a user (must have at least one)
- Admin users can assign/remove roles
- Role assignment tracked with timestamp and assigner for audit trail

**Example:**
```python
{
    "id": "aa0e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "770e8400-e29b-41d4-a716-446655440000",
    "assigned_at": "2026-01-08T12:05:00Z",
    "assigned_by_id": "bb0e8400-e29b-41d4-a716-446655440000"
}
```

---

## Permission Check Flow

The permission checking system follows this algorithm:

```
1. Authenticate Request
   ├─ Extract JWT token from Authorization header
   ├─ Validate token signature, expiration, claims
   ├─ Check token against blacklist
   └─ Extract user_id from token

2. Load User Permissions (with caching)
   ├─ Query: UserRole WHERE user_id = ?
   ├─ Get all role_ids for user
   ├─ Query: AccessRoleRules WHERE role IN role_ids AND element = ?
   └─ Aggregate permission flags (OR operation across roles)

3. Check Required Permission
   ├─ Match requested action to permission flag
   │  ├─ GET /list → read_all_permission
   │  ├─ GET /{id} → read_permission
   │  ├─ POST → create_permission
   │  ├─ PATCH /{id} → update_permission or update_all_permission
   │  └─ DELETE /{id} → delete_permission or delete_all_permission
   └─ Grant if ANY role grants permission (OR logic)

4. Return Result
   ├─ GRANT: Continue to view handler (200)
   ├─ DENY: Return 403 Forbidden
   └─ UNAUTHENTICATED: Return 401 Unauthorized
```

---

## Database Migrations Strategy

### Migration Order:

1. **0001_initial_authentication.py**
   - Create User model
   - Create TokenBlacklist model
   - Add indexes

2. **0002_initial_authorization.py**
   - Create Role model
   - Create BusinessElement model
   - Create AccessRoleRules model
   - Create UserRole model
   - Add indexes and constraints

3. **0003_seed_roles.py** (Data migration)
   - Create default roles: admin, user, moderator, guest

4. **0004_seed_elements.py** (Data migration)
   - Create default business elements: users, documents, projects, orders, shops, products

5. **0005_seed_access_rules.py** (Data migration)
   - Create default access rules for each role-element combination
   - Admin gets all permissions on all elements
   - User gets read-only on documents, projects
   - Moderator gets read/write on documents, projects

6. **0006_seed_admin_user.py** (Data migration)
   - Create admin user: admin@example.com / Admin123
   - Create regular user: user@example.com / User123
   - Create moderator: moderator@example.com / Mod123
   - Assign roles to users

---

## Validation Rules Summary

### User Validation
- ✅ Email: Valid format, unique (case-insensitive)
- ✅ Password: 8+ characters, 1 uppercase, 1 lowercase, 1 number
- ✅ First name: 1-100 characters
- ✅ Last name: 1-100 characters
- ✅ Middle name: 0-100 characters (optional)

### Role Validation
- ✅ Name: 1-50 characters, lowercase, alphanumeric + underscore, unique
- ✅ Description: 1-255 characters

### BusinessElement Validation
- ✅ Name: 1-100 characters, lowercase, alphanumeric + underscore, unique
- ✅ Description: 1-255 characters

### AccessRoleRules Validation
- ✅ Unique (role, element) pair
- ✅ Role must exist
- ✅ Element must exist

### UserRole Validation
- ✅ Unique (user, role) pair
- ✅ User must exist and be active
- ✅ Role must exist

---

## Indexes and Performance

### Critical Indexes (Required for Performance)

| Table | Index | Purpose | Type |
|-------|-------|---------|------|
| User | email | Authentication lookups | Unique |
| User | is_active | Filter active users | Standard |
| TokenBlacklist | token_hash | Blacklist checks | Unique |
| TokenBlacklist | expires_at | Cleanup queries | Standard |
| Role | name | Role lookups | Unique |
| BusinessElement | name | Element lookups | Unique |
| AccessRoleRules | (role, element) | Permission lookups | Composite Unique |
| UserRole | (user, role) | Prevent duplicates | Composite Unique |
| UserRole | user | User's roles | Standard |

### Query Optimization Strategies

1. **Permission Checks:** Use select_related() for User → UserRole → Role joins
2. **Access Rules:** Use prefetch_related() for Role → AccessRoleRules → BusinessElement
3. **List Endpoints:** Always paginate (max 100 items per page)
4. **Caching:** Cache user permissions for 5 minutes
5. **Token Validation:** Cache token blacklist checks (negative cache)

---

## State Transitions

### User Account States

```
┌─────────────┐
│   CREATED   │ (New user registered)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   ACTIVE    │ (is_active=True, can login)
└──────┬──────┘
       │ soft_delete()
       ▼
┌─────────────┐
│  INACTIVE   │ (is_active=False, cannot login)
└─────────────┘
```

### Authentication Session States

```
┌──────────────┐
│ UNAUTHENTICATED │
└───────┬──────────┘
        │ login()
        ▼
┌──────────────┐
│ AUTHENTICATED │ (Valid JWT token)
└───────┬──────┘
        │
        ├─ logout() ─────────┐
        ├─ token_expires() ─┤
        └─ soft_delete() ────┤
                             ▼
                    ┌──────────────┐
                    │ UNAUTHENTICATED │
                    └──────────────┘
```

---

**Document Status:** ✅ Complete - All entities, relationships, and validation rules defined
