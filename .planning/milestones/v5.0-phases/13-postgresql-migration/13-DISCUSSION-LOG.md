# Phase 13: PostgreSQL Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-20
**Phase:** 13-PostgreSQL Migration
**Areas discussed:** PostgreSQL Driver Package, Test Database Strategy, Database Startup & Readiness, Environment Configuration & Docker Compose

---

## PostgreSQL Driver Package

| Option | Description | Selected |
|--------|-------------|----------|
| `psycopg2-binary` | Pre-compiled, highly compatible with SQLModel/SQLAlchemy and easy to install on Windows/Linux. | ✓ |
| `psycopg[binary] (v3)` | The newer PostgreSQL adapter, but could introduce compatibility edge cases with older SQLModel versions. | |
| `You decide` | Let Antigravity make the design choice. | |

**User's choice:** `psycopg2-binary`
**Notes:** Decided to use `psycopg2-binary` for compatibility, ease of installation, and robust sync execution.

---

## Test Database Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Centralized & Switchable Fixture | Centralize session/client fixtures in conftest.py, using SQLite in-memory by default and PostgreSQL if TEST_DATABASE_URL is provided. | ✓ |
| Strict SQLite-only Tests | Keep tests hardcoded to SQLite, and verify PostgreSQL compatibility only manually or via smoke tests. | |
| `You decide` | Let Antigravity make the design choice. | |

**User's choice:** Centralized & Switchable Fixture
**Notes:** Centralizing the fixtures will clean up code duplication in 9+ test files and make it simple to run all tests against a real PostgreSQL instance by setting `TEST_DATABASE_URL`.

---

## Database Startup & Readiness

| Option | Description | Selected |
|--------|-------------|----------|
| Connection Retry Loop | Add a retry helper in app/db.py (e.g. 5 retries, 2s delay) that waits for the DB to be ready before calling init_db() on startup. | ✓ |
| Strict Compose Ordering | Rely solely on Docker Compose health checks and depends_on: service_healthy to sequence startup, keeping the Python code simple. | |
| `You decide` | Let Antigravity make the design choice. | |

**User's choice:** Connection Retry Loop
**Notes:** Implementing retry logic in the backend provides resilience when deploying to environments where PostgreSQL startup might be delayed, preventing premature crashes.

---

## Environment Configuration & Docker Compose

| Option | Description | Selected |
|--------|-------------|----------|
| Directory-Level Env Templates + Root docker-compose.prod.yml | Create backend/.env.example and frontend/.env.example to match their respective runtimes, and add docker-compose.prod.yml in the root. | ✓ |
| Root-Level Single Env Template + Root docker-compose.prod.yml | Maintain a single .env.example at the project root for unified configuration, and add docker-compose.prod.yml in the root. | |
| `You decide` | Let Antigravity make the design choice. | |

**User's choice:** Directory-Level Env Templates + Root docker-compose.prod.yml
**Notes:** Directory-level `.env.example` templates align with the stack runtime separation (Python backend vs Node/Vite frontend), and the production-grade Docker Compose file will reside in the root.

---

## the agent's Discretion

No items were left to agent discretion.

## Deferred Ideas

No ideas were deferred during this discussion.
