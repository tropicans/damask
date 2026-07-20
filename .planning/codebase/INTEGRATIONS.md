# External Integrations & Services

**Mapped Date:** 2026-07-20

## Database Systems

### SQLite (Development)
- **Path:** `backend/datamask.db`
- **Driver:** `sqlite3` via SQLModel / SQLAlchemy (`backend/app/db.py`)
- **Connection Configuration:** `check_same_thread=False`, `PRAGMA foreign_keys=ON`
- **Usage:** Local in-memory or persistent SQLite file storage for user management, audit logs, and invites.

### PostgreSQL (Production)
- **Driver:** `psycopg2-binary` (`backend/pyproject.toml`)
- **Container Service:** `db` in `docker-compose.prod.yml` (Image: `postgres:16-alpine`)
- **Database Name:** `securedata`
- **User:** `securedata_user`

## Authentication & Security Integrations

### Cookie-based Session Authentication
- **Cookie Name:** `secure_data_session`
- **Storage:** HttpOnly cookie issued on `/api/auth/login` or `/api/auth/register` (`backend/app/api/endpoints/auth.py`).
- **Token Format:** Signed JWT containing `user_id` and expiration (`backend/app/services/auth.py`).

### Double Submit CSRF Cookie Protection
- **Cookie Name:** `secure_data_csrf` (JS accessible, SameSite=Lax)
- **Request Header:** `X-CSRF-Token`
- **Middleware:** `CSRFMiddleware` in `backend/app/main.py` validates matching cookie and header on mutating HTTP methods (`POST`, `PUT`, `DELETE`, `PATCH`).

## Reverse Proxy & Container Infrastructure

### Nginx Reverse Proxy
- **Configuration:** `nginx/nginx.conf`
- **Host Port:** `80` (redirects / proxies to backend and frontend containers)
- **Production Compose:** `docker-compose.prod.yml`
- **Development Compose:** `docker-compose.yml` (Backend on `:8000`, Frontend on `:5173`)
