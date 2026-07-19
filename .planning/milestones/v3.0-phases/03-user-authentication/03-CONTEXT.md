# Phase 3: User Authentication - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementasi registrasi pengguna, login, logout, dan manajemen sesi aman menggunakan JWT. Mengintegrasikan otentikasi di sisi backend dengan basis data SQLite lokal menggunakan SQLModel, serta mengaktifkan antarmuka login/register di frontend React melalui state-based rendering (kondisional halaman).

</domain>

<decisions>
## Implementation Decisions

### Frontend Navigation & Redirection
- **D-01:** **State-based conditional rendering**: Frontend navigation menggunakan switch view berbasis state React langsung di dalam `App.tsx` (kondisional layout), menjaga kesederhanaan struktur tanpa perlu memasang library routing tambahan seperti `react-router-dom`.
- **D-02:** **App-level barrier**: Batasan akses diatur di level aplikasi utama. Halaman login/register ditampilkan terlebih dahulu secara penuh; pengguna harus login sebelum diizinkan mengakses layar unggah (Dropzone), pratinjau (Preview), dan pemrosesan masking.

### JWT Session Token Management
- **D-03:** **LocalStorage client storage**: Token JWT disimpan pada `LocalStorage` peramban pengguna agar sesi tetap aktif setelah halaman di-refresh.
- **D-04:** **JWT Expiration**: Masa kedaluwarsa token JWT ditetapkan selama 24 jam untuk menyeimbangkan kenyamanan pengguna lokal dengan aspek keamanan dasar.

### Database Engine & ORM
- **D-05:** **SQLModel ORM**: Seluruh model data pengguna dan akses database di backend diimplementasikan menggunakan SQLModel (integrasi Pydantic + SQLAlchemy) demi keselarasan tipe data dengan FastAPI.
- **D-06:** **File-based SQLite**: Database menggunakan SQLite berbasis berkas fisik lokal. Jalur penyimpanannya dikonfigurasi melalui variabel lingkungan `.env` dengan fallback default ke `backend/datamask.db` untuk menjamin data pengguna tersimpan secara persisten lintas restart server backend.

### Password Validation & Hashing
- **D-07:** **Basic Length Check**: Aturan kompleksitas kata sandi minimal 8 karakter (tanpa aturan regex karakter khusus yang ketat) untuk menyederhanakan interaksi di lingkungan internal/lokal.
- **D-08:** **bcrypt Hashing**: Kata sandi di-hash secara aman menggunakan algoritma bcrypt (via library python `passlib` dengan backend `bcrypt`) sebelum disimpan ke database SQLite.

### the agent's Discretion
- AI diberikan fleksibilitas untuk mendesain gaya tampilan visual (form login/register tabbed dengan tab "Login" dan "Daftar") serta struktur internal file database (misalnya helper fungsi db session).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope & Guidelines
- [prd.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/prd.md) — Product Requirement Document (PRD) defining core goals and user flows.
- [erd.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/erd.md) — Entity Relationship Diagram for DB structure.
- [.planning/REQUIREMENTS.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/REQUIREMENTS.md) — Traceability matrix and detailed v1/v2 constraints.
- [.planning/ROADMAP.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/ROADMAP.md) — Phased milestone plan and success criteria.

### Prior Context
- [.planning/phases/01-foundation-preview-engine/01-CONTEXT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/phases/01-foundation-preview-engine/01-CONTEXT.md) — Phase 1 decisions and context.
- [.planning/phases/02-masking-engine-download/02-CONTEXT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/phases/02-masking-engine-download/02-CONTEXT.md) — Phase 2 decisions and context.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Pengaturan konfigurasi backend di [config.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/core/config.py) untuk memuat nilai `.env` (misalnya JWT Secret Key, Database URL, dan masa aktif JWT).
- Desain antarmuka modern bernuansa gelap di [App.tsx](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/App.tsx) dan utilitas CSS di `index.css`.

### Established Patterns
- Menggunakan skema validasi Pydantic / model data masukan/keluaran di backend.
- Pengorganisasian endpoint FastAPI dalam modul terpisah di bawah `backend/app/api/endpoints/`.

### Integration Points
- **Backend User Model**: Buat berkas model SQLModel untuk tabel pengguna di file baru `backend/app/models/user.py` (atau `backend/app/models.py`).
- **Backend Database Setup**: Buat berkas inisialisasi engine dan dependency session di file baru `backend/app/db.py` (atau folder `backend/app/db/`).
- **Backend Auth Router**: Hubungkan endpoint registrasi dan login baru (`backend/app/api/endpoints/auth.py`) ke router utama di `backend/app/api/api.py`.
- **Frontend Auth UI & Context**: Buat komponen `frontend/src/components/AuthForm.tsx` (atau sejenisnya) dan hubungkan state otentikasi di dalam `frontend/src/App.tsx` agar mengendalikan barrier akses.

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-User Authentication*
*Context gathered: 2026-07-19*
