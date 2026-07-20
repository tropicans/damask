# External Integrations

**Analysis Date:** 2026-07-20

## APIs & External Services

**Mock Data Generation:**
- Faker (Local Library) - In-process generation of localized mock names, emails, and phone numbers.
  - SDK/Client: `faker` python package
  - Auth: None (local generation)
  - Endpoints: Native calls to `fake.name()`, `fake.ascii_free_email()`, `fake.phone_number()`, etc.

## Data Storage

**Databases:**
- SQLite (Local Dev) - Lightweight local database for session and job metadata.
  - Connection: Connection string via `DATABASE_URL` env var (e.g. `sqlite:///./securedata.db`)
  - Client: SQLModel / SQLAlchemy ORM
  - Migrations: Managed via SQLModel schema creation on application startup
- PostgreSQL (Production) - Enterprise database.
  - Connection: `DATABASE_URL` env var (e.g. `postgresql://user:pass@host:port/db`)
  - Client: SQLModel / SQLAlchemy ORM
  - Migrations: Production migration steps documented in deployment guide

**File Storage:**
- RAM Buffer Storage - Strictly in-memory file buffers (`io.BytesIO`).
  - SDK/Client: Python standard library `io`
  - Policy: No files written to disk; output stream is sent directly to browser and immediately freed from RAM.

**Caching:**
- Local memory dictionary - Consistently scrambles/anonymizes IDs by caching generated mock values during a single masking session.
  - Client: Custom cache in `app/services/masker.py`

## Authentication & Identity

**Auth Provider:**
- Custom JWT Authentication - Stateless JSON Web Token authentication.
  - Implementation: FastAPI dependency injection with token verification in `app/services/auth.py`
  - Token storage: Cookie-based auth (httpOnly cookies) or LocalStorage (header-based)
  - Session management: Configured JWT expiration

## Monitoring & Observability

**Logs:**
- Python standard `logging` configured in `app/core/logging.py`.
  - Output: stdout/stderr (standard container output logging)
  - Log levels: `INFO` for job metadata, `ERROR` for parsing errors

## CI/CD & Deployment

**Hosting:**
- Docker - Dockerfiles exist for both frontend and backend to enable deployment via container hosting.
- Docker Compose - `docker-compose.yml` for coordinating frontend and backend containers locally.

## Environment Configuration

**Development:**
- Required env vars:
  - `DATABASE_URL`: Connection string for SQLModel database
  - `JWT_SECRET_KEY`: Secret key used to sign JWT tokens
  - `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed frontend origins (e.g., `http://localhost:5173`)
- Secrets location: `.env` file (gitignored)
- Mock/stub services: In-memory/local SQLite database

**Production:**
- Secrets management: Configured through hosting platform environment variables (e.g. Render, Railway, AWS ECS).

## Webhooks & Callbacks

- None.

---

*Integration audit: 2026-07-20*
*Update when adding/removing external services*
