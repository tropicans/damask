# Requirements: SecureData Web - Data Reversion Facility

**Defined:** 2026-07-19
**Core Value:** Ensure sensitive data can be reverted back to its real values using a zero-knowledge, local-only mapping key, so that no PII is permanently stored on the server.

## v1 Requirements

### Data Reversion (REV)

- [ ] **REV-01**: Generate a 1-to-1 bijective mapping of original values to masked values per column during data masking.
- [ ] **REV-02**: Support downloading the reversion mapping key file (JSON format) alongside the masked file upon successful masking.
- [ ] **REV-03**: Create a dedicated "Revert Data" page/tab in the React frontend UI allowing users to upload a masked file and its reversion mapping JSON file.
- [ ] **REV-04**: Implement backend in-memory processing to parse the masked file and apply the reversion mapping JSON to restore original values.
- [ ] **REV-05**: Record revert execution metadata (original file name, file size, row count, and execution time) in the database audit log.
- [ ] **REV-06**: Ensure all security measures (CSRF, secure cookies/session, rate limiting, size limits) apply to the revert upload endpoint.
- [ ] **REV-07**: Handle malformed, corrupted, or mismatched files and mappings gracefully with detailed user-friendly error messages.

## v2 Requirements

### Advanced Reversion

- **REV-V2-01**: Support encrypted reversion mapping files using a user-specified secret key/passphrase.
- **REV-V2-02**: Support partial column reversion (reverting only selected columns from a fully masked file).

## Out of Scope

| Feature | Reason |
|---------|--------|
| Server-side persistence of mapping files | Violates zero-knowledge and privacy compliance (never store PII on server) |
| Multi-file bulk reversion in a single job | Out of scope for v1 MVP; single file reversion is sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REV-01 | Phase 9 | Pending |
| REV-02 | Phase 9 | Pending |
| REV-03 | Phase 10 | Pending |
| REV-04 | Phase 9 | Pending |
| REV-05 | Phase 10 | Pending |
| REV-06 | Phase 10 | Pending |
| REV-07 | Phase 9 & 10 | Pending |

**Coverage:**
- v1 requirements: 7 total
- Mapped to phases: 7
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-19*
*Last updated: 2026-07-19 after initial definition*
