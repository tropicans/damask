# Testing Strategy & Verification Practices

**Mapped Date:** 2026-07-20

## Overview & Metrics

The codebase maintains 100% passing test suites across both backend domain logic and frontend error handling utilities:
- **Backend Test Suite:** 107 tests across 12 test modules (**100% Passed**).
- **Frontend Test Suite:** 3 tests in native Node 22 test runner (**100% Passed**).

## Backend Testing Architecture (`backend/app/tests/`)

### Test Framework
- **Framework:** `pytest` (`^9.1.1`) with `pytest-asyncio` and `httpx`.
- **Client:** FastAPI `TestClient` for isolated HTTP request execution.
- **Database Isolation:** Pytest fixtures in `conftest.py` create fresh in-memory SQLModel database sessions per test run.

### Test Coverage Breakdown

| Test File | Focus Area | Key Assertions |
| :--- | :--- | :--- |
| `test_audit.py` | Audit Logging | Verification of job metadata logging and audit retrieval. |
| `test_auth.py` | Authentication & Registration | Login, password hashing, invite validation, session cookies. |
| `test_auth_policy.py` | Password & Lockout Policy | Lockout after 5 failed attempts, password complexity checks. |
| `test_csrf.py` | CSRF Protection | Validation of `secure_data_csrf` cookie and `X-CSRF-Token` header. |
| `test_detector.py` | PII Auto-Detection | Heuristic and regex detection for NIK, Email, Credit Cards, Phones. |
| `test_headers.py` | Security Headers | Verification of CSP, HSTS, X-Frame-Options, X-Content-Type-Options. |
| `test_input_validation.py` | Input Hardening | Validation of file size limits, invalid file extensions, payload limits. |
| `test_masker.py` | Masking Engine | Verification of Faker, Redact, Perturb, Hash, and Pseudonym strategies. |
| `test_parser.py` | CSV / XLSX Parsing | In-memory IO buffer parsing and dataframe exporting. |
| `test_reversion.py` | Data Reversion | Symmetric Fernet key generation, ZIP packaging, and full restoration. |
| `test_role_security.py` | Role-Based Access Control | Enforcement of `admin` vs `user` endpoint access control. |
| `test_user_mgmt.py` | User Management | Admin user status toggles (Active/Inactive) and role modification. |

### Running Backend Tests
From the `backend/` directory:
```bash
.\.venv\bin\python -m pytest app/tests
```

## Frontend Testing Architecture (`frontend/src/utils/`)

### Test Framework
- **Runner:** Built-in Node.js 22 test runner (`node:test` and `node:assert/strict`).
- **Test File:** `frontend/src/utils/formatError.test.js`.
- **Focus:** Validating `extractErrorMessage()` behavior when receiving FastAPI 422 validation detail arrays, string errors, and fallback messages.

### Running Frontend Tests
From the repository root:
```bash
C:\Users\yudhiar\AppData\Local\nvm\v22.22.3\node.exe --test frontend/src/utils/formatError.test.js
```
