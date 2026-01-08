# Constitutional Principles - Quick Reference

Quick lookup for constitutional requirements during development.

## Code Quality (Principle 1)

### Before You Code
- [ ] Plan your approach
- [ ] Consider type hints strategy

### While Coding
- [ ] Follow PEP 8 (88 char line length - Black standard)
- [ ] Add type hints to ALL functions/methods
- [ ] Keep functions simple (cyclomatic complexity < 10)
- [ ] Write docstrings (Google or NumPy style)

### Before Committing
- [ ] Run `ruff check .` - must pass
- [ ] Run `mypy .` - must pass
- [ ] Self-review for clarity and patterns
- [ ] Request code review (no self-merge!)

## Testing (Principle 2)

### Test Coverage Requirements
- Minimum 80% overall
- 95% for critical business logic
- 100% for security-sensitive code

### Test Types Required
- [ ] **Unit tests** - Core logic, validation, edge cases
- [ ] **Integration tests** - API endpoints, authentication, data flow
- [ ] **Performance tests** - Critical paths, query efficiency

### Test Quality
- [ ] Tests are isolated and repeatable
- [ ] Use fixtures/factories (no hard-coded data)
- [ ] Include regression tests for bug fixes
- [ ] Prefer real dependencies over mocks in integration tests

### Before Committing
- [ ] All tests pass locally
- [ ] Coverage meets minimums
- [ ] Tests are meaningful (not just hitting lines)

## User Experience (Principle 3)

### API Response Structure
```python
# Success
{
    "data": { ... },
    "meta": { "timestamp": "..." }
}

# Error
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Clear, actionable message",
        "details": []
    }
}
```

### HTTP Status Codes
- `200` - Success (GET, PUT, PATCH)
- `201` - Resource created (POST)
- `204` - Success with no content (DELETE)
- `400` - Bad request (validation errors)
- `401` - Unauthorized (auth required)
- `403` - Forbidden (insufficient permissions)
- `404` - Resource not found
- `500` - Server error

### Required Features
- [ ] Consistent JSON structure
- [ ] Clear error messages (no stack traces!)
- [ ] Pagination for lists (max 100 items/page)
- [ ] OpenAPI/Swagger documentation
- [ ] Semantic versioning for breaking changes

## Performance (Principle 4)

### Response Time Targets
- **95th percentile:** < 200ms
- **99th percentile:** < 500ms
- Operations > 500ms → background job

### Database Rules
- [ ] Add indexes for tables > 1000 rows
- [ ] NO N+1 queries (use `select_related`/`prefetch_related`)
- [ ] Implement pagination (never load all rows)
- [ ] Monitor query counts in tests

### Required Safeguards
- [ ] Rate limiting (default: 100 req/min per user)
- [ ] Timeouts on external calls (default: 5s)
- [ ] Circuit breakers for third-party APIs
- [ ] Efficient caching with proper headers
- [ ] Background jobs for slow operations

### Performance Testing
```python
# Example benchmark test
def test_api_performance(benchmark):
    result = benchmark(lambda: api_call())
    assert result.stats.mean < 0.2  # 200ms
```

## Pre-Commit Checklist

Use this before every commit:

```bash
# 1. Code Quality
ruff check .                    # Linting
mypy .                          # Type checking
# Review docstrings manually

# 2. Testing
pytest --cov=. --cov-report=term-missing
# Verify coverage ≥ 80%

# 3. Performance (if applicable)
pytest -k performance          # Run performance tests
# Check django-debug-toolbar for N+1 queries

# 4. Documentation
# Update OpenAPI docs if API changed
# Update README if behavior changed
```

## Common Violations

### ❌ Code Quality Violations
```python
# Missing type hints
def get_user(id):  # ❌
    return User.objects.get(id=id)

# No docstring
def complex_calculation(a, b, c):  # ❌
    ...
```

### ✅ Correct Approach
```python
def get_user(user_id: int) -> User:
    """
    Retrieve a user by ID.
    
    Args:
        user_id: The unique identifier of the user.
        
    Returns:
        User instance.
        
    Raises:
        User.DoesNotExist: If user not found.
    """
    return User.objects.get(id=user_id)
```

### ❌ Performance Violations
```python
# N+1 query problem
for order in Order.objects.all():  # ❌
    print(order.customer.name)  # Hits DB every iteration!

# No pagination
def list_users(request):  # ❌
    return User.objects.all()  # Could be millions!
```

### ✅ Correct Approach
```python
# Optimized query
orders = Order.objects.select_related('customer').all()
for order in orders:
    print(order.customer.name)  # No extra queries

# With pagination
from rest_framework.pagination import PageNumberPagination

class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
```

## When in Doubt

1. **Read the full constitution:** `.specify/memory/constitution.md`
2. **Check templates:** `.specify/templates/`
3. **Ask for code review:** Another pair of eyes catches issues
4. **Write tests first:** TDD ensures you meet requirements

---

**Remember:** Constitutional compliance is not optional. It ensures project quality, maintainability, and long-term success.
