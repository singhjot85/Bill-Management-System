# Authentication Architecture

## Purpose
Details the authentication mechanisms and policies within the Bill Management Application (BMA).

## Key Concepts
- **TokenAuthentication**: Primarily used for API-driven client communication (such as the Vue 3 SPA). Clients include the token in the `Authorization: Token <token_key>` header.
- **SessionAuthentication**: Used for standard session-based web requests and viewsets that rely on cookies.
- **Tenant Isolation**: Authentication resides within each tenant's context, resolving user permissions against the active schema.
- **AuthViewSet Deprecation**: The local viewset has been deprecated in favor of `dj_rest_auth` endpoints.

## Configuration
- `REST_FRAMEWORK` default settings:
  - `DEFAULT_AUTHENTICATION_CLASSES`: Enables `TokenAuthentication` and `SessionAuthentication`.
  - `DEFAULT_PERMISSION_CLASSES`: Enables `AllowAny` by default (viewsets must explicitly restrict access).

## Testing
- Tests are located at `backend/tests/tenants/test_auth.py`.
- Run using:
  ```bash
  pytest tests/tenants/test_auth.py
  ```

## Related Documentation
- [Multi-Tenancy Guide](./multi-tenancy.md)
- [Tenants Readme](../../backend/apps/tenants/Readme.md)
