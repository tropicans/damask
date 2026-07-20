# Phase 14: HTTPS & Production Deployment Guide - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-20
**Phase:** 14-HTTPS & Production Deployment Guide
**Areas discussed:** Nginx Deployment Topology, Port Hardening, Cloudflare Tunnel Integration

---

## Nginx Deployment Topology

### Reverse Proxy Host Choice
| Option | Description | Selected |
|--------|-------------|----------|
| Host VPS | Run Nginx directly on the host VPS (simplifies SSL/Certbot) | |
| Containerized Nginx | Run Nginx inside a Docker container | ✓ |
| You decide | Let the agent choose based on standard practices | |

### Serving Frontend Assets
| Option | Description | Selected |
|--------|-------------|----------|
| Proxy to frontend container | Proxy requests to the frontend Docker container | ✓ |
| Serve from host | Build static assets and serve them directly via Nginx on the host | |
| You decide | Let the agent choose based on standard practices | |

### Static File Caching
| Option | Description | Selected |
|--------|-------------|----------|
| Custom cache headers | Cache static assets with long expiration, but check index.html | ✓ |
| Default Nginx caching | Use standard Nginx defaults | |
| You decide | Let the agent choose based on standard practices | |

---

## Port Hardening

### Production Port Bindings
| Option | Description | Selected |
|--------|-------------|----------|
| Bind to localhost | Bind Nginx port to 127.0.0.1 (prevents bypassing HTTPS) | ✓ |
| Expose on all interfaces | Bind Nginx to 0.0.0.0 | |
| You decide | Let the agent choose based on standard practices | |

### Firewall Instructions
| Option | Description | Selected |
|--------|-------------|----------|
| Document firewall rules | Document setting up UFW for SSH (22) only, keeping standard web ports closed | ✓ |
| No firewall rules | Keep the guide focused solely on Docker/Nginx | |
| You decide | Let the agent choose based on standard practices | |

### Database Backups
| Option | Description | Selected |
|--------|-------------|----------|
| pg_dump in Docker | Document running pg_dump via docker exec | ✓ |
| Expose DB port | Expose port 5432 to 127.0.0.1 for host-level tools | |
| Do not document | Leave backups out of scope | |
| You decide | Let the agent choose based on standard practices | |

---

## Cloudflare Tunnel Integration

### SSL and Ingress Ingestion
| Option | Description | Selected |
|--------|-------------|----------|
| Cloudflare Tunnel | Terminate SSL at Cloudflare Edge and route internally via existing CT daemon | ✓ |
| Host Certbot / Let's Encrypt | Install Certbot and handle TLS directly on the VPS host | |
| You decide | Let the agent choose based on standard practices | |

---

## the agent's Discretion
- Local Nginx config details for caching headers.
- Formatting and layout of the deployment guide.
- Cron backups setup details.

## Deferred Ideas
- None — discussion stayed within phase scope.

---

*Phase: 14-https-production-deployment-guide*
*Discussion log generated: 2026-07-20*
