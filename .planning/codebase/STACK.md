# Technology Stack

**Analysis Date:** 2026-07-20

## Languages

**Primary:**
- Python 3.11+ (currently running 3.11.14 in virtualenv) - Backend application code, services, and APIs
- TypeScript 5.x - Frontend application code (React components, state, API calls)

**Secondary:**
- JavaScript - Build and configuration tooling (Vite, PostCSS, Tailwind, ESLint)
- SQL - Database migrations and schema definitions

## Runtime

**Environment:**
- Python 3.11+ (Backend)
- Node.js 20.x (Frontend development and build)
- Browser runtime (Google Chrome, Firefox, Safari)

**Package Manager:**
- uv / pip / poetry - Python backend package management (`uv.lock` and `pyproject.toml` present)
- npm 10.x - Node.js frontend package management (`package-lock.json` present)

## Frameworks

**Core:**
- FastAPI 0.110+ - High-performance Python backend framework
- React 18.x - Modern frontend UI library
- Vite 5.x - Frontend build tool and development server

**Testing:**
- Pytest 9.x - Python backend unit and integration testing
- Vitest - React frontend unit and component testing

**Build/Dev:**
- TailwindCSS 3.x - Utility-first CSS framework for interface styling
- Oxlint - High-performance JavaScript/TypeScript linter
- PostCSS & Autoprefixer - CSS preprocessing

## Key Dependencies

**Critical:**
- pandas 3.0+ - Data manipulation and analysis (CSV/XLSX processing)
- openpyxl 3.1+ - Engine for reading and writing Excel (.xlsx) files
- Faker 40.x - Generating mock/synthetic data for masking
- SQLModel 0.0.39 - ORM for SQL database access (combines SQLAlchemy and Pydantic)
- PyJWT 2.13.0 - JSON Web Token implementation for authentication

**Infrastructure:**
- passlib 1.7.4 (with bcrypt) - Secure password hashing
- slowapi 0.1.10 - Rate limiting extension for FastAPI
- axios 1.6.8 - HTTP client for API communication
- lucide-react 0.363.0 - Modern icons for frontend UI

## Configuration

**Environment:**
- `.env` files for both backend and frontend environments
- Keys: `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`

**Build:**
- `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` - TypeScript compiler options
- `vite.config.ts` - Vite bundler settings
- `tailwind.config.js`, `postcss.config.js` - Tailwind and PostCSS configurations
- `pyproject.toml`, `uv.lock` - Python dependency declarations

## Platform Requirements

**Development:**
- Cross-platform (Windows, macOS, Linux)
- Docker - Optional local database containerization (e.g., PostgreSQL)

**Production:**
- Vercel/Netlify for Frontend SPA
- Docker Container / AWS ECS / Railway / Render for FastAPI Backend
- PostgreSQL or SQLite for persistent data

---

*Stack analysis: 2026-07-20*
*Update after major dependency changes*
