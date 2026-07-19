# Pitfalls Research

**Domain:** Application Security (v3.0 Security Milestone)
**Researched:** 2026-07-19
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: XSS leading to Cookie theft

**What goes wrong:**
If an XSS vulnerability exists, attackers can execute scripts to steal JWT tokens.

**Why it happens:**
If the token is stored in `LocalStorage` or a non-HttpOnly cookie, JavaScript can read it via `document.cookie`.

**How to avoid:**
Set the `HttpOnly` flag on auth cookies. This makes them invisible to browser JavaScript, preventing script-based theft.

**Warning signs:**
Any front-end code checking LocalStorage for `token` or parsing JWT tokens in browser JS.

**Phase to address:**
Phase 1 (Cookie-based Auth).

---

### Pitfall 2: CSRF via Auto-sent Cookies

**What goes wrong:**
Since cookies are sent automatically by the browser with requests, malicious third-party websites can trigger authenticated requests on the server (CSRF).

**Why it happens:**
Migrating JWTs to HttpOnly cookies makes them vulnerable to CSRF unless explicitly protected.

**How to avoid:**
Implement `SameSite=Lax` on cookies to restrict cross-site sharing, and add Double Submit Cookie CSRF protection.

**Warning signs:**
State-changing API endpoints (POST/PUT/DELETE) that do not check for a CSRF token header or require specific headers.

**Phase to address:**
Phase 2 (CSRF Protection).

---

### Pitfall 3: In-Memory Rate Limiting State Loss on Restart

**What goes wrong:**
In-memory rate limiters reset their counts when the application server restarts.

**Why it happens:**
State is stored in RAM without a persistent store like Redis.

**How to avoid:**
Use `slowapi`'s in-memory storage for our local, single-instance app, but document that a Redis backend must be configured for multi-container load-balanced production.

**Warning signs:**
Restarting the backend container resets the request count instantly.

**Phase to address:**
Phase 3 (Rate Limiting).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| In-memory Rate Limiting | Quick setup, no external Redis requirement. | Rate limit counts reset on backend restart; doesn't scale horizontally. | Acceptable for local/development use. |
| Single Secret Key | Simple config. | Compromising the key compromises all aspects (JWTs, CSRF tokens, database crypt). | Never. Use separate keys for JWT signing and CSRF signing. |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Missing MIME type validation | Uploading executable files (scripts) disguised as CSV/XLSX. | Perform strict filename and Content-Type inspection. |
| Insecure CORS configuration | Malicious sites reading application responses. | Restrict CORS allowed origins to a whitelisted set of domains. |

---
*Pitfalls research for: Application Security*
*Researched: 2026-07-19*
