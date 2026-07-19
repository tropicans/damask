# Technology Stack

**Analysis Date:** 2026-07-19

## Languages

**Primary (Planned):**
- Python 3.11+ - Backend application code (FastAPI, Pandas, Faker)
- TypeScript 5.x - Frontend application code (React)

**Secondary:**
- JavaScript - Build and configuration tooling (Vite, Tailwind, ESLint)
- SQL - Database migrations and schema definitions

## Runtime

**Environment:**
- Python 3.11+ (Backend)
- Node.js 20.x (Frontend development and build)
- Browser runtime (Google Chrome, Firefox, Safari)

**Package Managers:**
- pip / poetry - Python backend package management
- npm 10.x - Node.js frontend package management

## Frameworks

**Core:**
- FastAPI 0.110+ - High-performance Python backend framework
- React 18.x - Modern frontend UI library
- Vite 5.x - Frontend build tool and development server

**Testing:**
- Pytest - Python backend unit and integration testing
- Vitest - React frontend unit and component testing

**Build/Dev:**
- TailwindCSS - Utility-first CSS framework for interface styling (if requested)
- ESLint & Prettier - Frontend code linting and formatting

## Key Dependencies

**Backend:**
- pandas - Data manipulation and analysis (CSV/XLSX processing)
- openpyxl - Engine for reading and writing Excel (.xlsx) files
- Faker - Generating mock/synthetic data for masking
- SQLAlchemy / SQLModel - ORM for SQL database access
- passlib & bcrypt - Secure password hashing

**Frontend:**
- axios - HTTP client for API communication
- lucide-react - Sleek modern icons
- shadcn/ui (Radix UI) - Premium accessible UI components

## Configuration

**Environment:**
- `.env` files for both backend and frontend environments
- Keys: `DATABASE_URL`, `JWT_SECRET_KEY`, `CORS_ALLOWED_ORIGINS`

**Build:**
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite bundler settings
- `pyproject.toml` or `requirements.txt` - Python dependencies configuration

## Platform Requirements

**Development:**
- Cross-platform (Windows, macOS, Linux)
- Docker - Optional local database containerization (e.g., PostgreSQL)

**Production:**
- Vercel/Netlify for Frontend SPA
- Docker Container / AWS ECS / Railway / Render for FastAPI Backend
- PostgreSQL or SQLite for lightweight persistent data

---

*Stack analysis: 2026-07-19*
*Update after major dependency changes*
