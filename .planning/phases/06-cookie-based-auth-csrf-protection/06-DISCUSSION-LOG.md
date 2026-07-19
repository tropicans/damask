# Phase 6: Cookie-based Auth & CSRF Protection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 6-Cookie-based Auth & CSRF Protection
**Areas discussed:** Cookie Session Verification, Double Submit Cookie CSRF Delivery, CORS & Cookie Settings, Logout & Token Expiration Handling

---

## Cookie Session Verification

| Option | Description | Selected |
|--------|-------------|----------|
| Always call `/api/auth/me` on load | Most secure, ensures the cookie is valid, prevents stale states | ✓ |
| Check non-HttpOnly `session_active` cookie first | Saves a network call if user is not logged in, but adds cookie management complexity | |
| Use cached localStorage user profile indicator | Simple, but can lead to stale states if cookie expires on backend | |

**User's choice:** Always call `/api/auth/me` on load
**Notes:** The React frontend will check session validity immediately when the app boots by making a call to `/api/auth/me`. If it succeeds, the user is authenticated. If it fails with a 401, the user is silently redirected to the Login view, resetting any local React states. The raw JWT token string is not returned in the JSON payload of login/register.

---

## Double Submit Cookie CSRF Delivery

| Option | Description | Selected |
|--------|-------------|----------|
| Automatic middleware injection | On every safe GET request like `/me` or `/preview`, set the cookie if missing | ✓ |
| Dedicated `/api/auth/csrf` endpoint | Frontend must explicitly request a token on initial boot | |
| Set on login/register only | CSRF cookie is created only when the user authenticates | |

**User's choice:** Automatic middleware injection
**Notes:** The backend will automatically inject a CSRF token cookie (`secure_data_csrf`) on safe GET requests if it's missing. Mutating requests (POST, PUT, DELETE) will be validated globally by backend middleware, except for public `/login` and `/register` endpoints. The Axios client will extract the CSRF token from the cookie via `document.cookie` and attach it as the `X-CSRF-Token` header. The CSRF token cookie is cleared/regenerated on logout.

---

## CORS & Cookie Settings

| Option | Description | Selected |
|--------|-------------|----------|
| Dynamic based on environment variables | Secure=True in production HTTPS, Secure=False in HTTP development, SameSite=Lax | ✓ |
| Hardcoded for local development | Secure=False, SameSite=Lax, Domain=None; simpler to manage initially | |

**User's choice:** Dynamic based on environment variables
**Notes:** Cookie secure flags, SameSite, and Domain attributes will be configured dynamically via environment variables. Specific origins will be allowed via `CORS_ALLOWED_ORIGINS` with `allow_credentials=True` on the FastAPI backend. The cookie `Domain` attribute will be left unset by default to restrict cookie scope to the issuing host. Custom cookie names (`secure_data_session` and `secure_data_csrf`) will be used to avoid naming conflicts.

---

## Logout & Token Expiration Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Send Set-Cookie with empty value, past expiration (Max-Age=0) | Ensures browser deletes the cookie immediately | ✓ |
| Only delete the token from the frontend React state | Leaves cookie in browser; insecure as subsequent requests can reuse it | |

**User's choice:** Send Set-Cookie with empty value, past expiration (Max-Age=0)
**Notes:** The backend will clear session cookies on logout by setting their expiration date to the past. On 401 errors caused by expired sessions, the backend will return a 401 and set a past-expiration cookie header to clean up the browser cookie. No backend token blacklist will be implemented, keeping the application stateless. The frontend will catch 401 errors globally using an Axios response interceptor, clearing React user state and showing the Login view.

---

## the agent's Discretion

The developer has discretion to:
1. Determine the exact helper utility/library to parse cookies on the backend and frontend.
2. Structure internal token extraction or cookie formatting helpers on the backend.

## Deferred Ideas

None — discussion stayed within phase scope.
