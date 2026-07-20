# Codebase Structure

**Analysis Date:** 2026-07-20

## Directory Layout

```
damask/
├── .agents/            # GSD agent scripts, workflows, and templates
├── .planning/          # Project planning docs (roadmaps, states, phases, codebase)
├── backend/            # FastAPI Python backend application
│   ├── app/            # Main application source code
│   │   ├── api/        # API routers and endpoints
│   │   ├── core/       # Logging, security limiters, config
│   │   ├── models/     # SQLModel tables (user, job)
│   │   ├── services/   # DataMasker, auth, detector, parser services
│   │   └── tests/      # Pytest test cases
│   ├── pyproject.toml  # Poetry dependencies file
│   └── uv.lock         # uv lockfile
├── docs/               # Architecture, API specifications, and deployment guides
└── frontend/           # Vite + React + TS frontend application
    ├── public/         # Public static assets
    ├── src/            # React source code
    │   ├── api/        # Axios API clients
    │   ├── assets/     # Images/icons
    │   ├── components/ # Reusable UI components
    │   ├── App.tsx     # Main application layout and routing
    │   └── main.tsx    # React entry mount point
    ├── package.json    # Frontend dependency declaration
    └── vite.config.ts  # Vite bundler config
```

## Directory Purposes

**.agents/**
- Purpose: System-level GSD configurations and scripts
- Contains: Workflow templates, custom tool integration hooks, and configurations
- Key files: `mcp_config.json`, `settings.json`

**.planning/**
- Purpose: Project roadmap, milestone specifications, and active phase plan tracking
- Contains: Roadmap, Project state, phase plan markdown files, and codebase documentation
- Subdirectories: `codebase/`, `milestones/`, `phases/`

**backend/app/**
- Purpose: FastAPI backend service codebase
- Contains: API route definitions, database ORM models, business logic services, and testing suites
- Subdirectories: `api/`, `core/`, `models/`, `services/`, `tests/`

**frontend/src/**
- Purpose: Frontend single page application codebase
- Contains: React components, axios clients, local stylesheets, and layout controllers
- Key files: `App.tsx` (main router/view controller), `main.tsx` (virtual DOM mounting)
- Subdirectories: `api/`, `assets/`, `components/`

## Key File Locations

**Entry Points:**
- `backend/app/main.py` - FastAPI app initialization, middleware loading, and routes mounting
- `frontend/src/main.tsx` - Vite frontend client mounting

**Configuration:**
- `backend/app/core/config.py` - Configuration class and env var settings using `pydantic-settings`
- `frontend/vite.config.ts` - Vite compilation and bundler configuration
- `backend/pyproject.toml` - Backend Poetry package manifest
- `frontend/package.json` - Frontend npm package manifest

**Core Logic:**
- `backend/app/services/masker.py` - Core df masking executor using Strategy Pattern
- `backend/app/services/detector.py` - Regex-based name, email, and phone column auto-detectors
- `backend/app/db.py` - SQLModel database engine and session setup

**Testing:**
- `backend/app/tests/` - Backend pytest suite directory
- `backend/app/tests/conftest.py` - Pytest fixtures and mock database overrides

**Documentation:**
- `docs/ARCHITECTURE.md` - High-level architectural specification
- `docs/API-SPEC.md` - HTTP endpoint parameters and JSON schemas
- `docs/DEPLOYMENT.md` - Production configuration and setup guidelines

## Naming Conventions

**Files:**
- `snake_case.py` for Python modules, variables, and utility helper files (`auth_service.py`)
- `PascalCase.tsx` / `PascalCase.ts` for React components and class structures (`LoginPage.tsx`)
- `camelCase.ts` for frontend hooks, utilities, and helper scripts (`useAuth.ts`)
- `test_*.py` for backend pytest files (`test_auth.py`)
- `kebab-case.*` for configuration and setup files (`tailwind.config.js`)

**Directories:**
- `snake_case` for backend directories (`api`, `core`, `models`, `services`)
- `camelCase` or `kebab-case` for frontend directories (`components`, `api`)

## Where to Add New Code

**New Feature:**
- Implement backend services under `backend/app/services/`.
- Wire frontend components under `frontend/src/components/` and connect them to API clients.

**New API Route:**
- Define endpoint endpoints under `backend/app/api/endpoints/`.
- Mount the router path in `backend/app/api/api.py`.
- Define backend schemas or models if database persistence is needed in `backend/app/models/`.

**New Masking Strategy:**
- Define df masking mutation helper function under `backend/app/services/masker.py`.
- Map the strategic rule name to the strategy function in the `mask_dataframe` selector block.

**Utilities:**
- Put general purpose functions in `backend/app/core/` (backend) or `frontend/src/api/` (frontend helper hooks).

---

*Structure analysis: 2026-07-20*
*Update when directory structure changes*
