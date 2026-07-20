# Phase 13: PostgreSQL Migration - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 13 implements the transition of the primary production database from SQLite to PostgreSQL:
1. **PostgreSQL Compatibility:** Supporting PostgreSQL as the primary database in the backend, configured via `DATABASE_URL` in `.env`.
2. **Production Docker Compose:** Creating a `docker-compose.prod.yml` with a PostgreSQL service, persistent volumes, and a database health check.
3. **Automated Verification:** Ensuring all 54+ tests pass against a PostgreSQL instance (while keeping SQLite as the default for local development).

</domain>

<decisions>
## Implementation Decisions

### PostgreSQL Connectivity
- **D-01:** Add `psycopg2-binary` to the python dependencies in `backend/pyproject.toml`. This is a pre-compiled version of the PostgreSQL driver, avoiding compilation errors on developer machines and in Docker images.

### Test Database Strategy
- **D-02:** Centralize the `session` and `client` fixtures in `backend/app/tests/conftest.py`, removing duplicate fixture code from all individual test files (e.g., `test_admin.py`, `test_auth.py`, etc.).
- **D-03:** The centralized `session` fixture will use SQLite in-memory (`sqlite://`) by default to maintain zero-config local testing. If a `TEST_DATABASE_URL` environment variable is provided, the fixture will dynamically create the engine for that database (enabling full test runs against a PostgreSQL database).

### Database Startup & Readiness
- **D-04:** Add a connection retry/wait loop in `backend/app/db.py` inside (or called by) `init_db()` to wait for the database service to be ready before calling `SQLModel.metadata.create_all(engine)`. The loop will retry up to 5 times with a 2-second delay.

### Environment Configuration & Docker Compose
- **D-05:** Create a `docker-compose.prod.yml` at the project root defining the production backend, frontend, and a PostgreSQL service.
- **D-06:** The PostgreSQL service in `docker-compose.prod.yml` will define a persistent volume `postgres_data` and a `healthcheck` command (e.g. using `pg_isready`).
- **D-07:** Create template environment files `backend/.env.example` and `frontend/.env.example` in their respective directories.
  - `backend/.env.example` will document development SQLite URLs and production PostgreSQL connection string formats.

### the agent's Discretion
- All choices follow the recommended options select by the user.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- `.planning/ROADMAP.md` — Phase 13 goal, success criteria, and dependencies.
- `.planning/REQUIREMENTS.md` — Requirements PROD-08, PROD-09.

### Database Setup & Entry Points
- `backend/app/db.py` — Engine setup, database initialization, and session generator.
- `backend/app/main.py` — Startup handler triggering database initialization.
- `backend/pyproject.toml` — Python package dependencies (poetry/uv).

### Testing Configuration
- `backend/app/tests/conftest.py` — Location for centralizing database and client fixtures.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/db.py`: The check `settings.DATABASE_URL.startswith("sqlite")` will be reused to conditionally handle SQLite-specific settings (like `check_same_thread` or foreign key pragmas) and default to standard parameters for PostgreSQL.
- `backend/app/tests/conftest.py`: Already contains standard pytest fixtures and can be expanded to house the centralized `session` and `client` fixtures.

### Established Patterns
- **Sync connection:** The backend utilizes synchronous database operations and transactions (`Session(engine)`), meaning a synchronous database adapter is required.

### Integration Points
- `backend/pyproject.toml`: Add `psycopg2-binary` dependency.
- `backend/app/db.py`: Implement the retry/wait connection logic.
- `backend/app/tests/conftest.py`: Houses the centralized fixtures. Individual test files will have their duplicate `session` and `client` fixtures removed so they inherit them from `conftest.py` automatically.
- `docker-compose.prod.yml` [NEW]: Production compose environment.
- `backend/.env.example` [NEW]: Environment variables template for the backend.
- `frontend/.env.example` [NEW]: Environment variables template for the frontend.

</code_context>

<specifics>
## Specific Ideas

- None — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 13-PostgreSQL Migration*
*Context gathered: 2026-07-20*
