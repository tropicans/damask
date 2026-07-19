# Phase 11: Auth Policy & Invite Registration - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 implements three interconnected security hardening features:
1. **Invite-based registration** — New users can only register with a valid, single-use invite code/link created by an admin. Direct open registration is rejected.
2. **Password policy enforcement** — Backend rejects passwords not meeting policy (min 8 chars, uppercase + lowercase + digit). Frontend shows a real-time password strength indicator (Lemah/Sedang/Kuat).
3. **Account lockout (brute-force protection)** — After 5 consecutive failed login attempts from the same IP, the account is locked for 15 minutes.
</domain>

<decisions>
## Implementation Decisions

### Invite System — Storage & Model
- **D-01:** Create a new `Invite` SQLModel/table with fields: `id` (UUID PK), `token` (UUID, unique, indexed), `created_by` (FK → users.id), `used_by` (FK → users.id, nullable), `expires_at` (datetime), `is_used` (bool, default False), `created_at` (datetime).
- **D-02:** Invite token is a UUID4 string. Admin creates invite via `POST /api/auth/invite` (admin-only endpoint). The response returns the full invite URL: `{FRONTEND_URL}/register?invite=<token>`.
- **D-03:** Invite expiry default is 48 hours from creation. Admin cannot customize expiry per-invite for v1 (simplicity); configurable via `settings.INVITE_EXPIRE_HOURS = 48`.
- **D-04:** Invite is single-use — marked `is_used=True` and `used_by` set upon successful registration. Reusing a consumed or expired invite returns HTTP 400 with a descriptive error.

### Invite Registration Flow — UX
- **D-05:** The registration flow uses a URL parameter: users navigate to `/register?invite=<token>`. The frontend `AuthForm.tsx` reads the query parameter on mount. If present, the invite token is pre-filled (hidden field) and registration proceeds. If absent, registration tab shows an error: "Pendaftaran memerlukan kode undangan yang valid."
- **D-06:** Admin invite creation UI: add a button "Buat Tautan Undangan" in the admin section of `App.tsx` (next to the Audit tab, admin-only). Clicking it triggers `POST /api/auth/invite`, then shows the generated link in a copyable modal/tooltip.

### Password Policy — Backend
- **D-07:** Backend validates new passwords at registration with a regex: must contain at least 1 uppercase, 1 lowercase, 1 digit, minimum 8 characters. Returns HTTP 422 with detail: `"Password harus mengandung minimal 1 huruf kapital, 1 huruf kecil, dan 1 angka."` when policy fails.
- **D-08:** Password policy is implemented as a standalone validator function in `app/services/auth.py` → `validate_password_policy(password: str) -> None` (raises `ValueError` on failure). Called from the `/register` endpoint before hashing.

### Password Strength Indicator — Frontend
- **D-09:** The strength indicator is a visual bar with 3 segments (Lemah/Sedang/Kuat) rendered below the password input in `AuthForm.tsx`. It calculates strength in real-time via a `calculatePasswordStrength(password)` util:
  - **Lemah (red):** < 2 criteria met
  - **Sedang (yellow):** 2–3 criteria met (length ≥8, uppercase, lowercase, digit)
  - **Kuat (green):** all 4 criteria met
- **D-10:** The strength bar is only shown when the registration tab is active (not on login tab) and only after the user has started typing in the password field.

### Account Lockout — Brute-Force Protection
- **D-11:** Track failed login attempts in a new `LoginAttempt` table (or an in-memory dict for simplicity). **Decision: use an in-memory dict** (`failed_attempts: dict[str, list[datetime]]`) keyed by IP address. This avoids DB overhead and is acceptable since the app is a local/internal tool that doesn't survive restarts with persistent lockout state. Reset on server restart is acceptable.
- **D-12:** If 5+ failed attempts from the same IP within a 15-minute rolling window → return HTTP 423 (Locked) with detail `"Akun dikunci 15 menit karena terlalu banyak percobaan login. Silakan coba lagi nanti."` and block the attempt. Cleanup: attempts older than 15 minutes are pruned from the list on each request.
- **D-13:** Successful login clears the failed attempt counter for that IP.

### Agent's Discretion
- The exact HTML/CSS for the password strength bar segments follows the existing Tailwind dark-mode palette in `AuthForm.tsx` (indigo/slate colors). Agent may design the visual indicator freely within that palette.
- CSRF token handling for new endpoints follows the established pattern in Phase 6 (existing CSRF cookie).
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- `.planning/ROADMAP.md` — Phase 11 goal, success criteria, and dependency chain.
- `.planning/REQUIREMENTS.md` — Requirements PROD-04, PROD-05, PROD-06, PROD-07, PROD-14.

### Backend Auth System
- `backend/app/api/endpoints/auth.py` — Existing `/register`, `/login`, `/logout`, `/me` endpoints to be extended.
- `backend/app/services/auth.py` — Auth service with `hash_password`, `verify_password`, `get_current_user` — new `validate_password_policy` and lockout logic added here.
- `backend/app/models/user.py` — Existing `User`, `UserRegister`, `UserLogin`, `UserResponse` models — new `Invite` model added alongside.
- `backend/app/core/config.py` — Settings pattern to follow; add `INVITE_EXPIRE_HOURS` and `FRONTEND_URL` settings.

### Frontend Auth System
- `frontend/src/components/AuthForm.tsx` — Main auth UI to extend with invite token field and password strength indicator.
- `frontend/src/api/auth.ts` — Auth API client to extend with `createInvite` function.
- `frontend/src/App.tsx` — Navigation/admin controls for invite link creation button.

### Database & Config
- `backend/app/db.py` — DB setup; new `Invite` table must be registered here.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AuthForm.tsx`: Already has tab-based login/register UI with error state, loading state, and password input. Extend in-place — add invite token reading from URL params, add strength indicator below password field.
- `services/auth.py`: `hash_password`, `verify_password` utilities reusable. In-memory lockout dict added here alongside.
- `core/limiter.py`: Rate limiter already applied on `/register` and `/login` (5/minute). Lockout is a separate mechanism on top.
- `core/config.py`: Settings pattern — follow for adding `INVITE_EXPIRE_HOURS` and `FRONTEND_URL`.

### Established Patterns
- **Admin-only endpoints**: Check `current_user.role == "admin"` via `Depends(get_current_user)` in the endpoint and raise `HTTPException(403)` — see pattern in `jobs.py`.
- **SQLModel tables**: Follow `User` model pattern in `models/user.py` for the new `Invite` model.
- **Cookie-based auth**: Existing HttpOnly cookie session pattern in `auth.py` login endpoint.
- **URL query params in React**: Use `new URLSearchParams(window.location.search)` or `useSearchParams` (if React Router is present) to read `?invite=<token>`.

### Integration Points
- `backend/app/api/endpoints/auth.py`: Add `POST /invite` (admin-only), modify `/register` to accept + validate invite token.
- `backend/app/models/user.py`: Add `Invite` SQLModel class.
- `backend/app/db.py`: Ensure `Invite` table is created on startup (SQLModel.metadata.create_all).
- `backend/app/services/auth.py`: Add `validate_password_policy()` and in-memory lockout dict + helpers.
- `frontend/src/components/AuthForm.tsx`: Read URL param on mount, add hidden invite_token field, add password strength bar.
- `frontend/src/api/auth.ts`: Add `createInvite()` API function.
- `frontend/src/App.tsx`: Add "Buat Tautan Undangan" button visible to admin role.
</code_context>

<specifics>
## Specific Ideas

- Invite URL format: `http://localhost:5173/register?invite=<uuid-token>` — frontend copies this to clipboard from the modal.
- Password strength criteria (4 total): length ≥ 8, has uppercase, has lowercase, has digit. Strength = number of criteria met.
- HTTP 423 (Locked) for lockout response — more semantically correct than 429 (Too Many Requests).
- In-memory lockout dict structure: `{ "192.168.1.1": [datetime1, datetime2, ...] }` — prune entries older than 15 minutes on each login attempt.
</specifics>

<deferred>
## Deferred Ideas

- Email delivery for invite links (SMTP) — explicitly out of scope per REQUIREMENTS.md; invite links shared via copy-paste.
- Configurable lockout duration per user (not just per IP) — deferred to v2.
- Invite link management UI (list/revoke invites) — belongs in Phase 12 admin UI.
- Password expiry / forced rotation — PROD-V2-03, explicitly deferred to v2.
</deferred>

---

*Phase: 11-Auth Policy & Invite Registration*
*Context gathered: 2026-07-19*
