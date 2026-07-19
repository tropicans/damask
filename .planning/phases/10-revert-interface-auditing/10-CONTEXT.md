# Phase 10: Revert Interface & Auditing - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 10 implements the UI features and backend logging for the data reversion facility. This includes:
1. Adding a new "Revert Data" navigation tab to the header (reusing App.tsx nav styles) accessible to all authenticated users.
2. Building the "Revert Data" view with drag-and-drop file inputs (masked file and reversion key JSON), and showing detailed validation/mismatch errors directly below the inputs.
3. Implementing opt-in "Generate Reversion Key" checkbox/switch in the masking configuration panel.
4. Transitioning to a dedicated "Success" screen upon successful masking, containing separate download buttons and a security warning.
5. Creating a new `RevertJob` database table/model to log metadata for revert operations (duration in ms, file name, size, row count, status, error).
6. Adding a sub-navigation/toggle in the Audit Dashboard to view masking logs vs reversion logs, with a detailed metadata modal for revert details.
</domain>

<decisions>
## Implementation Decisions

### Revert UI & Navigation
- **D-01:** Place the "Revert Data" interface in a new top-level tab in the header navigation, matching the styling of "Masking Engine" and "Riwayat Audit" tabs in App.tsx.
- **D-02:** Access to the "Revert Data" tab is open to all authenticated users (similar to the "Masking Engine").
- **D-03:** Detailed validation and mismatch errors from the backend revert operation (such as missing columns or values) will be displayed to the user in a red alert panel directly below the upload dropzones/upload inputs in the Revert view.

### Revert Audit Logging
- **D-04:** Create a separate `RevertJob` SQLModel and DB table to track data reversion metadata (including `id`, `user_id`, `file_name`, `file_size_bytes`, `row_count`, `execution_duration_ms`, `status`, `error_message`, and `created_at`). Reversion operations do not have column-level rules to log.
- **D-05:** Present revert execution records inside the "Riwayat Audit" tab by introducing a sub-navigation or toggle to switch between "Riwayat Masking" (Masking History) and "Riwayat Revert" (Reversion History).
- **D-06:** Selecting detail info for a revert job in the dashboard displays a modal containing only metadata properties (File name, size, row count, status, created time, and execution duration in ms) with no column-rule tables.

### Reversion Key Delivery
- **D-07:** Add an opt-in checkbox or switch in the masking configuration panel labeled "Generate Reversion Key" / "Buat Kunci Pemulihan".
- **D-08:** Successful masking will transition the UI to a dedicated "Success" view. If a reversion key was generated, the view will show download links for the packaged file (the ZIP containing both files) and a security warning advising the user to store the key safely.

### the agent's Discretion
- None. Decisions were fully aligned during the discussion.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- [.planning/ROADMAP.md](file:///.planning/ROADMAP.md) — Defines milestones, phase goals, and success criteria.
- [.planning/REQUIREMENTS.md](file:///.planning/REQUIREMENTS.md) — Lists requirements REV-03, REV-05, REV-06, and REV-07.

### API & Design Documentation
- [docs/API-SPEC.md](file:///docs/API-SPEC.md) — The application's HTTP API specifications.
- [docs/ARCHITECTURE.md](file:///docs/ARCHITECTURE.md) — The application's architecture overview.
- [backend/app/api/endpoints/mask.py](file:///backend/app/api/endpoints/mask.py) — Contains the `/api/mask/revert` and `/api/mask` endpoint implementations from Phase 9.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- [Dropzone.tsx](file:///frontend/src/components/Dropzone.tsx): Can be reused or duplicated for uploading the masked file and reversion key JSON.
- [AuditDashboard.tsx](file:///frontend/src/components/AuditDashboard.tsx): The structure and layout can be used to add the toggle and list the reversion logs.

### Established Patterns
- **Role-based Tabs**: Nav tabs check user role in `App.tsx` (e.g. `user.role === 'admin'`). The new Revert tab is open to all roles.
- **In-memory Stream Processing**: Revert endpoint is accessed in-memory.

### Integration Points
- `frontend/src/App.tsx` to handle the tab navigation, success screen rendering, and masking config page checkboxes.
- `backend/app/api/endpoints/mask.py` to add `RevertJob` logging when reversion runs.
- `backend/app/models/job.py` to add `RevertJob` schema.
- `backend/app/db.py` to import and create the new table.
- `backend/app/api/endpoints/jobs.py` to add `/revert` log retrieval endpoints.
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

*Phase: 10-Revert Interface & Auditing*
*Context gathered: 2026-07-19*
