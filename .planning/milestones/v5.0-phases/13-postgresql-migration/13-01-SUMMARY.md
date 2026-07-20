---
phase: 13-postgresql-migration
plan: 13-01
subsystem: database
tags: [postgres, sqlite, pytest, psycopg2-binary, sqlmodel]

requires:
  - phase: 12-user-management-audit-trail
    provides: [user database tables, admin access rules]
provides:
  - psycopg2-binary dependency for postgresql connection support
  - database connection retry and wait loop in db.py
  - centralized session and client fixtures in conftest.py supporting switchable databases
affects: [production deployment, integration tests]

tech-stack:
  added: [psycopg2-binary]
  patterns: [database connection retry, centralized pytest fixtures]

key-files:
  created: []
  modified: [backend/pyproject.toml, backend/app/db.py, backend/app/tests/conftest.py, backend/app/tests/test_admin.py, backend/app/tests/test_auth.py, backend/app/tests/test_input_hardening.py, backend/app/tests/test_invite.py, backend/app/tests/test_jobs.py, backend/app/tests/test_mask_zip.py, backend/app/tests/test_rate_limits.py, backend/app/tests/test_role_auth.py, backend/app/tests/test_revert_endpoint.py]

key-decisions:
  - "Centralized session and client fixtures in conftest.py and enabled TEST_DATABASE_URL environment variable to allow running tests against PostgreSQL in CI."

patterns-established:
  - "Database connection wait: wait up to 5 retries with 2s delay to allow database server startup in Docker compose environments."

requirements-completed: [PROD-08]

coverage:
  - id: D1
    description: "psycopg2-binary dependency added under [tool.poetry.dependencies]"
    requirement: "PROD-08"
    verification:
      - kind: other
        ref: "pip show psycopg2-binary"
        status: pass
    human_judgment: false
  - id: D2
    description: "_wait_for_db connection loop helper in db.py"
    requirement: "PROD-08"
    verification:
      - kind: integration
        ref: "backend/app/tests/conftest.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "Centralized session and client fixtures in conftest.py with switchable DB support"
    requirement: "PROD-08"
    verification:
      - kind: integration
        ref: "pytest -v"
        status: pass
    human_judgment: false
  - id: D4
    description: "Removed duplicate fixtures from 9 test modules"
    requirement: "PROD-08"
    verification:
      - kind: integration
        ref: "pytest -v"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-07-20T04:07:00Z
status: complete
---

# Phase 13 Plan 1: PostgreSQL Compatibility & Centralized Test Fixtures

**Added `psycopg2-binary` PostgreSQL driver, implemented database connection wait/retry loop in `init_db()`, and centralized switchable test fixtures in `conftest.py`.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-07-20T11:00:00+07:00
- **Completed:** 2026-07-20T11:10:00+07:00
- **Tasks:** 5
- **Files modified:** 12

## Accomplishments
- Added `psycopg2-binary` dependency for PostgreSQL database connection support.
- Added database connection wait and retry loop (`_wait_for_db()`) to handle database container startup delays.
- Centralized the duplicated `session` and `client` fixtures from 9 test files into a single `conftest.py` file with support for switchable DB engines via `TEST_DATABASE_URL` env var.
- Removed duplicate test fixtures and imports across the entire test suite.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add `psycopg2-binary` dependency** - `647be03` (feat)
2. **Task 2: Add connection retry loop in `db.py`** - `b7be4bd` (feat)
3. **Task 3: Centralize `session` and `client` fixtures in `conftest.py`** - `3d8d8e8` (refactor)
4. **Task 4: Remove duplicate `session` and `client` fixtures from test files** - `ebbcef1` (refactor)

## Files Created/Modified
- `backend/pyproject.toml` - Added `psycopg2-binary` dependency
- `backend/app/db.py` - Implemented `_wait_for_db()` retry helper
- `backend/app/tests/conftest.py` - Created centralized fixtures
- `backend/app/tests/test_admin.py` - Removed duplicate fixtures
- `backend/app/tests/test_auth.py` - Removed duplicate fixtures
- `backend/app/tests/test_input_hardening.py` - Removed duplicate fixtures
- `backend/app/tests/test_invite.py` - Removed duplicate fixtures
- `backend/app/tests/test_jobs.py` - Removed duplicate fixtures
- `backend/app/tests/test_mask_zip.py` - Removed duplicate fixtures
- `backend/app/tests/test_rate_limits.py` - Removed duplicate fixtures
- `backend/app/tests/test_role_auth.py` - Removed duplicate fixtures
- `backend/app/tests/test_revert_endpoint.py` - Removed duplicate fixtures

## Decisions Made
- Centralized the database test fixtures to support running tests against PostgreSQL in the future by setting the `TEST_DATABASE_URL` environment variable.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None - test suite passed completely with zero regressions.

## User Setup Required
None.

## Next Phase Readiness
Ready for the next plan: 13-02-PLAN.md to create production Docker Compose configuration and environment templates.
