# Codebase Concerns

**Analysis Date:** 2026-07-19

## Tech Debt

**None yet (Greenfield Project):**
- Since this is a new project initialization, there is no legacy code debt. Future developers should adhere to the architecture laid out in `ARCHITECTURE.md` and style conventions in `CONVENTIONS.md` to prevent accumulation of debt.

## Known Bugs

- None (No application code exists yet).

## Security Considerations

**In-Memory File Processing:**
- Risk: In-memory file processing could lead to Denial of Service (DoS) if a user uploads an extremely large file, causing the server to run out of RAM.
- Current mitigation: The PRD limits file sizes to 50MB (FR-1).
- Recommendations: Set strict payload size limits at the proxy/web server layer (e.g. Nginx, FastAPI middleware) and reject larger files before parsing starts.

**Information Leakage in Temp Buffers:**
- Risk: Remnants of PII (Personally Identifiable Information) could theoretically remain in RAM after processing a file.
- Current mitigation: Processing inside local function scopes to allow Python's garbage collector to release dataframe buffers.
- Recommendations: Explicitly call garbage collection `gc.collect()` or overwrite data frames in place before reference deletion if handling high-sensitivity data.

## Performance Bottlenecks

**Large Excel/CSV Parsing:**
- Problem: Reading files up to 50MB using `pandas` and `openpyxl` blocking the single-threaded Python event loop in FastAPI.
- Cause: Synchronous file CPU operations in pandas.
- Improvement path: Run file processing tasks in an async thread pool using FastAPI's `run_in_threadpool` or delegate to Celery workers if processing times exceed 5 seconds.

## Scaling Limits

**File Processing Thread Pool:**
- Current capacity: Single container can run a limited number of parallel CPU-intensive pandas dataframe mask tasks.
- Limit: RAM boundaries and CPU cores.
- Symptoms at limit: High CPU usage, out-of-memory container crashes, slow request times.
- Scaling path: Autoscale FastAPI backend containers horizontally using container orchestrators (e.g., AWS ECS, Kubernetes).

## Test Coverage Gaps

**Initial Project:**
- What's not tested: Everything (no code exists yet).
- Priority: High. Unit tests must be written concurrently with the implementation of the auth service and the masking engine.

---

*Concerns audit: 2026-07-19*
*Update as issues are fixed or new ones discovered*
