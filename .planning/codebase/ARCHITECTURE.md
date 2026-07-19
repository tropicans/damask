# Architecture

**Analysis Date:** 2026-07-19

## Pattern Overview

**Overall:** Client-Server Single Page Application (React SPA frontend + FastAPI REST API backend)

**Key Characteristics:**
- Separation of Concerns: Decoupled frontend (Vite/React/TS) and backend (FastAPI/Python).
- Stateless API: Session management via JWT; no long-lived state stored on server except audit logs.
- Memory Buffer Processing: CSV/XLSX file uploads are processed entirely in memory (via Pandas and openpyxl) and streamed directly back to the user without persistent disk writes.

## Layers

**Frontend Presentation Layer (UI):**
- Purpose: Render user interface, handle file uploads, configure column masking options, and trigger downloads.
- Contains: React components, state, hooks, views, page layouts.
- Location: `frontend/src/`
- Depends on: Frontend API Client
- Used by: End user browser

**Frontend API Client:**
- Purpose: Abstract network requests to backend services.
- Contains: Axios client configurations and API functions.
- Location: `frontend/src/api/`
- Depends on: None
- Used by: Frontend React components

**Backend API Layer (HTTP routes):**
- Purpose: Handle incoming HTTP requests, validate input schemas, authenticate users, and route tasks to application services.
- Contains: FastAPI APIRouter, endpoint functions, CORS settings.
- Location: `backend/app/api/`
- Depends on: Backend Service Layer, Models
- Used by: Frontend API client

**Backend Service Layer (Business Logic):**
- Purpose: Core logic for Excel/CSV parsing, regex-based column auto-detection, Faker masking, and exporting processed file streams.
- Contains: DataMasker service, AutoDetection service, User Auth service.
- Location: `backend/app/services/`
- Depends on: Database Access Layer, third-party libraries (pandas, faker)
- Used by: Backend API routes

**Database Access Layer (Data Persistence):**
- Purpose: Manage SQLite/PostgreSQL connection pools and execute SQL operations via SQLModel.
- Contains: DB engine setup, session helpers, database models.
- Location: `backend/app/db/`
- Depends on: Models (SQLModel definitions)
- Used by: Backend Service layer

## Data Flow

**File Masking Request Workflow:**

1. User uploads a `.csv` or `.xlsx` file via the React drag-and-drop dashboard.
2. React parses the first few lines using a lightweight client library or uploads it to a `/preview` backend endpoint.
3. The backend preview endpoint loads the file into a Pandas DataFrame, extracts the first 3 rows as samples, runs regex checks to recommend masking rules, and returns the metadata and preview.
4. User selects masking rules for each column in the UI dropdown and clicks "Start Masking".
5. React sends the file along with the JSON config of masking rules to backend `/mask` endpoint.
6. The backend `/mask` endpoint streams the file into a memory buffer, maps the columns using the DataMasker service (which applies Faker and perturbation functions), writes the output into a new memory stream, logs the job metadata to the DB, and streams the file back to the browser.
7. User's browser triggers an automatic download of the masked file.

**State Management:**
- Frontend: Local React state (useState, useContext) for UI preferences, uploading files, and preview configurations.
- Backend: Stateless. Audit log records and user accounts are persisted to SQLite/PostgreSQL, but files are processed transiently in RAM.

## Key Abstractions

**MaskingRule:**
- Purpose: Abstract class or protocol representing a specific masking technique (e.g. Fake Name, Perturb Numeric).
- Pattern: Strategy Pattern (each masking type has its own strategy handler).

**DataMasker:**
- Purpose: Orchestrate pandas DataFrame transformations using selected MaskingRules.
- Pattern: Service Wrapper.

## Entry Points

**Frontend SPA:**
- Location: `frontend/src/main.tsx`
- Triggers: Browser landing page load
- Responsibilities: Mount the React application and initialize routers.

**Backend Server:**
- Location: `backend/app/main.py`
- Triggers: Uvicorn/Gunicorn startup
- Responsibilities: Initialize FastAPI application, mount middleware (CORS, Error Handlers), and include routers.

## Error Handling

**Strategy:** FastAPI exception handlers parse validation errors and return structured HTTP JSON responses. The frontend displays Toast notifications or alerts to the user based on error codes.

**Patterns:**
- Try/catch blocks in backend endpoints catching Custom Exception classes (e.g., `FileProcessingError`, `AuthenticationError`).
- React error boundaries to prevent app crashes on UI render errors.

## Cross-Cutting Concerns

**Logging:**
- Python standard `logging` configured in backend to write structured logs to stdout.

**Validation:**
- Pydantic models in backend for endpoint request/response validation.
- Yup / Zod on frontend for form schemas (e.g., login, registration).

---

*Architecture analysis: 2026-07-19*
*Update when major patterns change*
