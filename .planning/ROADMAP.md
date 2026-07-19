# Roadmap: SecureData Web

## Milestones

- ✅ **v1.0 MVP** - Phases 1-4 (shipped 2026-07-19)
- ✅ **v2.0 add documentation** - Phase 5 (shipped 2026-07-19)
- 🚧 **v3.0 secured the app** - Phases 6-8 (in progress)

---

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) - SHIPPED 2026-07-19</summary>

### Phase 1: Foundation & Preview Engine
- **Goal**: Upload CSV/XLSX file strictly in-memory, parse and return the first 3 preview rows with automatic column regex mapping recommendations.
- **Plans**: 3 plans (completed)

### Phase 2: Masking Engine & Download
- **Goal**: Configure and execute column-based Faker transformations, and download the masked file in-memory.
- **Plans**: 3 plans (completed)

### Phase 3: User Authentication
- **Goal**: Secure login and registration.
- **Plans**: 2 plans (completed)

### Phase 4: Audit Logging & Dashboard
- **Goal**: Persist audit logs of masking jobs and display them in a dashboard.
- **Plans**: 2 plans (completed)

</details>

<details>
<summary>✅ v2.0 add documentation (Phase 5) - SHIPPED 2026-07-19</summary>

### Phase 5: Documentation Suite
- **Goal**: Create architecture, API spec, deployment docs, root README, and annotate codebase with inline docstrings.
- **Plans**: 3 plans (completed)

</details>

### 🚧 v3.0 secured the app (In Progress)

**Milestone Goal:** Secure the application by hardening authentication, API communication, and access controls against common web vulnerabilities.

#### Phase 6: Cookie-based Auth & CSRF Protection
- **Goal**: Move JWT storage from client LocalStorage to HttpOnly cookies and implement Double Submit Cookie CSRF prevention.
- **Depends on**: Phase 5
- **Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05
- **Success Criteria** (what must be TRUE):
  1. Login and register endpoints set access token as an HttpOnly, Secure, SameSite=Lax cookie.
  2. Frontend handles cookie-based auth without storing JWTs in LocalStorage.
  3. State-changing requests verify CSRF token sent in the custom request header matching a CSRF cookie.
- **Plans**: 2 plans
  - [ ] 06-01: Implement HttpOnly cookie auth on backend and frontend Axios/state client.
  - [ ] 06-02: Implement Double Submit Cookie CSRF middleware and update Axios interceptor.

#### Phase 7: Secure Headers & Rate Limiting
- **Goal**: Configure HTTP security headers and restrict API requests using slowapi.
- **Depends on**: Phase 6
- **Requirements**: SEC-06, SEC-07
- **Success Criteria** (what must be TRUE):
  1. All API routes return response headers including CSP, HSTS, X-Frame-Options.
  2. Rate limiting limits auth routes and file processing routes.
- **Plans**: 2 plans
  - [ ] 07-01: Set up secure HTTP response headers middleware.
  - [ ] 07-02: Integrate rate limiting with slowapi.

#### Phase 8: Input Hardening & Role Authorization
- **Goal**: Harden file upload validation and restrict dashboard access by user roles.
- **Depends on**: Phase 7
- **Requirements**: SEC-08, SEC-09
- **Success Criteria** (what must be TRUE):
  1. Backend rejects file uploads exceeding 50MB before parsing them.
  2. Dashboard statistics and job records are restricted to admin/auditor roles.
- **Plans**: 2 plans
  - [ ] 08-01: Add strict MIME-type and 50MB size checks for file uploads.
  - [ ] 08-02: Restrict dashboard audit logs to administrator roles.

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation & Preview Engine | v1.0 | 3/3 | Complete | 2026-07-19 |
| 2. Masking Engine & Download | v1.0 | 3/3 | Complete | 2026-07-19 |
| 3. User Authentication | v1.0 | 2/2 | Complete | 2026-07-19 |
| 4. Audit Logging & Dashboard | v1.0 | 2/2 | Complete | 2026-07-19 |
| 5. Documentation Suite | v2.0 | 3/3 | Complete | 2026-07-19 |
| 6. Cookie-based Auth & CSRF | v3.0 | 0/2 | Not started | - |
| 7. Secure Headers & Limits | v3.0 | 0/2 | Not started | - |
| 8. Input & Role Security | v3.0 | 0/2 | Not started | - |

---
*Roadmap updated: 2026-07-19*
