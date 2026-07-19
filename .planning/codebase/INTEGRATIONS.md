# External Integrations

**Analysis Date:** 2026-07-19

## APIs & External Services

**Data Generating / Synthesis (Planned):**
- Faker (Python Library) - Used for generating random localized names, emails, and phone numbers for masking.
- Pandas / Openpyxl (Python Libraries) - Used to parse and output Excel and CSV file streams.

## Data Storage

**Databases:**
- SQLite (Development) / PostgreSQL (Production)
  - Connection: via `DATABASE_URL` env var
  - Client: SQLAlchemy / SQLModel ORM
  - Migrations: Alembic in backend/migrations/

**File Storage:**
- InMemoryBuffer (RAM) - All uploaded CSV/XLSX files are processed in-memory.
- Buckets / Persistent Storage: None. (Design choice: Files are processed instantly and returned via stream to prevent sensitive data storage).

## Authentication & Identity

**Auth Provider:**
- Custom JWT (JSON Web Tokens) Implementation
  - Token storage: secure HttpOnly Cookies (recommended) or localStorage
  - Encryption: HS256 algorithm with passlib/bcrypt for password hashing

## Monitoring & Observability

**Logs:**
- Standard stdout/stderr logging formatted for container runtimes (e.g. JSON logging)
- Audit log entries: Saved to the SQLite/PostgreSQL database to record masking job metadata (filename, row count, processed columns).

## CI/CD & Deployment

**Hosting:**
- Docker Compose for local development (FastAPI backend + React frontend)
- Production hosting (Planned):
  - Frontend SPA: Vercel or static hosting
  - Backend: Dockerized on AWS ECS, Railway, or similar container hosting platform

**CI Pipeline:**
- GitHub Actions - Automated testing (pytest, vitest) and Docker builds

## Environment Configuration

**Development:**
- Required env vars:
  - `DATABASE_URL`: Connection string for SQLite/PostgreSQL
  - `JWT_SECRET_KEY`: Private key for signing tokens
  - `BACKEND_URL`: URL of the FastAPI backend for frontend requests
- Secrets location: `.env` file (gitignored)

**Production:**
- Secrets management: Environment variables injected via container management platform (e.g., ECS task definition, Railway dashboard)

---

*Integration audit: 2026-07-19*
*Update when adding/removing external services*
