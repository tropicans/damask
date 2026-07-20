# Directory Structure & File Layout

**Mapped Date:** 2026-07-20

## Repository Root

```text
c:\Users\yudhiar\Downloads\oprek\Dev\damask\
├── .agents/                 # Project GSD workflows and skill declarations
├── .planning/               # GSD project documentation, milestones, state, and codebase map
│   ├── codebase/            # Mapped reference documents (STACK, ARCHITECTURE, STRUCTURE, etc.)
│   ├── milestones/          # Archived historical milestone documentation (v1.0 - v5.0)
│   ├── phases/              # Phase-specific execution plans and contextual context files
│   ├── PROJECT.md           # Core project description, guidelines, and key decision log
│   ├── ROADMAP.md           # Milestone roadmap tracking
│   └── STATE.md             # Current project execution state
├── backend/                 # FastAPI Python backend service
├── frontend/                # Vite React TypeScript frontend web application
├── nginx/                   # Reverse proxy configuration for production environment
├── sample_nasabah.csv       # Test dataset (Customer data with PII)
├── sample_karyawan.csv      # Test dataset (Employee payroll data)
├── docker-compose.yml       # Docker Compose definition for development environment
├── docker-compose.prod.yml  # Docker Compose definition for production environment
├── AGENTS.md                # Project-level conventions, architecture, and GSD enforcement rules
└── README.md                # Overall project summary and getting started guide
```

## Backend Layout (`backend/`)

```text
backend/
├── app/
│   ├── api/
│   │   ├── api.py           # Includes all endpoint routers under /api
│   │   └── endpoints/
│   │       ├── admin.py     # User management & audit log endpoints (Admin only)
│   │       ├── auth.py      # Registration, login, invite creation, logout, /me
│   │       └── jobs.py      # Preview, mask execution, revert, and audit log endpoints
│   ├── core/
│   │   ├── config.py        # Pydantic Settings loading environment variables
│   │   ├── limiter.py       # SlowAPI rate limiter setup
│   │   └── logging.py       # Python standard logging configuration
│   ├── models/
│   │   ├── job.py           # SQLModel schemas for MaskingJob, JobDetail, RevertJob
│   │   └── user.py          # SQLModel schemas for User, Invite, LoginAudit
│   ├── services/
│   │   ├── auth.py          # Password hashing, JWT token verification, IP lockout logic
│   │   ├── detector.py      # Regex & heuristic auto-detection for PII columns
│   │   ├── masker.py        # Strategy pattern masking implementations (Faker, Redact, etc.)
│   │   ├── parser.py        # Pandas & openpyxl CSV/XLSX IO buffer processing
│   │   └── reversion.py     # Symmetric Fernet encryption key generation & file restoration
│   ├── tests/               # Pytest suite (12 test modules covering 107 test cases)
│   ├── db.py                # Database connection, foreign key pragmas, & auto-seed logic
│   └── main.py              # FastAPI app setup, exception handlers, and security middleware
├── datamask.db              # SQLite development database file
├── Dockerfile               # Backend Docker build specification
├── pyproject.toml           # Poetry package declaration and dependencies
└── uv.lock                  # Lockfile for uv dependency resolution
```

## Frontend Layout (`frontend/`)

```text
frontend/
├── src/
│   ├── api/
│   │   ├── admin.ts         # Admin API client calls (users, roles, status, audits)
│   │   ├── auth.ts          # Auth API client calls (login, register, invite, /me)
│   │   ├── client.ts        # Axios base client, CSRF header interceptor, 401 callback
│   │   └── jobs.ts          # Preview, masking execution, and revert API client calls
│   ├── components/
│   │   ├── AuditDashboard.tsx # Compliance statistics and job/login audit table
│   │   ├── AuthForm.tsx       # Login and invite-based registration form
│   │   ├── Dropzone.tsx       # Drag-and-drop file upload component
│   │   ├── PreviewTable.tsx   # Data grid with per-column rule selection dropdowns
│   │   └── UserManagement.tsx # Admin user status toggle and role management modal
│   ├── utils/
│   │   ├── formatError.ts     # FastAPI error detail string extractor
│   │   └── formatError.test.js# Native Node test runner suite for formatError
│   ├── App.tsx              # Root React component managing navigation and global state
│   ├── main.tsx             # React DOM root mounting script
│   └── index.css            # Tailwind CSS directives and global styles
├── index.html               # Main SPA HTML container
├── package.json             # NPM package declaration, scripts, and dependencies
├── tailwind.config.js       # Tailwind CSS theme configuration
├── tsconfig.json            # TypeScript configuration root
└── vite.config.ts           # Vite bundler configuration
```
