# Phase 1: Foundation & Preview Engine - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement file upload management (CSV/XLSX), memory-only processing buffer, column header reading, first 3 rows preview display, and regex-based automatic masking recommendations. This includes setting up the FastAPI backend and React frontend.

</domain>

<decisions>
## Implementation Decisions

### Format File (Dukungan Format File Excel)
- **D-01:** Hanya mendukung format `.xlsx` dan `.csv` untuk v1. Dukungan format Excel lama (`.xls`) ditunda ke v2 untuk menjaga dependensi backend (seperti `xlrd`) tetap ramping dan aman.

### Lokasi Regex (Lokasi Penyimpanan Pola Regex)
- **D-02:** Aturan pola regex untuk sistem deteksi otomatis kolom sensitif akan disimpan dalam file konfigurasi eksternal (JSON/YAML) (misalnya `config/regex_rules.json`). Hal ini mempermudah kustomisasi aturan di masa mendatang tanpa memodifikasi kode Python backend.

### Styling CSS (Framework Styling Frontend)
- **D-03:** Menggunakan TailwindCSS v3 di frontend React. Pilihan ini diambil untuk memungkinkan penggunaan pustaka komponen premium seperti `shadcn/ui` (Radix UI) dan mempercepat penyusunan tata letak UI yang modern dan responsif.

### File Besar (Optimasi Pembacaan File Besar untuk Preview)
- **D-04:** Endpoint `/preview` akan menerapkan chunk parsing / pembacaan baris terbatas (lazy loading) sehingga hanya beberapa baris awal yang diproses. Hal ini menghindari pemuatan seluruh berkas berukuran hingga 50MB ke RAM server untuk kebutuhan pratinjau.

### the agent's Discretion
- Tidak ada area khusus yang diserahkan sepenuhnya kepada AI ("You decide"); semua keputusan di atas dipilih dan disepakati oleh pengguna.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Scope & Guidelines
- [prd.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/prd.md) — Product Requirement Document (PRD) defining core goals and user flows.
- [erd.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/erd.md) — Entity Relationship Diagram for DB structure.
- [.planning/REQUIREMENTS.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/REQUIREMENTS.md) — Traceability matrix and detailed v1/v2 constraints.
- [.planning/ROADMAP.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/ROADMAP.md) — Phased milestone plan and success criteria.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Proyek ini baru saja diinisialisasi. Belum ada komponen, hook, atau utilitas khusus yang dapat digunakan kembali selain konfigurasi lingkungan pengembangan dasar.

### Established Patterns
- **In-Memory Buffer**: Sesuai keputusan proyek (`PROJECT.md`), file harus diproses sepenuhnya di memory buffer (RAM) tanpa penulisan permanen di server.
- **Client-Server Separation**: Frontend React.js berkomunikasi via API REST stateless dengan FastAPI backend.

### Integration Points
- Backend entry point: `backend/app/main.py`
- Frontend entry point: `frontend/src/main.tsx`

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

- Dukungan format Excel lama (`.xls`) ditangguhkan ke v2 (atau fase berikutnya).

</deferred>

---

*Phase: 1-Foundation & Preview Engine*
*Context gathered: 2026-07-19*
