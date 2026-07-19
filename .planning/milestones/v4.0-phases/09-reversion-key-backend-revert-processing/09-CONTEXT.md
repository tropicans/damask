# Phase 9: Reversion Key & Backend Revert Processing - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 9 focuses on generating a bijective 1-to-1 mapping during data masking (without storing any PII or mappings on the server), packaging and returning this mapping as a JSON key file alongside the masked data in an in-memory ZIP archive, and implementing backend in-memory processing to parse the masked file and apply the reversion mapping JSON to restore the original values. This covers backend endpoints, services, logic, and unit tests.
</domain>

<decisions>
## Implementation Decisions

### Reversion Key Format & Delivery
- **D-01:** When the user requests a reversion key during masking, the API packages both the masked file and the JSON reversion key in a `.zip` archive in-memory and streams it back. This conforms to the 50MB file size limit and zero-knowledge constraints without server-side disk writes.

### Bijectivity Enforcement on Collisions
- **D-02:** To guarantee a 1-to-1 bijective mapping of original values to masked values per column, the masking service checks for collisions. If a collision is detected during mapping generation, it retries generating the fake value up to 100 times. If still colliding, it appends a unique suffix (the original value or a unique counter) to ensure it is unique.

### Revert Endpoint Interface
- **D-03:** The new `/api/mask/revert` endpoint accepts a standard multipart/form-data upload containing two fields: `file` (the masked CSV or Excel file) and `key` (the JSON mapping key file).

### Mismatched Mapping Validation
- **D-04:** Strict Validation (Fail Fast). If any expected column is missing, or a masked value in the file does not exist in the mapping key, the backend aborts the operation, raises a 400 Bad Request, and returns a detailed list of mismatched columns or values to prevent data corruption or partial leakages.

### Agent's Discretion
- None. Decisions were fully locked during discussion.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- [.planning/ROADMAP.md](file:///.planning/ROADMAP.md) — Defines milestones, phase goals, and success criteria.
- [.planning/REQUIREMENTS.md](file:///.planning/REQUIREMENTS.md) — Lists requirements REV-01, REV-02, REV-04, and REV-07.

### API & Design Documentation
- [docs/API-SPEC.md](file:///docs/API-SPEC.md) — The application's HTTP API specifications.
- [docs/ARCHITECTURE.md](file:///docs/ARCHITECTURE.md) — The application's architecture overview.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- [mask_dataframe](file:///backend/app/services/masker.py#L106-L143): Can be updated or wrapped in a new service helper `mask_dataframe_with_key` to support generating the 1-to-1 bijective mapping while reusing the existing strategy rule applications.
- [mask_file](file:///backend/app/api/endpoints/mask.py#L37-L218): Can be updated to support an optional `generate_key: bool` Form field and package the ZIP stream.

### Established Patterns
- **In-memory File Processing**: All operations run transiently in memory (using `io.BytesIO`, `pandas`, `openpyxl`) and stream response back immediately, logging only job execution metadata without persisting files.
- **Double Submit CSRF Cookie & Rate Limiting**: Apply to the new `/api/mask/revert` endpoint.

### Integration Points
- `/api/mask/revert` to be added in [mask.py](file:///backend/app/api/endpoints/mask.py) or a separate endpoints file under [backend/app/api/endpoints/](file:///backend/app/api/endpoints/).
</code_context>

<specifics>
## Specific Ideas

- No specific requirements — open to standard approaches.
</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope.
</deferred>

---

*Phase: 9-Reversion Key & Backend Revert Processing*
*Context gathered: 2026-07-19*
