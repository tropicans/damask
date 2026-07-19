# Phase 10: Revert Interface & Auditing - Research

**Researched:** 2026-07-19
**Domain:** React/Vite (TSX), FastAPI, SQLModel/SQLite, Audit Log
**Confidence:** HIGH

<user_constraints>
## User Constraints (from 10-CONTEXT.md)

### Locked Decisions
- **D-01:** Place the "Revert Data" interface in a new top-level tab in the header navigation, matching the styling of "Masking Engine" and "Riwayat Audit" tabs in App.tsx.
- **D-02:** Access to the "Revert Data" tab is open to all authenticated users.
- **D-03:** Detailed validation and mismatch errors from the backend revert operation will be displayed in a red alert panel directly below the upload inputs in the Revert view.
- **D-04:** Create a separate `RevertJob` SQLModel and DB table to track data reversion metadata (including `id`, `user_id`, `file_name`, `file_size_bytes`, `row_count`, `execution_duration_ms`, `status`, `error_message`, and `created_at`). Reversion operations do not have column-level rules.
- **D-05:** Present revert execution records inside the "Riwayat Audit" tab by introducing a sub-navigation or toggle to switch between "Riwayat Masking" and "Riwayat Revert".
- **D-06:** Selecting detail info for a revert job in the dashboard displays a modal containing only metadata properties.
- **D-07:** Add an opt-in checkbox or switch in the masking configuration panel labeled "Generate Reversion Key" / "Buat Kunci Pemulihan".
- **D-08:** Successful masking will transition the UI to a dedicated "Success" view. If a reversion key was generated, the view will show download links for the packaged file (the ZIP containing both files) and a security warning advising the user to store the key safely.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REV-03 | Create a dedicated "Revert Data" page/tab in the React frontend UI allowing users to upload a masked file and its reversion mapping JSON file. | New tab UI in App.tsx using a file upload interface (similar to Dropzone.tsx but supporting two separate upload slots). |
| REV-05 | Record revert execution metadata (original file name, file size, row count, and execution time) in the database audit log. | `RevertJob` model definition in `app/models/job.py`, tracked inside `/api/mask/revert` using `time.perf_counter()`. |
| REV-06 | Ensure all security measures (CSRF, secure cookies/session, rate limiting, size limits) apply to the revert upload endpoint. | Enforced in `main.py` (CSRF/Headers) and `endpoints/mask.py` (limiters, file size guards). |
| REV-07 | Handle malformed, corrupted, or mismatched files and mappings gracefully with detailed user-friendly error messages. | Frontend catches error payload from `/api/mask/revert` and displays detailed red alert panels below inputs. |
</phase_requirements>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Revert Execution Audit Logging | API/Backend | DB | Logs execution metadata for revert requests. |
| Revert History UI View | Frontend SPA | API/Backend | Exposes paginated history list and metadata details in Audit Dashboard. |
| Masking Config Key Toggle | Frontend SPA | API/Backend | Pass `generate_key` parameter in Form data if checkbox is checked. |
| Success Download Interface | Frontend SPA | — | Dedicated success page displaying download trigger links and security tips. |
</architectural_responsibility_map>

<research_summary>
## Summary

This phase completes the Data Reversion Facility by integrating the frontend components, implementing backend revert audit logging, and expanding the audit dashboard.
Key technical updates include:
1. **Database & Log Retrieval**: Registering `RevertJob` in `models/job.py` and `db.py`, implementing paginated `/api/jobs/revert` and `/api/jobs/revert/stats` endpoints in `endpoints/jobs.py`.
2. **Revert Endpoint Update**: Intercepting `/api/mask/revert` execution to measure duration and write `RevertJob` logs on success/failure.
3. **Frontend Views & Nav**: Adding a "Revert Data" navigation tab to App.tsx, a success view for masking downloads (with ZIP extractor instructions and warnings), a dual dropzone upload panel for revert execution, and a sub-nav tab in the AuditDashboard.tsx showing Masking vs Reversion histories.
</research_summary>

## Standard Stack

### Core
- React 18.x
- FastAPI 0.110+
- SQLModel / SQLite
- Lucide React (for icons)

## Architecture Patterns

### Revert Job Data Model
```python
class RevertJob(SQLModel, table=True):
    __tablename__ = "revert_jobs"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    file_name: str = Field(nullable=False)
    file_size_bytes: int = Field(nullable=False)
    row_count: Optional[int] = Field(default=None)
    execution_duration_ms: int = Field(nullable=False)
    status: str = Field(nullable=False)  # "SUCCESS" or "FAILED"
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Anti-Patterns to Avoid
- **Hardcoding UI Tab access roles**: Keep the Revert Data tab accessible to *all* logged-in roles.
- **Double-logging/Double-buffering**: Ensure duration is captured around the CPU-intensive dataframe parsing and mapping; release file streams promptly to prevent memory leak issues.

## Code Examples

### Revert Job Audit Logging in API Endpoint
```python
import time

start_time = time.perf_counter()
row_count = None
status = "FAILED"
err_msg = None

try:
    # Processing DataFrame...
    row_count = len(df)
    status = "SUCCESS"
except Exception as e:
    err_msg = str(e)[:250]
    raise
finally:
    duration_ms = int((time.perf_counter() - start_time) * 1000)
    job = RevertJob(
        user_id=current_user.id,
        file_name=filename,
        file_size_bytes=file_size,
        row_count=row_count,
        execution_duration_ms=duration_ms,
        status=status,
        error_message=err_msg
    )
    session.add(job)
    session.commit()
```

## Validation Architecture

### Test Framework
- pytest (Backend)
- Vitest (Frontend)

### Phase Requirements → Test Map
- `test_revert_logging`: Verify `RevertJob` records are correctly created in DB during reversion.
- `test_revert_log_api`: Test `/api/jobs/revert` retrieves user's history and logs correctly.
- `test_revert_ui_renders`: Vitest checks the new "Revert Data" component and fields are present.

## Metadata
- **Confidence breakdown:** Standard stack (HIGH), Architecture (HIGH), Pitfalls (HIGH).
- **Research date:** 2026-07-19
- **Valid until:** 2026-08-19
