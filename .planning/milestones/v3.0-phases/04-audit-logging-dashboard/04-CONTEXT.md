# Phase 4: Audit Logging & Dashboard - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementasi pencatatan log audit pekerjaan penyamaran (masking) ke basis data secara lokal. Ini mencakup pembuatan tabel riwayat pekerjaan (`masking_jobs`) dan detail kolom yang disamarkan (`job_details`) menggunakan SQLModel, pembuatan endpoint API backend untuk melacak riwayat pekerjaan dan statistik agregat, serta pembangunan dashboard riwayat pengerjaan lengkap dengan metrik ringkasan dan detail modal di frontend React.

</domain>

<decisions>
## Implementation Decisions

### Skema Basis Data (Database Schema)
- **D-01:** **Relasional Sederhana**: Struktur basis data dirancang menggunakan dua tabel relasional: `masking_jobs` untuk menyimpan metadata umum eksekusi (ID pekerjaan, ID pengguna, nama berkas, ukuran berkas, jumlah baris, status akhir, waktu eksekusi) dan `job_details` untuk mencatat daftar kolom yang disamarkan beserta aturan penyamarannya (rule_name disimpan sebagai string langsung, mempermudah perluasan rule baru tanpa master table).
- **D-02:** **Cascade Delete**: Kebijakan cascade delete diterapkan pada relasi kunci asing antara tabel `users` dan `masking_jobs`. Jika data pengguna dihapus, seluruh riwayat log masking terkait otomatis dibersihkan demi kepatuhan privasi data.

### Pencatatan Status & Kegagalan Pekerjaan (Job Logging & Status)
- **D-03:** **Post-Execution Only**: Penulisan log audit baru dilakukan ke basis data SQLite setelah seluruh proses masking selesai sepenuhnya. Langkah ini mencatat apakah status akhir pekerjaan adalah 'SUCCESS' or 'FAILED', meminimalkan beban tulis (write-overhead) database.
- **D-04:** **Error Message Singkat**: Jika status pekerjaan bernilai 'FAILED', sistem mencatat deskripsi pesan kesalahan singkat (misalnya 'Format berkas rusak' atau 'Kolom tidak cocok') di kolom `error_message` untuk mempermudah proses debugging oleh pengguna tanpa menyimpan data sensitif berkas.

### Navigasi & Tata Letak UI Dashboard (UI Navigation & Layout)
- **D-05:** **Top Navigation Tabs**: Navigasi di frontend diimplementasikan dengan menambahkan tab menu baru di bagian header (misalnya 'Masking Engine' dan 'Riwayat Audit') menggunakan state-based rendering di `App.tsx` untuk memisahkan kedua fokus utama secara bersih.
- **D-06:** **Read-only Table dengan Detail Modal**: Tampilan log pekerjaan utama disajikan dalam bentuk tabel ringkas di halaman Riwayat Audit. Terdapat tombol 'Detail' pada setiap baris log sukses untuk membuka popup modal berisi rincian daftar kolom beserta aturan penyamaran yang diterapkan.

### Tampilan Statistik Ringkasan (Aggregate Metrics)
- **D-07:** **Tiga Kartu Metrik Ringkasan**: Dashboard akan menampilkan tiga kartu statistik di bagian atas halaman Riwayat Audit: (1) Total Berkas Diproses, (2) Total Baris Disanitasi, dan (3) Rasio Keberhasilan (Sukses vs Gagal) untuk visualisasi cepat.
- **D-08:** **Backend Aggregation Endpoint**: Perhitungan metrik ringkasan dilakukan secara efisien di sisi backend menggunakan query agregasi SQL (seperti `COUNT` dan `SUM`) melalui endpoint API khusus `/api/jobs/stats`.

### the agent's Discretion
- Desain visual visualisasi kartu metrik, detail transisi pop-up modal detail, struktur internal penanganan kueri session SQLite, dan optimasi query join diserahkan kepada agen AI.

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
- [.planning/phases/03-user-authentication/03-CONTEXT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/.planning/phases/03-user-authentication/03-CONTEXT.md) — Phase 3 decisions and context.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- [db.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/db.py): Engine inisialisasi SQLModel dan helper `get_session` untuk memfasilitasi transaksi basis data.
- [auth.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/services/auth.py): Kumpulan dependensi otentikasi seperti `get_current_user` guna memvalidasi sesi JWT sebelum melakukan audit logging.
- [App.tsx](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/frontend/src/App.tsx): File entry point utama aplikasi React dengan state-based rendering. Dapat diperluas dengan menambahkan tab 'Riwayat Audit'.

### Established Patterns
- Menggunakan skema validasi Pydantic / model data masukan/keluaran di backend untuk endpoint API.
- Struktur endpoint FastAPI tersegregasi di bawah `backend/app/api/endpoints/`.
- Dependensi `Depends(get_current_user)` dipasang di API router backend untuk mengamankan data pengguna secara presisi.

### Integration Points
- **Backend Audit Models:** Buat berkas model SQLModel untuk tabel riwayat di file baru `backend/app/models/job.py` yang mendefinisikan tabel `masking_jobs` dan `job_details`. Pastikan di-import di `backend/app/db.py` agar dideteksi oleh SQLModel metadata saat inisialisasi basis data.
- **Backend Log Trigger:** Modifikasi `backend/app/api/endpoints/mask.py` agar melakukan kueri tulis penulisan log audit ke basis data setelah proses masking file berhasil diselesaikan maupun saat gagal.
- **Backend Audit Endpoints:** Buat berkas router baru `backend/app/api/endpoints/jobs.py` (atau `audit.py`) untuk menyediakan endpoint mengambil daftar riwayat pekerjaan (`/api/jobs`) dan endpoint kalkulasi statistik agregat (`/api/jobs/stats`). Hubungkan router baru ini ke router utama di `backend/app/api/api.py`.
- **Frontend API Client:** Buat modul API client baru `frontend/src/api/jobs.ts` untuk memfasilitasi call Axios ke endpoint `/api/jobs` dan `/api/jobs/stats`.
- **Frontend Components:** Buat komponen `frontend/src/components/AuditDashboard.tsx` (atau sejenisnya) untuk merender kartu metrik ringkasan, tabel riwayat pekerjaan, dan modal detail daftar kolom beserta aturan penyamarannya.

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

*Phase: 04-Audit Logging & Dashboard*
*Context gathered: 2026-07-19*
