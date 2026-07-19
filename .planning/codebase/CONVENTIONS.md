# Coding Conventions

**Analysis Date:** 2026-07-19

## Naming Patterns

**Python Files:**
- snake_case for all modules, variables, and functions (`auth_service.py`, `process_file()`).
- PascalCase for class definitions (`DataMasker`, `UserAuth`).
- UPPER_SNAKE_CASE for local/global constants (`MAX_FILE_SIZE_MB = 50`).

**React/TS Files:**
- PascalCase for React components and pages (`LoginPage.tsx`, `ToastNotification.tsx`).
- camelCase for utility functions, hooks, variables, and properties (`useAuth()`, `columnConfig`).
- kebab-case for config files, assets, and styling documents (`vite.config.ts`, `global-styles.css`).

## Code Style

**Python Style:**
- Follow PEP 8 guidelines.
- Use Black format (line length 88 or 100 characters).
- Type hints on all function parameters and return values:
  ```python
  def mask_column(data: list[str], strategy: str) -> list[str]:
  ```

**Frontend Style:**
- Prettier for auto-formatting (2-space tabs, single quotes, trailing commas, semicolons).
- ESLint with TypeScript recommendation rules enabled.
- Avoid using `any` type in TypeScript; always define explicit interfaces/types.

## Import Organization

**Python Import Order:**
1. Standard library imports (e.g. `os`, `sys`, `typing`)
2. Related third party imports (e.g. `fastapi`, `pandas`, `pydantic`)
3. Local application/library specific imports (e.g. `app.services.masker`)
*(Separate groups by single blank line)*

**React/TS Import Order:**
1. React core, hooks, and context
2. Third-party UI / icon / state libraries (`lucide-react`, `axios`)
3. Internal modules, pages, components, utils
4. Styles and assets

## Error Handling

**Backend Strategy:**
- Use HTTPException for standard API responses (e.g. 400 Bad Request, 401 Unauthorized).
- Wrap file-handling operations in try/catch blocks and raise custom service-level exceptions (e.g., `DataProcessingException`) to prevent raw pandas errors from escaping.
- Return structured error JSON models containing descriptive user error messages.

**Frontend Strategy:**
- Wrap API calls in try-catch structures inside hooks or controller functions.
- Catch API errors and display elegant Toast UI notices, rather than crashing page flow.

## Logging

- Use Python standard `logging` library configured in `app/core/logging.py`.
- Log incoming masking jobs (size, row count, column mappings) at `INFO` level.
- Log parsing errors or file upload failures at `ERROR` level with stack trace.
- Never write console logs or print statements in production code.

---

*Convention analysis: 2026-07-19*
*Update when patterns change*
