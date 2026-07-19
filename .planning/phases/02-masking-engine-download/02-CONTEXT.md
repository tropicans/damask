# Phase 2: Masking Engine & Download - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementasi backend eksekusi masking data menggunakan Faker, penyesuaian aturan masking oleh pengguna di UI frontend, serta streaming download file hasil masking tanpa menyentuh penyimpanan fisik disk server.

</domain>

<decisions>
## Implementation Decisions

### Lokalisasi Faker (Faker Localization)
- **D-01:** Kebijakan locale menggunakan kombinasi `id_ID` (untuk Nama & Telepon Indonesia) dengan fallback `en_US` (untuk domain, email, atau data global/lainnya).
- **D-02:** Format nomor telepon Indonesia (Fake Phone) yang dihasilkan bersifat dinamis campuran antara format lokal (`08...`) dan internasional (`+62...`).

### Algoritma Perturbasi Numerik (Numeric Perturbation)
- **D-03:** Menggunakan *Smart Typing* di mana hasil perturbasi dibulatkan ke integer terdekat jika data aslinya berupa integer, sedangkan format desimal/float dipertahankan tingkat presisinya.
- **D-04:** Sel kosong (null/NaN) atau nilai non-numerik (seperti teks "N/A" atau string kosong) di kolom numerik akan dilewati dan dipertahankan seperti aslinya.

### Pola Pengacakan ID (ID Anonymization Strategy)
- **D-05:** Menggunakan *Format-preserving Scrambling* (mengacak digit angka dengan angka acak baru 0-9 dan huruf dengan huruf acak baru A-Z/a-z, serta mempertahankan karakter tanda hubung/titik dan panjang aslinya).
- **D-06:** Pengacakan bersifat *Deterministik per File*, yaitu nilai ID asli yang sama dalam satu file akan diacak menjadi nilai masking yang sama untuk menjaga integritas relasional data dalam file tersebut.

### Mekanisme Streaming Download (Streaming Download)
- **D-07:** Berkas hasil masking yang diunduh akan diberi nama dengan menambahkan suffix `_masked` sebelum ekstensi file (contoh: `data_karyawan_masked.xlsx`).
- **D-08:** Menggunakan strategi *Transactional Fail-fast*, di mana error pemrosesan di tengah jalan akan menghentikan seluruh proses masking, membebaskan buffer RAM (`io.BytesIO`), dan mengirimkan kode HTTP error tanpa mengunduh file setengah ter-masking demi keamanan data.

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
- [.planning/phases/01-foundation-preview-engine/01-CONTEXT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/phases/01-foundation-preview-engine/01-CONTEXT.md) — Phase 1 decisions and context.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Antarmuka preview data tabel ([PreviewTable.tsx](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/components/PreviewTable.tsx)), drag-and-drop zone ([Dropzone.tsx](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/components/Dropzone.tsx)), dan API client upload ([preview.ts](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/api/preview.ts)).
- Pemuatan/parsing file menggunakan Pandas dan openpyxl di backend ([parser.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/services/parser.py) dan [detector.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/services/detector.py)).

### Established Patterns
- **RAM-only processing**: File diproses dalam memori RAM (`io.BytesIO`) dan tidak disimpan di disk server backend untuk kepatuhan perlindungan data.
- **RESTful API stateless**: Frontend React berkomunikasi dengan FastAPI backend melalui REST API.

### Integration Points
- **Backend masking endpoint**: Tambahkan endpoint `/api/mask` atau sejenisnya di `backend/app/api/endpoints/` untuk menerima file upload dan konfigurasi rules dari frontend.
- **Backend masking service**: Tambahkan berkas `masker.py` di `backend/app/services/` untuk mengimplementasikan strategi transformasi Pandas + Faker.
- **Frontend dashboard / masking trigger**: Aktifkan tombol "Mulai Masking" di [App.tsx](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/App.tsx#L127) dan hubungkan ke endpoint backend baru tersebut.

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

*Phase: 2-masking-engine-download*
*Context gathered: 2026-07-19*
