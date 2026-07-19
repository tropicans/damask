# Codebase Structure

**Analysis Date:** 2026-07-19

## Directory Layout

```
datamask/
├── backend/                  # FastAPI backend server
│   ├── app/                  # Application source code
│   │   ├── api/              # API endpoints and routers
│   │   ├── core/             # Configuration, security, JWT helpers
│   │   ├── db/               # Database connection and session management
│   │   ├── models/           # SQLModel/Pydantic schemas and database models
│   │   └── services/         # Masking engine, Pandas helpers, Faker logic
│   ├── tests/                # Backend unit and integration tests
│   ├── Dockerfile            # Container build for backend
│   ├── pyproject.toml        # Poetry/Pip dependencies definition
│   └── requirements.txt      # Python dependencies list
├── frontend/                 # Vite/React frontend application
│   ├── src/                  # React source files
│   │   ├── api/              # API client functions (axios/fetch wrappers)
│   │   ├── components/       # Reusable UI components (drag-and-drop, dropdowns)
│   │   ├── context/          # React Context (authentication state, app state)
│   │   ├── layouts/          # Page layouts (Navbar, AppWrapper)
│   │   ├── pages/            # View pages (Login, Dashboard, AuditLogs)
│   │   └── main.tsx          # React application entry point
│   ├── Dockerfile            # Container build for frontend
│   ├── package.json          # Node package manifest
│   ├── vite.config.ts        # Vite configuration file
│   └── tsconfig.json         # TypeScript compiler configurations
├── docker-compose.yml        # Orchestrates backend, frontend, and database
├── prd.md                    # Product Requirements Document
├── erd.md                    # Entity Relationship Diagram
└── .planning/                # GSD planning and state tracking directory
    └── codebase/             # Automated codebase analysis documents
```

## Directory Purposes

**backend/app/api/**
- Purpose: HTTP endpoint routing and request payload validation.
- Contains: `auth.py` (login/register endpoints), `jobs.py` (file uploads, preview, and execution endpoints).
- Key files: `routes.py` - main APIRouter aggregator.

**backend/app/services/**
- Purpose: Implementation of core business logic.
- Contains: `masker.py` (Pandas + Faker data masking engine), `detector.py` (auto-detect rules based on column name regex).

**frontend/src/components/**
- Purpose: UI components reused across pages.
- Contains: `DragDropUpload.tsx` (handles file drag and drop), `MaskingConfigTable.tsx` (renders column config selectors), `PreviewTable.tsx` (renders first 3 rows preview).

**frontend/src/pages/**
- Purpose: Major router page locations.
- Contains: `LoginPage.tsx` (Auth interface), `DashboardPage.tsx` (File uploading and configuration), `AuditPage.tsx` (Job history list).

## Key File Locations

**Entry Points:**
- `backend/app/main.py` - Backend FastAPI server bootstrap.
- `frontend/src/main.tsx` - Frontend React/Vite client entry point.

**Configuration:**
- `backend/app/core/config.py` - Python settings management using Pydantic Settings.
- `frontend/vite.config.ts` - Vite bundler and proxy configurations.
- `docker-compose.yml` - Multi-container orchestration parameters.

**Testing:**
- `backend/tests/` - Backend test suite.
- `frontend/src/__tests__/` - Component and helper unit tests.

## Naming Conventions

**Files:**
- snake_case.py: Python backend source files (e.g. `data_masker.py`).
- kebab-case.ts: TypeScript frontend utility modules (e.g. `api-client.ts`).
- PascalCase.tsx: React functional components and pages (e.g. `DragDropUpload.tsx`).

**Directories:**
- snake_case: Backend folders.
- kebab-case: Frontend folders.

## Where to Add New Code

**New Masking Strategy:**
- Implementation: Add to `backend/app/services/strategies.py` or create a new file in that directory.
- Test: Add test case in `backend/tests/test_strategies.py`.

**New UI Component:**
- Implementation: Add to `frontend/src/components/` in PascalCase.
- Test: Alongside the component or in `frontend/src/__tests__/components/`.

**New Database Audit Log Column:**
- Model definition: Update `backend/app/models/job.py`.
- Migration: Run alembic revision command inside backend container.

---

*Structure analysis: 2026-07-19*
*Update when directory structure changes*
