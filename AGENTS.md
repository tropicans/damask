<!-- GSD:project-start source:PROJECT.md -->

## Project

**SecureData Web**

SecureData Web is a local/internal web application that allows users to upload CSV, XLS, and XLSX files containing sensitive personal identifiable information (PII) or financial data, configure custom masking rules per column, and download a safely anonymized version of the file. The tool is designed to prevent data leakage to external LLMs and cloud systems by processing uploads strictly in-memory and logging only job execution metadata.

**Core Value:** Ensure sensitive data is masked safely and efficiently before it leaves the organization's secure perimeter.

### Constraints

- **Security**: Must process files in temporary RAM buffers only. Output streams must be deleted/collected immediately after transmission.
- **Tech Stack**: Backend in Python (FastAPI/Pandas/Faker), Frontend in React.js, Database SQLite (dev) / PostgreSQL (prod).
- **Performance**: Must handle up to 50MB files without memory leaks or excessive event-loop blocking on the single-threaded Python backend.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.11+ - Backend application code (FastAPI, Pandas, Faker)
- TypeScript 5.x - Frontend application code (React)
- JavaScript - Build and configuration tooling (Vite, Tailwind, ESLint)
- SQL - Database migrations and schema definitions

## Runtime

- Python 3.11+ (Backend)
- Node.js 20.x (Frontend development and build)
- Browser runtime (Google Chrome, Firefox, Safari)
- pip / poetry - Python backend package management
- npm 10.x - Node.js frontend package management

## Frameworks

- FastAPI 0.110+ - High-performance Python backend framework
- React 18.x - Modern frontend UI library
- Vite 5.x - Frontend build tool and development server
- Pytest - Python backend unit and integration testing
- Vitest - React frontend unit and component testing
- TailwindCSS - Utility-first CSS framework for interface styling (if requested)
- ESLint & Prettier - Frontend code linting and formatting

## Key Dependencies

- pandas - Data manipulation and analysis (CSV/XLSX processing)
- openpyxl - Engine for reading and writing Excel (.xlsx) files
- Faker - Generating mock/synthetic data for masking
- SQLAlchemy / SQLModel - ORM for SQL database access
- passlib & bcrypt - Secure password hashing
- axios - HTTP client for API communication
- lucide-react - Sleek modern icons
- shadcn/ui (Radix UI) - Premium accessible UI components

## Configuration

- `.env` files for both backend and frontend environments
- Keys: `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite bundler settings
- `pyproject.toml` or `requirements.txt` - Python dependencies configuration

## Platform Requirements

- Cross-platform (Windows, macOS, Linux)
- Docker - Optional local database containerization (e.g., PostgreSQL)
- Vercel/Netlify for Frontend SPA
- Docker Container / AWS ECS / Railway / Render for FastAPI Backend
- PostgreSQL or SQLite for lightweight persistent data

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- snake_case for all modules, variables, and functions (`auth_service.py`, `process_file()`).
- PascalCase for class definitions (`DataMasker`, `UserAuth`).
- UPPER_SNAKE_CASE for local/global constants (`MAX_FILE_SIZE_MB = 50`).
- PascalCase for React components and pages (`LoginPage.tsx`, `ToastNotification.tsx`).
- camelCase for utility functions, hooks, variables, and properties (`useAuth()`, `columnConfig`).
- kebab-case for config files, assets, and styling documents (`vite.config.ts`, `global-styles.css`).

## Code Style

- Follow PEP 8 guidelines.
- Use Black format (line length 88 or 100 characters).
- Type hints on all function parameters and return values:
- Prettier for auto-formatting (2-space tabs, single quotes, trailing commas, semicolons).
- ESLint with TypeScript recommendation rules enabled.
- Avoid using `any` type in TypeScript; always define explicit interfaces/types.

## Import Organization

## Error Handling

- Use HTTPException for standard API responses (e.g. 400 Bad Request, 401 Unauthorized).
- Wrap file-handling operations in try/catch blocks and raise custom service-level exceptions (e.g., `DataProcessingException`) to prevent raw pandas errors from escaping.
- Return structured error JSON models containing descriptive user error messages.
- Wrap API calls in try-catch structures inside hooks or controller functions.
- Catch API errors and display elegant Toast UI notices, rather than crashing page flow.

## Logging

- Use Python standard `logging` library configured in `app/core/logging.py`.
- Log incoming masking jobs (size, row count, column mappings) at `INFO` level.
- Log parsing errors or file upload failures at `ERROR` level with stack trace.
- Never write console logs or print statements in production code.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Pattern Overview

- Separation of Concerns: Decoupled frontend (Vite/React/TS) and backend (FastAPI/Python).
- Stateless API: Session management via JWT; no long-lived state stored on server except audit logs.
- Memory Buffer Processing: CSV/XLSX file uploads are processed entirely in memory (via Pandas and openpyxl) and streamed directly back to the user without persistent disk writes.

## Layers

- Purpose: Render user interface, handle file uploads, configure column masking options, and trigger downloads.
- Contains: React components, state, hooks, views, page layouts.
- Location: `frontend/src/`
- Depends on: Frontend API Client
- Used by: End user browser
- Purpose: Abstract network requests to backend services.
- Contains: Axios client configurations and API functions.
- Location: `frontend/src/api/`
- Depends on: None
- Used by: Frontend React components
- Purpose: Handle incoming HTTP requests, validate input schemas, authenticate users, and route tasks to application services.
- Contains: FastAPI APIRouter, endpoint functions, CORS settings.
- Location: `backend/app/api/`
- Depends on: Backend Service Layer, Models
- Used by: Frontend API client
- Purpose: Core logic for Excel/CSV parsing, regex-based column auto-detection, Faker masking, and exporting processed file streams.
- Contains: DataMasker service, AutoDetection service, User Auth service.
- Location: `backend/app/services/`
- Depends on: Database Access Layer, third-party libraries (pandas, faker)
- Used by: Backend API routes
- Purpose: Manage SQLite/PostgreSQL connection pools and execute SQL operations via SQLModel.
- Contains: DB engine setup, session helpers, database models.
- Location: `backend/app/db/`
- Depends on: Models (SQLModel definitions)
- Used by: Backend Service layer

## Data Flow

- Frontend: Local React state (useState, useContext) for UI preferences, uploading files, and preview configurations.
- Backend: Stateless. Audit log records and user accounts are persisted to SQLite/PostgreSQL, but files are processed transiently in RAM.

## Key Abstractions

- Purpose: Abstract class or protocol representing a specific masking technique (e.g. Fake Name, Perturb Numeric).
- Pattern: Strategy Pattern (each masking type has its own strategy handler).
- Purpose: Orchestrate pandas DataFrame transformations using selected MaskingRules.
- Pattern: Service Wrapper.

## Entry Points

- Location: `frontend/src/main.tsx`
- Triggers: Browser landing page load
- Responsibilities: Mount the React application and initialize routers.
- Location: `backend/app/main.py`
- Triggers: Uvicorn/Gunicorn startup
- Responsibilities: Initialize FastAPI application, mount middleware (CORS, Error Handlers), and include routers.

## Error Handling

- Try/catch blocks in backend endpoints catching Custom Exception classes (e.g., `FileProcessingError`, `AuthenticationError`).
- React error boundaries to prevent app crashes on UI render errors.

## Cross-Cutting Concerns

- Python standard `logging` configured in backend to write structured logs to stdout.
- Pydantic models in backend for endpoint request/response validation.
- Yup / Zod on frontend for form schemas (e.g., login, registration).

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
