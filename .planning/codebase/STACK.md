# Technology Stack

**Mapped Date:** 2026-07-20

## Languages & Runtimes

- **Python 3.11+** (`backend/pyproject.toml`) - High-performance backend application runtime.
- **TypeScript 5.x** (`frontend/package.json`) - Typed frontend UI application logic.
- **Node.js 20.x/22.x** - Development runtime and frontend Vite build tool.
- **SQL** - Database schema definition and data persistence via SQLModel.

## Frameworks & Build Tools

- **FastAPI 0.110+** (`backend/app/main.py`) - High-performance async Python backend framework.
- **React 18.3+** (`frontend/src/App.tsx`) - Modern UI component library.
- **Vite 5.x** (`frontend/vite.config.ts`) - Fast frontend build tool & development server.
- **TailwindCSS 3.4+** (`frontend/tailwind.config.js`) - Utility-first CSS styling framework.

## Core Backend Dependencies

- **Pandas 2.2+** (`backend/app/services/parser.py`) - Tabular data manipulation and CSV/XLSX parsing.
- **openpyxl 3.1+** - Excel (.xlsx) read/write engine for Pandas.
- **SQLModel 0.0.39** (`backend/app/db.py`) - Unified SQLAlchemy ORM & Pydantic data modeling.
- **Faker 40.31+** (`backend/app/services/masker.py`) - Realistic synthetic data generation.
- **Cryptography 49.0+** (`backend/app/services/reversion.py`) - Fernet symmetric encryption for reversion keys.
- **PyJWT & Passlib / bcrypt** (`backend/app/services/auth.py`) - Secure password hashing & JWT token generation.
- **slowapi 0.1.9** (`backend/app/core/limiter.py`) - Rate-limiting middleware for auth endpoints.
- **psycopg2-binary 2.9+** - PostgreSQL database driver for production environment.

## Core Frontend Dependencies

- **Axios 1.6+** (`frontend/src/api/client.ts`) - HTTP client with CSRF header interceptor and 401 handling.
- **lucide-react** (`frontend/src/components/`) - Modern iconography.

## Testing & Quality Assurance

- **pytest 9.1+** (`backend/app/tests/`) - Comprehensive backend unit and endpoint integration testing suite.
- **Node Test Runner** (`frontend/src/utils/formatError.test.js`) - Native Node 22 test runner for frontend utility validation.
