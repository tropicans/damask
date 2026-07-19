# Feature Research

**Domain:** Application Security (v3.0 Security Milestone)
**Researched:** 2026-07-19
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels insecure/incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| HttpOnly Cookie Auth | Stored tokens must be safe from XSS. | MEDIUM | Backend sets JWT cookie; frontend automatically sends it. |
| Secure HTTP Headers | Standard browser defense-in-depth headers. | LOW | Add via backend middleware (CSP, HSTS, X-Frame-Options). |
| Rate Limiting on Login | Prevents brute-force account cracking. | MEDIUM | Use slowapi or custom route decorator on auth endpoints. |
| Input Validation | Ensures uploaded CSV/XLSX matches schema/size constraints before parsing. | MEDIUM | Strict pydantic and pandas size checks. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Double Submit Cookie CSRF | Protects API from CSRF without database state. | MEDIUM | Frontend reads CSRF cookie and adds header. Backend validates. |
| Audit Log Integrity | Ensures logged events cannot be falsified/altered by standard users. | MEDIUM | Set logs to read-only/append-only and secure dashboard routes. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Saving raw uploads for auditing | Easy debugging of upload issues. | High risk of PII data leak. Violates core in-memory promise. | Only log file metadata (name hash, size, row count), never raw data. |
| Custom crypto for tokens | "Better than standard JWTs." | Custom crypto often contains subtle security flaws. | Use standard `PyJWT` with HS256 and secure environment keys. |

## Feature Dependencies

```
[HttpOnly Cookie Auth] ──requires──> [CSRF Protection (Double Submit)]
                                           └──requires──> [Frontend API client update]

[Rate Limiting] ──enhances──> [HttpOnly Cookie Auth]

[Secure Headers (CSP)] ──enhances──> [HttpOnly Cookie Auth]
```

### Dependency Notes

- **HttpOnly Cookie Auth requires CSRF Protection:** Storing JWTs in cookies exposes them to Cross-Site Request Forgery (CSRF). Double Submit Cookie pattern must be added to mitigate this.
- **CSRF Protection requires Frontend API client update:** The React axios client must read the CSRF cookie and include it in request headers.

## MVP Definition

### Launch With (v3.0)

- [ ] HttpOnly Cookie Auth — Move JWT storage off frontend LocalStorage.
- [ ] Double Submit Cookie CSRF — Necessary companion to HttpOnly Cookie Auth.
- [ ] Secure HTTP Headers (CSP, HSTS, CORS, X-Frame-Options) — Core browser defense.
- [ ] Endpoint Rate Limiting — Lock down auth and upload routes.
- [ ] Safe File Stream Input Validation — Size boundary limits (50MB) and type checking.
- [ ] Dashboard & Audit Log Access Controls — Restrict dashboard endpoints to authorized roles.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| HttpOnly Cookie Auth | HIGH | MEDIUM | P1 |
| CSRF Protection | HIGH | MEDIUM | P1 |
| Secure HTTP Headers | HIGH | LOW | P1 |
| Endpoint Rate Limiting | MEDIUM | MEDIUM | P1 |
| Input validation | HIGH | MEDIUM | P1 |
| Audit log access restrictions | HIGH | MEDIUM | P1 |

## Sources

- OWASP Top 10 API Security Risks.
- Starlette / FastAPI documentation on Middleware and Cookie management.

---
*Feature research for: Application Security*
*Researched: 2026-07-19*
