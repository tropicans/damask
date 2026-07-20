# Technical Debt, Known Issues & Security Concerns

**Mapped Date:** 2026-07-20

## 1. Domain & Email Validation Behavior

### RFC 6762 Reserved TLD Validation (`.local`)
- **Issue:** Pydantic's `EmailStr` uses `email-validator`, which strictly rejects mDNS special-use TLDs such as `.local` according to IETF RFC 6762.
- **Impact:** Registering or logging in with email addresses ending in `.local` (e.g. `admin@securedata.local`) returns an HTTP 422 validation error.
- **Mitigation:** Default seeded accounts use standard TLDs (`admin@securedata.com`, `user@securedata.com`). Documentation instructs users to use `.com`, `.org`, or standard enterprise domain extensions.

## 2. In-Memory Buffer Memory Pressure

### Processing Large Files (>50MB)
- **Risk:** Files are processed transiently in RAM via Pandas dataframes and `openpyxl`. If multiple users concurrently upload 50MB+ files, RAM consumption on the backend Uvicorn process will spike.
- **Mitigation:** Pydantic payload size checks and file size limits enforce maximum upload thresholds. Intermediate bytes buffers (`io.BytesIO`) are released to garbage collection immediately after streaming the HTTP response back to the client.

## 3. Database Concurrency & Production Migration

### SQLite vs PostgreSQL
- **Development:** Uses SQLite (`backend/datamask.db`) with `check_same_thread=False` and foreign key PRAGMA enforcement.
- **Production:** Requires PostgreSQL (`docker-compose.prod.yml`) with `psycopg2-binary` driver to handle concurrent connection pooling across multi-worker Uvicorn or Gunicorn deployments.

## 4. Reversion Key Storage Security

### Client-Side Reversion Key Loss Risk
- **Design Intent:** Reversion key JSON files are generated client-side inside the downloaded ZIP package and **are never stored on the server** to guarantee zero data leakage.
- **Trade-off:** If the user loses the downloaded `reversion_key_XXXX.json` file, restoring the original raw dataset is mathematically impossible. This is an intentional privacy feature, but requires user awareness.

## 5. Docker Desktop Windows Daemon Warm-up

### Cold Start Delay on Windows
- **Issue:** Starting Docker Desktop via terminal (`Start-Process`) on Windows may take 15–30 seconds to initialize the `dockerDesktopLinuxEngine` named pipe backend.
- **Mitigation:** Added diagnostic steps (`wsl --shutdown` and service check) and clear user guidance when Docker engine cold-start is detected.
