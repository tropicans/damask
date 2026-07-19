# Requirements: SecureData Web (Milestone: secured the app)

**Defined:** 2026-07-19
**Core Value:** Secure the SecureData Web application by hardening authentication, API communication, and access controls against common web vulnerabilities.

## v3 Requirements

Requirements for the security milestone.

### Cookie-based Authentication (SEC-AUTH)

- [ ] **SEC-01**: Access token (JWT) is stored in a secure, HttpOnly, SameSite=Lax cookie on login/register.
- [ ] **SEC-02**: Access token cookie is cleared from the client on logout by sending a past-expiration Set-Cookie header.
- [ ] **SEC-03**: Backend API retrieves JWT from the cookie instead of the Authorization header for authentication checks.

### CSRF & Browser Protections (SEC-CSRF)

- [ ] **SEC-04**: Double Submit Cookie CSRF protection is implemented for state-changing endpoints (POST/PUT/DELETE).
- [ ] **SEC-05**: Frontend Axios client automatically captures the CSRF token from the non-HttpOnly cookie and includes it in request headers for all mutating requests.
- [ ] **SEC-06**: Configure secure HTTP response headers (Content-Security-Policy, Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options) via a global middleware on the backend.

### Traffic & Payload Hardening (SEC-HARDEN)

- [ ] **SEC-07**: Configure rate limiting on authentication routes (login, register) and data upload/masking routes.
- [ ] **SEC-08**: Harden input validation for incoming CSV/XLSX file uploads (strict 50MB payload limits, MIME-type and extension validation).
- [ ] **SEC-09**: Restrict access to the dashboard and audit log endpoints to users with authorized roles.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Saving raw uploads for auditing | Excluded to guarantee compliance with privacy regulations (never store raw PII). |
| Custom encryption for tokens | Standard cryptographic libraries (PyJWT) are more secure and easier to audit. |
| Redis-backed distributed rate limiting | In-memory is sufficient for this single-instance local application; Redis can be configured as a future enhancement. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SEC-01 | Phase 6 | Pending |
| SEC-02 | Phase 6 | Pending |
| SEC-03 | Phase 6 | Pending |
| SEC-04 | Phase 6 | Pending |
| SEC-05 | Phase 6 | Pending |
| SEC-06 | Phase 7 | Pending |
| SEC-07 | Phase 7 | Pending |
| SEC-08 | Phase 8 | Pending |
| SEC-09 | Phase 8 | Pending |

**Coverage:**
- v3 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-19*
*Last updated: 2026-07-19 after milestone initialization*
