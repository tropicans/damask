# Coding Conventions

**Analysis Date:** 2026-07-20

## Naming Patterns

### Files
- **Backend:** `snake_case.py` for all modules, controllers, models, and services (e.g., `auth_service.py`, `process_file()`).
- **Frontend Components:** `PascalCase.tsx` / `PascalCase.ts` for React UI components (e.g., `LoginPage.tsx`, `ToastNotification.tsx`).
- **Frontend Utilities:** `camelCase.ts` for hooks and scripts (e.g., `useAuth.ts`).
- **Configurations:** `kebab-case.*` for tool and environment config files (e.g., `vite.config.ts`, `tailwind.config.js`).

### Functions & Methods
- **Backend (Python):** `snake_case` for all function and method names (e.g., `get_db_session()`, `verify_password()`).
- **Frontend (TS/JS):** `camelCase` for functions (e.g., `fetchPreviewData()`, `handleUpload()`).

### Variables & Constants
- **Variables:** `snake_case` in Python, `camelCase` in TS/JS.
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE_MB = 50`, `ACCESS_TOKEN_EXPIRE_MINUTES`).

### Classes & Types
- **Classes:** `PascalCase` in both Python and TS/JS (e.g., `DataMasker`, `UserAuth`).
- **TypeScript Interfaces/Types:** `PascalCase` with explicit property declarations; avoid using `any` type.

## Code Style

### Python (Backend)
- Follow PEP 8 guidelines.
- Use Black format (line length 88 or 100 characters).
- Type hints are required on all function parameters and return values (e.g., `def mask_data(df: pd.DataFrame, rules: dict) -> bytes:`).

### TypeScript/React (Frontend)
- Prettier auto-formatting (2-space tabs, single quotes, trailing commas, semicolons).
- ESLint with TypeScript recommendation rules enabled.

## Import Organization

### Python (Backend)
Group imports with a single blank line between groups in the following order:
1. Standard library imports (e.g. `import io`, `import logging`).
2. Third-party library imports (e.g. `from fastapi import APIRouter`, `import pandas as pd`).
3. Local application imports (e.g. `from app.core.config import settings`).

### TypeScript/React (Frontend)
Group imports in the following order:
1. React core, hooks, and React-related library packages.
2. Third-party package imports (e.g. `axios`, `lucide-react`).
3. Local component, hooks, and api imports.
4. Stylesheets and asset imports.

## Error Handling

### Backend (Python)
- Use FastAPI `HTTPException` for standard API responses (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden).
- Wrap file-handling operations in try/except blocks and raise custom service-level exceptions (e.g., `FileProcessingError`) to prevent raw pandas or SQLAlchemy errors from escaping.
- Return structured error JSON models containing descriptive user error messages.

### Frontend (React)
- Wrap API calls in try-catch structures inside hooks or controller functions.
- Catch API errors and display elegant Toast UI notices or alert states, rather than crashing the page flow.
- Use React error boundaries where appropriate to isolate rendering failures.

## Logging

### Framework
- Python standard `logging` library configured in `app/core/logging.py`.
- Output is sent to standard stdout/stderr streams.

### Patterns
- Log incoming masking jobs (size, row count, column mappings) at `INFO` level.
- Log parsing errors or file upload failures at `ERROR` level with full stack trace.
- Never write console logs or raw `print` statements in production code.

---

*Convention analysis: 2026-07-20*
*Update when patterns change*
