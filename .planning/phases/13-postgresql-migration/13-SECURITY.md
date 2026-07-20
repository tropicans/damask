---
phase: 13
slug: postgresql-migration
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-20T04:55:00Z
---

# Phase 13 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Docker Network | Isolation of database traffic from the host network | Database queries and raw user data (PII) |
| Client-Server boundary | External HTTPS requests from users/browsers to API/Frontend | JWT session cookies and user requests |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-13-01 | Information Disclosure | PostgreSQL DB | high | mitigate | Database port 5432 is not exposed to the host system in `docker-compose.prod.yml`. Access is restricted to the internal network. | closed |
| T-13-02 | Information Disclosure | Configuration | high | mitigate | Secret configuration keys (`POSTGRES_PASSWORD`, `JWT_SECRET_KEY`) are externalized in `.env.example` and parameterized in `docker-compose.prod.yml` to prevent secret leakage in version control. | closed |
| T-13-03 | Tampering / Info Leak | Session Management | high | mitigate | Session cookies are configured with `COOKIE_SECURE: "true"` in the backend environment within `docker-compose.prod.yml` to enforce HTTPS transmission. | closed |
| T-13-04 | Information Disclosure | Network | medium | mitigate | Only frontend (`5173`) and API (`8000`) ports are exposed to the host. Internally, services communicate through a private docker network bridge. | closed |

*Status: open · closed · open — below {block_on} threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-20 | 4 | 4 | 0 | Antigravity |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-20
