# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v5.0 — production readiness

**Shipped:** 2026-07-20
**Phases:** 4 | **Plans:** 10 | **Sessions:** 3

### What Was Built
- **Invite-only Registration & Auth Policy (PROD-AUTH)**: Implemented invite-only registration where registration requires a valid admin-generated invite token. Added a real-time password strength indicator in the UI and enforced password complexity rules on both backend and frontend. Added temporary account lockout (15 minutes) after 5 consecutive failed login attempts from the same IP.
- **User Management & Audit Trail (PROD-ADMIN)**: Created a User Management UI dashboard for administrators to view all users, demote/promote roles, and deactivate/activate accounts. Enhanced the audit trail to log all successful and failed logins, and integrated login history and failed attempts sub-tabs into the Audit Dashboard.
- **PostgreSQL Migration Support (PROD-DB)**: Migrated the database setup to support PostgreSQL for production while keeping SQLite for local development. Integrated connection health checks and automated database initialization retry loops to wait for database availability.
- **Production Reverse Proxy & Deployment (PROD-DEPLOY)**: Configured containerized Nginx reverse proxy routing `/api` to the backend and `/` to the frontend, applying port hardening bound to localhost. Authored a bilingual production deployment guide `docs/DEPLOYMENT-PROD.md` covering SSL setup, Certbot renewal, backups, and firewall configurations.

### What Worked
- PostgreSQL migration using SQLModel and connection retry helpers made database container initialization robust during docker-compose startup.
- Multi-stage Nginx configuration bound exclusively to localhost prevented external direct access to app ports, satisfying host-level hardening constraints.

### What Was Inefficient
- Not having a globally installed node/npm command line on the host environment required manual task automation rather than fully relying on the node-based GSD CLI tool.

### Patterns Established
- Multi-container isolation where only Nginx is exposed, with backend and database services residing entirely in internal docker networks.
- Database retry loops on startup to manage multi-container startup orchestration without orchestration tools like Kubernetes.

### Key Lessons
1. Lockouts and password policy are critical application-level security controls, but Nginx/VPS-level firewalls (like fail2ban) are recommended for network-level mitigation.
2. Production database migrations should always be validated using containerized integration tests before writing deployment configs.

### Cost Observations
- Model mix: 100% Gemini 3.5 Flash (Medium)
- Sessions: 3
- Notable: Clean division of backend service tests made PostgreSQL migration validation straightforward.

---

## Milestone: v3.0 — secured the app

**Shipped:** 2026-07-19
**Phases:** 3 | **Plans:** 6 | **Sessions:** 6

### What Was Built
- **Cookie-based Session Authentication (SEC-AUTH)**: Moved JWT access token storage from client LocalStorage to secure HttpOnly cookies, verified JWT from cookies, and implemented clean cookie removal on logout.
- **Double Submit Cookie CSRF Protection (SEC-CSRF)**: Implemented Double-Submit Cookie CSRF protection for all POST, PUT, and DELETE routes on the backend. Created Axios request interceptor on the frontend to automatically attach the CSRF token from cookie to the request header.
- **Secure Headers & API Rate Limiting**: Added global HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.) and registered rate limits via `slowapi` on authentication (5/min) and file processing (10/min) routes.
- **Input Hardening & Role Authorization**: Hardened file upload validation with strict MIME-type and 50MB file size checks using chunked streaming before reading into memory. Restricted audit logging and dashboard access to `admin` and `auditor` roles.

### What Worked
- Rebuilding containers and running Pytest inside the backend Docker container ensured that all tests were clean and reproducible in a production-like environment.
- Using Python's chunked file streaming allowed checking the content length and MIME-types early, preventing large payloads from consuming server resources.

### What Was Inefficient
- The `pytest` execution path on Windows sometimes had import path issues due to the Docker root path, which required configuring `pythonpath = ["."]` in `pyproject.toml` to resolve module import issues.

### Patterns Established
- Secure cookies and CSRF headers in Axios client configuration for all API interactions.
- Global middleware configuration for unified HTTP security headers.

### Key Lessons
1. Always secure JWTs using HttpOnly cookies to prevent XSS-based token theft.
2. In-memory pandas operations should be preceded by strict input file stream checks (size and MIME-type validation) to prevent Denial of Service (DoS) attacks on single-threaded FastAPI workers.

### Cost Observations
- Model mix: 100% Gemini 3.5 Flash (Medium)
- Sessions: 6
- Notable: Fast local verification execution inside Docker.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 4 | 4 | Initial MVP and local storage authentication |
| v2.0 | 1 | 1 | Added complete documentation suite |
| v3.0 | 6 | 3 | Full application security hardening and rate limiting |
| v5.0 | 3 | 4 | Production-readiness audit, admin user management, PostgreSQL migration, Nginx configurations |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v3.0 | 26 | 100% | 0 |
| v5.0 | 54 | 100% | 0 |

### Top Lessons (Verified Across Milestones)

1. Keep pandas uploads strictly in-memory using BytesIO to prevent temporary raw data leakage.
2. Store auth tokens in HttpOnly SameSite cookies to protect the application from client-side token leakage.
3. Configure multi-container Docker deployment with Nginx proxying internal services to restrict host exposure.
