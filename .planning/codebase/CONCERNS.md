# Codebase Concerns

**Analysis Date:** 2026-07-20

## Tech Debt

**Deprecated FastAPI `on_event` handlers:**
- Issue: FastAPI startup tasks are registered using the deprecated `@app.on_event("startup")` syntax.
- File: `backend/app/main.py` (line 114)
- Why: Retained from earlier templates.
- Impact: Deprecation warnings on application startup; will be removed in future FastAPI releases.
- Fix approach: Refactor startup and shutdown logic into a unified lifespan event handler using `asynccontextmanager`.

**Pydantic v2 Deprecation in Models:**
- Issue: `class Config` is used for model configuration instead of the new Pydantic v2 `model_config` / `ConfigDict`.
- File: `backend/app/models/user.py` (line 39)
- Why: Written using older Pydantic patterns.
- Impact: Deprecation warnings raised by Pydantic during runtime.
- Fix approach: Import `ConfigDict` and define `model_config = ConfigDict(...)` instead of nested configuration classes.

**In-memory brute-force tracking:**
- Issue: Brute force attempts are tracked using an in-memory dictionary (`_failed_attempts`) instead of a database table or Redis cache.
- File: `backend/app/services/auth.py` (line 9)
- Why: Simple state implementation without requiring persistent store overhead for temporary lockouts.
- Impact: If the server restarts, all failed attempts and lockout states are cleared. Does not scale across multiple backend instances.
- Fix approach: Move lockout tracking to a persistent table in SQLite/PostgreSQL.

## Known Bugs

- None currently identified.

## Security Considerations

**Memory buffer leaks on unhandled exceptions:**
- Risk: If file processing fails midway due to a corrupted DataFrame, memory buffers (`io.BytesIO`) could remain referenced in memory, leading to high RAM consumption or potential data leaks in heap.
- File: `backend/app/api/endpoints/mask.py` (upload processing block)
- Current mitigation: Basic try/except blocks exist, but no explicit `finally: buffer.close()` cleanup for all edge cases.
- Recommendations: Implement context managers or explicit `try...finally` clauses to ensure all `BytesIO` streams are closed immediately after processing completes.

**Lack of Rate Limiting on Authentication Endpoints:**
- Risk: Brute force and credential stuffing attacks on `/api/auth/login` and `/api/auth/register`.
- File: `backend/app/main.py`
- Current mitigation: In-memory account lockout after 5 attempts.
- Recommendations: Apply rate-limiting decorators (`slowapi`) directly to auth endpoints to throttle request rates.

## Performance Bottlenecks

**Large Excel/CSV parsing in Pandas:**
- Problem: Parsing files up to 50MB into memory as DataFrames can block the single-threaded Python event loop for several seconds.
- File: `backend/app/services/parser.py`
- Measurement: Processing a 50MB Excel file can take 5+ seconds and consume up to 250MB–500MB of RAM during DataFrame generation.
- Cause: Pandas reads the entire file synchronously into memory.
- Improvement path: Run file parsing tasks in a background executor (thread/process pool) using `anyio.to_thread.run_sync` to prevent blocking the FastAPI event loop.

## Fragile Areas

**Pandas/openpyxl engine parsing:**
- File: `backend/app/services/parser.py`
- Why fragile: Expects files to have well-formed structures. Inconsistent columns, malformed headers, or binary corruption will throw raw parsing exceptions.
- Common failures: `pd.read_excel` crashes on invalid openpyxl formats.
- Safe modification: Add comprehensive schema checks and sanitize column headers before processing.
- Test coverage: Partially tested in `test_masker.py`.

## Scaling Limits

**File Processing Size limit:**
- Current capacity: Max 50MB files (configured via endpoint validations).
- Limit: Memory limits of the hosting container. Multiple concurrent uploads of 50MB files can trigger Out-Of-Memory (OOM) kills.
- Symptoms at limit: Container crashes, 502 Bad Gateway responses.
- Scaling path: Migrate to async chunk-based processing or offload heavy data processing tasks to Celery workers.

## Dependencies at Risk

**passlib:**
- Risk: `passlib` is largely unmaintained (last release in 2020) and has compatibility warnings with bcrypt and Python 3.12+.
- Impact: Authentication and password hashing logic could break in future Python versions.
- Migration plan: Transition to using standard library `hashlib` or direct `bcrypt` package calls.

## Missing Critical Features

**Lack of database-driven session revocation:**
- Problem: Users cannot be logged out from other sessions; no way to deactivate JWT tokens before expiration.
- Current workaround: Tokens expire after fixed duration.
- Blocks: Security compliance requirements for instant credential revocation.
- Implementation complexity: Low (add token blacklist table).

## Test Coverage Gaps

**Frontend Test Suite:**
- What's not tested: The entire React user interface (components, hooks, axios API client integration).
- Risk: UI regressions or state updates could break upload/preview/download flows without warning.
- Priority: High.
- Difficulty to test: Requires setting up Vitest, React Testing Library, and MSW (Mock Service Worker) for API stubbing.

---

*Concerns audit: 2026-07-20*
*Update as issues are fixed or new ones discovered*
