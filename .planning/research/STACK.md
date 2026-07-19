# Stack Research

**Domain:** Application Security (FastAPI Backend + React Frontend)
**Researched:** 2026-07-19
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| FastAPI (existing) | ^0.110.0 | API Backend | High-performance framework supporting async middleware for security headers, rate limiting, and CORS. |
| React (existing) | 18.x | Frontend UI | Component-based UI. Needs to be configured to handle HttpOnly cookie-based JWT authentication and CSRF headers. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| slowapi | ^0.1.9 | Rate Limiting | Use to throttle API requests (specifically auth, upload, and dashboard endpoints) using memory or Redis backend. |
| pyjwt | ^2.13.0 | Token Generation | Sign and verify JWTs with a cryptographic key on backend. |
| itsdangerous | ^2.2.0 | CSRF Token Generation | Part of the Python standard-ish library (used by FastAPI/Starlette) to sign CSRF tokens in cookies. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Docker Compose | Development Sandbox | Configures containers for backend, frontend, and db, simulating local production-like environments with secure routing. |

## Installation

```bash
# Add slowapi rate limiter to poetry dependencies
cd backend
poetry add slowapi
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `slowapi` | Custom in-memory rate limiting middleware | If we want zero external dependencies and very lightweight rate limiting. |
| HttpOnly Cookie + CSRF | LocalStorage + Bearer Auth | LocalStorage is simpler to implement but insecure against XSS attacks. Cookie-based storage is mandatory for security. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| LocalStorage for JWTs | Vulnerable to Cross-Site Scripting (XSS) attacks. If XSS occurs, credentials can be stolen. | HttpOnly, Secure, SameSite=Lax cookies. |
| CORS Wildcard (`*`) | Allows any domain to read responses, violating the browser's Same-Origin Policy when credentials (cookies) are sent. | Restricted whitelist of allowed origins. |

## Stack Patterns by Variant

**If deployed locally (localhost):**
- Secure flag on HttpOnly cookies can be disabled or handled by the browser (browsers permit Secure cookies over localhost HTTP).
- SameSite should be Lax.

**If deployed in production (HTTPS):**
- Secure flag MUST be enabled on HttpOnly cookies.
- CORS Allowed Origins must explicitly match the frontend domain.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| slowapi@0.1.9 | fastapi@0.110.0 | Fully compatible. Works with Starlette's application/request objects. |

## Sources

- FastAPI security guides on OAuth2 with Password (and hashing), Bearer with JWT tokens.
- OWASP Session Management Cheat Sheet for Cookie Attributes (HttpOnly, Secure, SameSite).
- Slowapi documentation.

---
*Stack research for: Application Security*
*Researched: 2026-07-19*
