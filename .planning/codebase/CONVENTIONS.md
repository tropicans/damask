# Coding Conventions & Development Guidelines

**Mapped Date:** 2026-07-20

## Naming Conventions

### Python Backend
- **Modules & Files:** `snake_case` (`auth_service.py`, `masker.py`, `db.py`)
- **Classes:** `PascalCase` (`User`, `MaskingJob`, `FakeNameStrategy`)
- **Functions & Methods:** `snake_case` (`hash_password()`, `verify_password()`, `record_failed_attempt()`)
- **Constants:** `UPPER_SNAKE_CASE` (`MAX_FILE_SIZE_MB = 50`, `INVITE_EXPIRE_HOURS = 24`)

### TypeScript / React Frontend
- **React Components:** `PascalCase` (`App.tsx`, `AuthForm.tsx`, `AuditDashboard.tsx`)
- **Utilities & API Client Modules:** `camelCase` / `kebab-case` (`formatError.ts`, `client.ts`, `auth.ts`)
- **Functions & Hooks:** `camelCase` (`getCurrentUser()`, `extractErrorMessage()`, `handleAuthSuccess()`)
- **Interfaces & Types:** `PascalCase` (`UserResponse`, `InviteResponse`, `PasswordStrength`)

## Code Style & Formatting Rules

### Python
- Follow PEP 8 guidelines.
- Mandatory type hints on function arguments and return values (`def hash_password(password: str) -> str:`).
- Document docstrings describing purpose, arguments, and return types for all endpoints and service functions.

### TypeScript / React
- Functional React components with hooks.
- Explicit TypeScript interface/type definitions for all API request and response bodies.
- Prettier auto-formatting (2 spaces, single quotes).
- Safe error text handling: Use `extractErrorMessage(err)` when catching Axios errors before passing error messages to React state to prevent `Objects are not valid as a React child` crashes on FastAPI 422 validation objects.

## Error Handling & Exception Management

### Backend
- Use FastAPI `HTTPException` with explicit HTTP status codes (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity, 423 Locked).
- Catch custom domain exceptions (`AuthException`) with custom exception handlers in `backend/app/main.py`.
- Delete session cookie (`secure_data_session`) automatically when responding with 401 Unauthorized.

### Frontend
- Global Axios response interceptor in `frontend/src/api/client.ts` triggers a global 401 callback to reset user state to `null`.
- Display user-friendly error banners with `extractErrorMessage()` parsing.

## Logging Practices

- Use Python standard `logging` library configured via `app.core.logging.setup_logging()`.
- Log incoming masking jobs, invite creations, and user status changes at `INFO` level.
- Log failed authentication attempts and security lockouts at `WARNING` or `INFO` level with client IP addresses.
- Avoid using `print()` statements in backend production code.
