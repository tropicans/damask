# Phase 8: Input Hardening & Role Authorization Context

## Domain
Hardening file upload payload validation and restricting audit dashboard access using role-based access control.

## Decisions

- **D-01 (Strict File Size Limit)**: Perform size checks BEFORE loading file bytes completely into RAM:
  - Verify the request `Content-Length` header first.
  - Read incoming file streams in chunks (8KB size), raising `413 Payload Too Large` immediately if cumulative size exceeds 50MB (52,428,800 bytes).
- **D-02 (MIME-type Validation)**: Reject uploads whose `content_type` is not one of:
  - CSV: `text/csv`, `application/vnd.ms-excel`, `text/x-csv`, `application/csv`, `text/comma-separated-values`
  - Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **D-03 (User Roles Schema)**: Add a `role` string field to the `User` schema (defaulting to `"user"`). Supported roles are `"admin"`, `"auditor"`, and `"user"`.
- **D-04 (Role Access Control)**:
  - Restrict all endpoints in `/api/jobs/*` to users with `"admin"` or `"auditor"` roles, returning `403 Forbidden` for regular users.
  - Show the "Dashboard Audit" navigation tab on the frontend only to users with authorized roles.

## Canonical Refs
- [ROADMAP.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev\datamask/.planning/ROADMAP.md)
- [REQUIREMENTS.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev\datamask/.planning/REQUIREMENTS.md)
