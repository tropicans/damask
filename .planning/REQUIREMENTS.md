# Requirements: SecureData Web

**Defined:** 2026-07-19
**Core Value:** Ensure sensitive data is masked safely and efficiently before it leaves the organization's secure perimeter.

## v1 Requirements

Requirements for the initial release, mapped directly to roadmap phases.

### File Management (FILE)

- [ ] **FILE-01**: User can upload tabular data files in `.csv`, `.xls`, and `.xlsx` formats.
- [ ] **FILE-02**: File size uploads are limited to 50MB maximum to prevent RAM overflow.
- [ ] **FILE-03**: Uploaded files are processed strictly in-memory (RAM buffer) and never written to permanent disk storage.
- [ ] **FILE-04**: User can download the processed masked file in its original file format (.csv or .xlsx).

### Column Preview & Recommendation (PREV)

- [ ] **PREV-01**: System parses the file to read column headers.
- [ ] **PREV-02**: System reads and displays the first 3 rows of data in the UI as a preview.
- [ ] **PREV-03**: System uses regex rules on column names to suggest default masking strategies.

### Masking Operations (MASK)

- [ ] **MASK-01**: User can select a specific masking rule for each column from a dropdown menu.
- [ ] **MASK-02**: Support **No Masking** (preserves the original column data).
- [ ] **MASK-03**: Support **Fake Name** (generates randomized Indonesian or global names).
- [ ] **MASK-04**: Support **Fake Email** (generates randomized fake email addresses).
- [ ] **MASK-05**: Support **Fake Phone** (generates randomized phone numbers).
- [ ] **MASK-06**: Support **Anonymize ID/Number** (scrambles digits and characters).
- [ ] **MASK-07**: Support **Perturb Numeric** (modifies numerical/financial values by a random factor within $\pm 20\%$).

### User Authentication (AUTH)

- [ ] **AUTH-01**: User can create an account with email and password.
- [ ] **AUTH-02**: User can log in with their email and password to start a session.
- [ ] **AUTH-03**: User session is maintained securely via JWT.
- [ ] **AUTH-04**: User can log out to terminate the session.

### Audit Logging & History (AUDT)

- [ ] **AUDT-01**: System records metadata for each masking job (user ID, original file name, file size, row count, and execution status).
- [ ] **AUDT-02**: System records which columns were masked and with what rules in each job.
- [ ] **AUDT-03**: User can view a dashboard displaying their personal masking job history.
- [ ] **AUDT-04**: Job history records contain only metadata and never store the actual contents of the files.

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Admin Dashboard (ADMN)

- **ADMN-01**: Admin can view aggregate usage statistics of the system (total files, total rows processed).
- **ADMN-02**: Admin can configure system-wide default regex mapping rules.

## Out of Scope

Explicitly excluded to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Cloud-based file storage | Violates primary local privacy and compliance constraint. |
| Third-party OAuth Login | Avoids external dependencies for the initial internal tool version. |
| Direct LLM Chat integration | Kept separate to focus purely on local masking and file outputs. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FILE-01 | Phase 1 | Pending |
| FILE-02 | Phase 1 | Pending |
| FILE-03 | Phase 1 | Pending |
| FILE-04 | Phase 1 | Pending |
| PREV-01 | Phase 1 | Pending |
| PREV-02 | Phase 1 | Pending |
| PREV-03 | Phase 1 | Pending |
| MASK-01 | Phase 2 | Pending |
| MASK-02 | Phase 2 | Pending |
| MASK-03 | Phase 2 | Pending |
| MASK-04 | Phase 2 | Pending |
| MASK-05 | Phase 2 | Pending |
| MASK-06 | Phase 2 | Pending |
| MASK-07 | Phase 2 | Pending |
| AUTH-01 | Phase 3 | Pending |
| AUTH-02 | Phase 3 | Pending |
| AUTH-03 | Phase 3 | Pending |
| AUTH-04 | Phase 3 | Pending |
| AUDT-01 | Phase 4 | Pending |
| AUDT-02 | Phase 4 | Pending |
| AUDT-03 | Phase 4 | Pending |
| AUDT-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-19*
*Last updated: 2026-07-19 after initial definition*
