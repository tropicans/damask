# Phase 14: HTTPS & Production Deployment Guide - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 14 delivers a secure production deployment model and documentation optimized for containerization and Cloudflare Tunnel ingress:
1. **Production Deployment Guide:** A detailed guide (`docs/DEPLOYMENT-PROD.md`) covering VPS setup, Docker Compose deployment, port hardening, firewall configuration, and integration with an existing Cloudflare Tunnel.
2. **Template Nginx Configuration:** A ready-to-use Nginx configuration template (`nginx/nginx.conf`) running inside Docker as a local reverse proxy to forward traffic to backend and frontend containers.

</domain>

<decisions>
## Implementation Decisions

### Nginx Deployment Topology
- **D-01:** Run Nginx inside a Docker container (as a service in `docker-compose.prod.yml`) to serve as the single entrypoint for the Docker network.
- **D-02:** Nginx will route `/api` to the `backend` service and all other traffic to the `frontend` service using Docker internal service names.
- **D-03:** Nginx will cache frontend static assets (JS, CSS, images) with long expiration, but configure `index.html` to check for updates (`Cache-Control: no-cache`).

### Port Hardening & Ingress
- **D-04:** Only the `nginx` service port (e.g., `80` or `8080`) will be exposed to the host, and it must be bound to localhost (`127.0.0.1:80:80`). The `frontend` and `backend` container ports will NOT be exposed to the host directly.
- **D-05:** Document host-level firewall rules in `docs/DEPLOYMENT-PROD.md` (e.g., using UFW) to allow only SSH on port 22. Inbound HTTP (80) and HTTPS (443) are NOT exposed on the host since the existing Cloudflare Tunnel connects outbound.
- **D-06:** Document database backups using `pg_dump` executed inside the PostgreSQL Docker container, avoiding exposing port 5432 to the host or internet.

### SSL & Cloudflare Tunnel
- **D-07:** Do NOT configure Let's Encrypt / Certbot or local SSL certificates on Nginx. SSL/TLS is terminated at the Cloudflare edge, and secure local ingress is handled by the user's existing Cloudflare Tunnel agent.
- **D-08:** Document how to point the user's existing Cloudflare Tunnel configuration to the local Nginx gateway (`http://localhost:80` or `http://localhost:8080`).

### the agent's Discretion
- Exact choice of host port for Nginx (default to port 80).
- Detailed formatting and layout of `docs/DEPLOYMENT-PROD.md`.
- Cron syntax templates for PostgreSQL backups.

</decisions>

<specifics>
## Specific Ideas

- Nginx container acts as a local HTTP reverse proxy routing `/api` to `http://backend:8000` and `/` to `http://frontend:5173`.
- The existing Cloudflare Tunnel daemon points to the exposed port of the Nginx container on localhost.

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
- `docker-compose.prod.yml` ports mapping can be cleaned up to only expose `nginx` service to the host.
- `backend/app/main.py` uses `/api` prefix for all routers.

### Established Patterns
- **Container network:** Services communicate internally using Docker dns names (`db`, `backend`, `frontend`).

### Integration Points
- `docker-compose.prod.yml`: Add `nginx` service and remove direct port mappings for `backend` and `frontend` on the host.
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
