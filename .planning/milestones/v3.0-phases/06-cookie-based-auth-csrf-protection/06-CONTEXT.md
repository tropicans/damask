# Phase 6: Cookie-based Auth & CSRF Protection - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Move JWT token storage from client-side LocalStorage to HttpOnly cookies and implement Double Submit Cookie CSRF prevention.
This involves updating:
1. Backend login, register, and logout endpoints to set/delete cookies.
2. Backend authentication dependency to retrieve JWT from the cookie instead of the Authorization header.
3. Backend CSRF middleware to set a CSRF token cookie on safe GET requests and validate it on mutating POST/PUT/DELETE requests.
4. Frontend Axios client to support credentials (cookies) and automatically extract/forward CSRF tokens.
5. Frontend App-level session checking and redirection logic to work with cookie-based authentication.

</domain>

<decisions>
## Implementation Decisions

### Cookie Session Verification
- **D-01:** Always call `/api/auth/me` on load. The frontend React app will make an initial request to `/api/auth/me` on page load to verify if a valid session exists.
- **D-02:** Silent fallback to Login on `/me` failure. If the initial `/me` request fails with a 401, the frontend will clear any local user state and display the Login form without displaying intrusive session expired messages.
- **D-03:** Return only the User profile object in JSON response. The `/login` and `/register` endpoints will not return the raw JWT string in the JSON payload. Sesi state is fully managed by browser cookies.
- **D-04:** Fixed token expiration. JWT token lifetime is fixed to 24 hours as defined in the configuration, requiring re-authentication upon expiration.

### Double Submit Cookie CSRF Delivery
- **D-05:** Automatic middleware injection of CSRF cookie. The backend will set a `secure_data_csrf` cookie containing a random token on safe GET requests (e.g. `/me`, `/preview`) if the cookie is not already present.
- **D-06:** Global validation on mutating endpoints. The backend middleware will validate the CSRF token on all POST, PUT, and DELETE requests, excluding public `/api/auth/login` and `/api/auth/register` endpoints.
- **D-07:** Axios request interceptor for header injection. The frontend Axios client will extract the CSRF token from the `secure_data_csrf` cookie via `document.cookie` and attach it as an `X-CSRF-Token` header.
- **D-08:** CSRF token rotation on logout. The CSRF cookie will be cleared/regenerated when the user logs out to prevent token reuse.

### CORS & Cookie Settings
- **D-09:** Dynamic cookie attributes. Session cookie attributes will be determined dynamically (e.g. `Secure=True` in production HTTPS, `Secure=False` in HTTP development, `SameSite=Lax`).
- **D-10:** CORS credentials enablement. FastAPI CORS configuration will set specific origins via `CORS_ALLOWED_ORIGINS` and enable `allow_credentials=True`.
- **D-11:** Unset cookie Domain. The cookie `Domain` attribute will be left unset by default, restricting cookies to the issuing host (suitable for localhost and single-host deploys).
- **D-12:** Custom cookie names. We will use `secure_data_session` for the JWT session cookie and `secure_data_csrf` for the CSRF token cookie to prevent conflicts.

### Logout & Token Expiration Handling
- **D-13:** Active cookie deletion on logout. The backend `/logout` endpoint will set the `secure_data_session` cookie to an empty value with a past expiration date (`Max-Age=0`).
- **D-14:** Active cookie deletion on 401 backend rejection. If backend authentication fails because the JWT has expired, the backend will return a 401 response and set a past-expiration cookie header to clean up the browser cookie.
- **D-15:** Stateless session termination. No server-side token blacklist will be implemented. Clients rely on stateless cookie deletion.
- **D-16:** Centralized 401 catch-and-redirect. The frontend Axios client will use a response interceptor to globally catch 401 errors, reset React user state, and show the Login view.

### the agent's Discretion
- The developer has discretion to determine the exact helper utility/library for cookie parsing on the backend or utility library (if any) to parse cookies on the frontend.
- The developer has discretion to write helper functions for token extraction or cookie formatting on the backend.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope & Guidelines
- [ROADMAP.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/ROADMAP.md) — Phased roadmap and success criteria.
- [REQUIREMENTS.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/REQUIREMENTS.md) — Requirements traceability (specifically SEC-01 through SEC-05).
- [PROJECT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/PROJECT.md) — Base project constraints and current milestone details.

### Prior Context
- [.planning/milestones/v3.0-phases/03-user-authentication/03-CONTEXT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/milestones/v3.0-phases/03-user-authentication/03-CONTEXT.md) — Initial user authentication decisions (state-based routing, database structure).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- JWT signing and verification settings in [config.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/core/config.py).
- Backend dependency `get_current_user` in [auth.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/services/auth.py).
- Axios `apiClient` instance in [client.ts](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/api/client.ts).

### Established Patterns
- State-based session rendering in `frontend/src/App.tsx` (using conditional user checks to mount components).
- Dependency injection in FastAPI endpoint routing functions.

### Integration Points
- API routers: `backend/app/api/endpoints/auth.py` (adding cookie extraction and logout endpoints).
- API client configuration: `frontend/src/api/client.ts` (modifying headers and cookies credentials handling).
- Application root: `frontend/src/App.tsx` (updating mount logic to check session cookie via `/me` on launch).

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-Cookie-based Auth & CSRF Protection*
*Context gathered: 2026-07-19*
