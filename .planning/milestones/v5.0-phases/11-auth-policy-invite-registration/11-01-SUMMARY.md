---
phase: 11-auth-policy-invite-registration
plan: "11-01"
subsystem: auth
tags: [fastapi, sqlmodel, bcrypt]

requires:
  - phase: 10-revert-interface-auditing
    provides: revert UI and revert logging
provides:
  - Invite model and database schema for invites
  - POST /api/auth/invite admin-only endpoint
  - validate_password_policy validation logic
  - In-memory brute-force lockout protection (lockout for 15 minutes after 5 failures)
affects:
  - 11-02-PLAN
  - 11-03-PLAN

tech-stack:
  added: []
  patterns: [In-memory failed login tracking, Single-use registration token validation]

key-files:
  created: []
  modified:
    - backend/app/models/user.py
    - backend/app/services/auth.py
    - backend/app/api/endpoints/auth.py
    - backend/app/db.py
    - backend/app/core/config.py

key-decisions:
  - "Used an in-memory dictionary for tracking failed login attempts from a given IP address, resetting upon server restart, which is sufficient for this local/internal tool."
  - "Enforced password policy (minimum 8 characters, at least 1 uppercase, 1 lowercase, and 1 digit) on the backend before hashing."

patterns-established:
  - "Invite token verification pattern: check existence, check is_used, check expires_at, and set used_by/is_used on registration."

requirements-completed:
  - PROD-04
  - PROD-05
  - PROD-06
  - PROD-14

coverage:
  - id: D1
    description: "Invite model and table registered in SQLModel"
    requirement: PROD-04
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_create_invite_success"
        status: pass
    human_judgment: false
  - id: D2
    description: "POST /api/auth/invite is admin-only and generates valid invite URLs"
    requirement: PROD-04
    verification:
      - kind: integration
        ref: "backend/app/tests/test_invite.py#test_non_admin_cannot_create_invite"
        status: pass
    human_judgment: false
  - id: D3
    description: "Invite token expires after 48 hours"
    requirement: PROD-04
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_expired_invite_rejected"
        status: pass
    human_judgment: false
  - id: D4
    description: "Invite tokens are single-use only"
    requirement: PROD-04
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_used_invite_rejected"
        status: pass
    human_judgment: false
  - id: D7
    description: "Validate password policy at registration (min 8 chars, uppercase, lowercase, digit)"
    requirement: PROD-05
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_register_with_no_uppercase_rejected"
        status: pass
    human_judgment: false
  - id: D11
    description: "Failed attempt tracking dictionary in auth.py service"
    requirement: PROD-06
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_brute_force_lockout"
        status: pass
    human_judgment: false
  - id: D12
    description: "Lock out IP after 5 failed login attempts for 15 minutes"
    requirement: PROD-06
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_brute_force_lockout"
        status: pass
    human_judgment: false
  - id: D13
    description: "Successful login clears failed attempt count"
    requirement: PROD-06
    verification:
      - kind: unit
        ref: "backend/app/tests/test_invite.py#test_successful_login_clears_failed_attempts"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-07-20
status: complete
---

# Phase 11: Auth Policy & Invite Registration - Plan 11-01 Summary

**Backend implementation of the Invite model, password policy validation, and login brute-force lockout.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-07-20T08:56:00Z
- **Completed:** 2026-07-20T09:10:00Z
- **Tasks:** 5
- **Files modified:** 5

## Accomplishments
- Implemented `Invite` SQLModel class and `InviteResponse` schema.
- Added `validate_password_policy` function using regex validation.
- Configured in-memory dictionary-based brute force protection, lockout IP for 15 minutes after 5 failed login attempts.
- Modified `/register` endpoint to validate invite tokens and enforce the password policy.
- Modified `/login` endpoint to integrate lockout checks.

## Task Commits

Each task was committed atomically:
1. **Task 1: Add INVITE_EXPIRE_HOURS and FRONTEND_URL to settings** - `0723eb3` (feat)
2. **Task 2: Add Invite SQLModel to models/user.py** - `0723eb3` (feat)
3. **Task 3: Register Invite table in db.py** - `0723eb3` (feat)
4. **Task 4: Add validate_password_policy and account lockout to auth.py** - `0723eb3` (feat)
5. **Task 5: Add POST /invite endpoint and modify /register with invite validation in auth.py** - `0723eb3` (feat)

## Files Created/Modified
- `backend/app/core/config.py` - Added invite configuration settings.
- `backend/app/models/user.py` - Created SQLModel table for invites.
- `backend/app/db.py` - Registered Invite table with SQLModel.
- `backend/app/services/auth.py` - Added password policy validation and IP lockout tracking.
- `backend/app/api/endpoints/auth.py` - Added /invite endpoint and updated /register and /login endpoints.

## Decisions Made
- Used an in-memory dictionary for tracking failed login attempts from a given IP address, resetting upon server restart, which is sufficient for this local/internal tool.
- Enforced password policy (minimum 8 characters, at least 1 uppercase, 1 lowercase, and 1 digit) on the backend before hashing.

## Deviations from Plan
None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None.

## Next Phase Readiness
- Backend functionality for password policy, invite validation, and IP lockout is complete and verified by unit tests.
- Ready to implement frontend invite-based registration UI in Wave 2.
