# Architecture Research

**Domain:** Application Security (v3.0 Security Milestone)
**Researched:** 2026-07-19
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                      │
│  ┌───────────────────────┐       ┌───────────────────────┐  │
│  │   Auth context/hooks  │       │      Axios Client     │  │
│  │ (Cookies automatically│       │ (Reads CSRF cookie    │  │
│  │     sent by browser)  │       │  attaches header)     │  │
│  └───────────┬───────────┘       └───────────┬───────────┘  │
└──────────────┼───────────────────────────────┼──────────────┘
               │ (Secure HttpOnly Cookie)      │ (X-CSRF-Token Header)
               ▼                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI Engine)                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  Security Middleware                  │  │
│  │  - CORS Check                                         │  │
│  │  - Rate Limiter (slowapi/in-memory limits)            │  │
│  │  - Security Headers (CSP, HSTS, X-Frame-Options)      │  │
│  │  - CSRF Validator (Matches cookie to header value)     │  │
│  └───────────────────────────┬───────────────────────────┘  │
│                              ▼                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Router Endpoints                   │  │
│  │  - Uses oauth2 dependency checking auth cookie        │  │
│  │  - Restricts dashboard access to admins/roles         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| CORS Middleware | Filters cross-origin requests. | FastAPI `CORSMiddleware` configured with trusted origins. |
| Security Headers Middleware | Adds HSTS, CSP, X-Frame-Options, X-Content-Type-Options to outgoing responses. | Custom FastAPI middleware or `secure` library middleware. |
| Rate Limiting Middleware | Restricts client request speed based on IP or authenticated user ID. | `slowapi` library routing decorator or custom middleware. |
| CSRF Middleware | Implements Double Submit Cookie check on all POST/PUT/DELETE requests. | Reads signed CSRF cookie, validates against request header. |
| OAuth2 Dependency | Extracts JWT from request cookie rather than Authorization header. | Custom FastAPI dependency overriding Starlette's `OAuth2PasswordBearer`. |

## Recommended Project Structure

No new folders are required, but the security components fit into:
```
backend/
├── app/
│   ├── core/
│   │   ├── security.py       # JWT creation, password hashing, secure keys
│   │   └── middleware.py     # Custom secure headers, CSRF middleware
│   ├── api/
│   │   ├── deps.py           # Dependency injection (e.g., get_current_user from cookie)
│   │   └── auth.py           # Auth endpoints setting HttpOnly cookies
│   └── main.py               # Rate limiter & CORS config
```

### Structure Rationale

- **`core/middleware.py`:** Groups all HTTP inspection and mutation policies (headers, CSRF) in one central file.
- **`api/deps.py`:** Updates `get_current_user` to cleanly extract credentials from cookies, keeping endpoint code dry.

## Architectural Patterns

### Pattern 1: Double Submit Cookie (CSRF Protection)

**What:** Frontend reads a cryptographically random, non-HttpOnly cookie (`csrf_token`) and duplicates its value in a request header (e.g. `X-CSRF-Token`). The backend verifies that the cookie value and header value match and are cryptographically signed.
**When to use:** Crucial when migrating JWT storage to HttpOnly cookies, since browsers automatically send cookies on cross-site requests.
**Trade-offs:** Avoids server-side CSRF token sessions, keeping the backend stateless.

### Pattern 2: Cookie-based OAuth2 Dependency Injection

**What:** Standard FastAPI `OAuth2PasswordBearer` searches the `Authorization` header. We override this to extract the token from the `access_token` cookie.
**Trade-offs:** Standard OpenAPI Swagger UI authorization button requires extra configuration or custom extraction to work seamlessly.

## Data Flow

### Request Flow with Security Gates

```
[User Request]
     ↓
[CORS Middleware] ──(Blocked?)──> [403 Forbidden]
     ↓ (Allowed)
[Rate Limiter] ──(Exceeded?)──> [429 Too Many Requests]
     ↓ (Within limit)
[CSRF Validation] ──(Mismatch?)──> [400 Bad Request]
     ↓ (Valid)
[Route Dependency (JWT Verification)] ──(Invalid?)──> [401 Unauthorized]
     ↓ (Valid JWT)
[Endpoint Execution]
```

## Scaling Considerations

Our app is designed for internal/local usage (up to 50MB file uploads, processed in-memory).
Memory-based rate limiting (`slowapi` in-memory backend) is perfect because it requires no infrastructure additions (like Redis). If clustered, this would split rate limits per node, which is acceptable for this setup.

## Anti-Patterns

### Anti-Pattern 1: Disabling CORS Check for convenience
**What people do:** Setting `allow_origins=["*"]` with `allow_credentials=True`.
**Why it's wrong:** Browsers block this configuration outright. If circumvented, any website can execute requests on behalf of the logged-in user.
**Do this instead:** Use explicit domain lists (`http://localhost:5173`, etc.).

## Sources

- FastAPI dependencies and middleware guides.
- OWASP CSRF prevention guidelines.

---
*Architecture research for: Application Security*
*Researched: 2026-07-19*
