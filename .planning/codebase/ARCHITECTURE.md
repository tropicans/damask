# Architecture

**Analysis Date:** 2026-07-20

## Pattern Overview

**Overall:** Decoupled Single Page Application (SPA) and Stateless REST API.

**Key Characteristics:**
- **Decoupled separation of concerns:** React + Vite SPA on the frontend, FastAPI on the backend.
- **In-memory transient file processing:** Uploaded files are processed strictly in RAM buffers and never written to disk, preventing data leaks.
- **Stateless request handling:** Authenticated endpoints verify JWT signatures per request.
- **Strategy Pattern for masking rules:** Extensible architecture where each masking rule implements a specific mutation strategy on Pandas DataFrames.

## Layers

### Frontend View Layer
- Purpose: Render user interface, forms, preview tables, dashboards, and handle file uploads.
- Contains: React components (`frontend/src/App.tsx`, `frontend/src/components/*`).
- Depends on: Frontend API Client Layer.
- Used by: End user browser.

### Frontend API Client Layer
- Purpose: Abstract HTTP communication with the backend.
- Contains: Axios client configurations and endpoint request functions (`frontend/src/api/*`).
- Depends on: Axios.
- Used by: Frontend View Layer.

### Backend API Router Layer
- Purpose: Handle incoming HTTP requests, validate input schemas, authenticate requests, and route tasks to application services.
- Contains: FastAPI APIRouters, endpoint functions, CORS settings (`backend/app/api/*`).
- Depends on: Backend Service Layer, Models & Data Access Layer.
- Used by: Frontend API client.

### Backend Service Layer
- Purpose: Execute core business logic including file parsing, masking strategy application, column type detection, and authentication.
- Contains: Masking services, auto-detection service, parser utilities, user auth services (`backend/app/services/*`).
- Depends on: Models & Data Access Layer, third-party libraries (Pandas, Faker).
- Used by: Backend API Router Layer.

### Models & Data Access Layer
- Purpose: Manage database connections, execute SQL queries, and define schemas.
- Contains: DB engine setup, SQLModel class definitions (`backend/app/db.py`, `backend/app/models/*`).
- Depends on: SQLModel / SQLAlchemy.
- Used by: Backend Service Layer, Backend API Router Layer.

## Data Flow

### 1. File Upload & Column Auto-Detection
1. User selects a CSV or Excel file in the React frontend.
2. Frontend calls `POST /api/preview/preview` with the file via Axios.
3. FastAPI endpoint `backend/app/api/endpoints/preview.py` receives the file stream.
4. `parser.py` parses the file into a Pandas DataFrame in RAM using `io.BytesIO`.
5. `detector.py` runs regex-based rules to auto-detect columns containing names, emails, and phone numbers.
6. The API returns the first 3 rows as preview data alongside recommended masking strategies for each column.
7. Frontend renders the preview table with pre-selected recommendations in dropdown selectors.

### 2. Custom Masking & File Download
1. User configures/confirms the masking rules per column and clicks "Mask Data".
2. Frontend uploads the file and the rules mapping to `POST /api/mask/mask`.
3. FastAPI endpoint `backend/app/api/endpoints/mask.py` validates the request and token.
4. `masker.py` runs the `DataMasker` service, applying selected masking strategies column-by-column to the DataFrame.
5. The processed DataFrame is written into an output `io.BytesIO` buffer.
6. An audit log metadata record (row count, file size, columns masked) is saved to the database.
7. The output buffer is streamed back to the user via a FastAPI `StreamingResponse` (causing a file download in the browser).
8. Garbage collection immediately clears the memory buffers.

### State Management
- **Frontend State:** Managed via local React state (`useState`, `useContext`) to track current user session, uploaded files, and preview configurations.
- **Backend State:** The API is stateless; persistent metadata (users, masking jobs, job details) is stored in SQLite (dev) or PostgreSQL (prod).

## Key Abstractions

### Masking Strategy
- Purpose: Abstract class or function mapping a string value to a masked/synthetic value.
- Examples: Indonesian-localized `fake_name`, `fake_email`, `fake_phone`, `scramble_id` (consistent masking using local memory cache), `perturb_numeric` ($\pm 20\%$ variance).
- Pattern: Strategy Pattern.

### DataMasker
- Purpose: Coordinate the pandas DataFrame transformations using selected MaskingRules.
- Examples: `mask_dataframe` in `app/services/masker.py`.
- Pattern: Service Wrapper.

## Entry Points

### Frontend App
- Location: `frontend/src/main.tsx`
- Triggers: Browser loading the application.
- Responsibilities: Mount the React application, initialize global CSS, and set up routing/context providers.

### Backend App
- Location: `backend/app/main.py`
- Triggers: Uvicorn/Gunicorn startup.
- Responsibilities: Initialize FastAPI, set up CORS middleware, configure security headers, register rate limiters, mount routers, and initialize DB on startup.

## Error Handling

**Strategy:**
Services raise custom exceptions (e.g., `DataProcessingException`) or standard Python errors. The API Router catches exceptions and returns appropriate `HTTPException` responses with clear user-facing error messages.

**Patterns:**
- Try/catch blocks in backend endpoints catching processing and database exceptions.
- Structured JSON error responses (`{"detail": "Error message description"}`) returned to the client.
- Frontend Axios interceptors or local try/catch blocks catching API errors and displaying elegant UI toast notices.

## Cross-Cutting Concerns

**Logging:**
- Standard Python `logging` configured in `backend/app/core/logging.py`.
- Logs masking job executions (metadata only) at `INFO` level.
- Logs errors with stack traces at `ERROR` level.

**Validation:**
- Pydantic models in the backend for input payload validation (registration, login schemas).
- Pandas and openpyxl check file integrity on load.

**Authentication:**
- JWT Bearer tokens passed via headers or secure HTTP-only cookies.
- CSRF protection mechanisms configured on state-changing requests.

---

*Architecture analysis: 2026-07-20*
*Update when major patterns change*
