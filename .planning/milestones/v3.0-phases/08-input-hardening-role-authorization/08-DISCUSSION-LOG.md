# Phase 8: Input Hardening & Role Authorization Discussion Log

## Discussion Area 1: File Size Checking
- **Options Considered**:
  1. Check size post-reading fully in memory.
  2. Check Content-Length header and read in chunks (Recommended).
- **Selection**: Option 2.
- **Notes**: Checking Content-Length is a quick fail, and chunk-by-chunk reading ensures that a malicious client cannot crash the server with a giant file.

## Discussion Area 2: Role Management
- **Options Considered**:
  1. Standardize role names as simple string field on User schema (Recommended).
  2. Implement a separate `Role` table and relationships.
- **Selection**: Option 1.
- **Notes**: Simple string roles (e.g. `"admin"`, `"auditor"`, `"user"`) are sufficient for this internal application and do not introduce database complexity.

## Discussion Area 3: Dashboard Restriction
- **Options Considered**:
  1. Restrict `/api/jobs` dashboard endpoints entirely to admin/auditor roles (Recommended).
  2. Allow regular users to view their own history but restrict stats.
- **Selection**: Option 1.
- **Notes**: Fulfilling SEC-09 strictly by reserving dashboard statistics and audit log records to administrative/auditor roles.
