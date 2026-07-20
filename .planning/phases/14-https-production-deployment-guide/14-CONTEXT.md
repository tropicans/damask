# Phase 14: HTTPS & Production Deployment Guide - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 14 delivers a secure production deployment model and documentation:
1. **Production Deployment Guide:** A detailed guide (`docs/DEPLOYMENT-PROD.md`) covering VPS setup, Docker install, Nginx reverse proxy configuration, SSL/TLS setup with Let's Encrypt (Certbot), SSL auto-renewal, and an environment variable checklist.
2. **Template Nginx Configuration:** A ready-to-use Nginx configuration template (`nginx/nginx.conf`) forwarding HTTPS traffic to the frontend and backend Docker containers.

</domain>

<decisions>
## Implementation Decisions

### Nginx Deployment Topology
- **D-01:** Install and run Nginx directly on the host VPS (not inside a Docker container) to simplify Let's Encrypt/Certbot setup and certificate path management.
- **D-02:** Nginx on the host VPS will proxy all frontend request traffic to the frontend Docker container.
- **D-03:** Nginx on the host will cache frontend static assets (JS, CSS, images) with long expiration, but configure `index.html` to check for updates (`Cache-Control: no-cache`).

### Port Hardening
- **D-04:** Bind the frontend and backend ports in `docker-compose.prod.yml` to localhost (`127.0.0.1:8000:8000` and `127.0.0.1:5173:5173`) to ensure all external traffic goes through Nginx HTTPS and cannot bypass the reverse proxy.
- **D-05:** Document host-level firewall rules in `docs/DEPLOYMENT-PROD.md` (e.g., using UFW) to allow only SSH on port 22, HTTP on port 80, and HTTPS on port 443.
- **D-06:** Document database backups using `pg_dump` executed inside the PostgreSQL Docker container, avoiding exposing port 5432 to the host or internet.

### Certbot SSL Auto-Renewal
- **D-07:** Install Certbot on the host VPS and manage auto-renewal via a systemd timer / cron job to easily reload the host Nginx service.
- **D-08:** Configure Nginx to serve the Let's Encrypt ACME challenge from a webroot directory on the host VPS for zero-downtime renewal.
- **D-09:** Document the generation of a custom 2048-bit Diffie-Hellman parameters file (`dhparam.pem`) and include it in the Nginx template to achieve an A+ SSL rating.

### the agent's Discretion
- Exact choice of strong cipher suites and TLS versions (default to modern TLS 1.2 and 1.3).
- Detailed formatting and layout of `docs/DEPLOYMENT-PROD.md`.
- Cron syntax templates for PostgreSQL backups.

</decisions>

<specifics>
## Specific Ideas

- Nginx routes `/api` to the backend Docker container (`http://127.0.0.1:8000`) and all other routes to the frontend container (`http://127.0.0.1:5173`).
- Diffie-Hellman parameter generation: `openssl dhparam -out /etc/nginx/dhparam.pem 2048`.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- `.planning/ROADMAP.md` — Phase 14 goals and success criteria.
- `.planning/REQUIREMENTS.md` — Requirements PROD-10, PROD-11.

### Container Configuration
- `docker-compose.prod.yml` — Base production Docker Compose environment configurations.
- `backend/Dockerfile` — Backend service packaging.
- `frontend/Dockerfile` — Frontend service packaging.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docker-compose.prod.yml` ports mapping can be updated to add `127.0.0.1:` prefix.
- `backend/app/main.py` uses `/api` prefix for all routers.

### Established Patterns
- **Container network:** Frontend container depends on backend container, and both run in a shared Docker bridge network.

### Integration Points
- `docker-compose.prod.yml`: Restrict exposed port bindings to localhost.
- `docs/DEPLOYMENT-PROD.md` [NEW]: Location of the production deployment guide.
- `nginx/nginx.conf` [NEW]: Location of the template Nginx configuration.

</code_context>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.

</deferred>

---

*Phase: 14-https-production-deployment-guide*
*Context gathered: 2026-07-20*
