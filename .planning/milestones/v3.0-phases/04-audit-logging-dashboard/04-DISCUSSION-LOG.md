# Phase 4: Audit Logging & Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 4-Audit Logging & Dashboard
**Areas discussed:** Skema Basis Data, Pencatatan Status & Kegagalan Pekerjaan, Navigasi & Tata Letak UI Dashboard, Tampilan Statistik Ringkasan

---

## Skema Basis Data (Database Schema)

| Option | Description | Selected |
|--------|-------------|----------|
| Relasional Sederhana | Dua tabel: `masking_jobs` untuk metadata umum, dan `job_details` untuk mencatat kolom & aturan penyamarannya (rule_name disimpan sebagai string langsung). | ✓ |
| Relasional Kompleks Penuh (Sesuai ERD) | Tiga tabel: `masking_jobs`, `job_details`, dan tabel master `masking_rules` (memerlukan seeding data master saat startup). | |
| Single Table JSON | Satu tabel `masking_jobs` dengan seluruh detail kolom dan aturan disimpan langsung sebagai teks JSON di satu kolom. | |

**User's choice:** Relasional Sederhana.
**Notes:** Keputusan ini diambil karena menyederhanakan kueri dan skema basis data SQLite, meminimalkan kompleksitas seeding data master saat aplikasi dimulai, serta tetap menjaga struktur relasional yang rapi untuk relasi *one-to-many* log pengerjaan.

---

## Kebijakan Cascade Delete

| Option | Description | Selected |
|--------|-------------|----------|
| Cascade Delete | Jika pengguna dihapus, semua riwayat log masking mereka otomatis terhapus demi kepatuhan privasi (GDPR/UU PDP). | ✓ |
| Anonymize on Delete (Set NULL) | Tetap pertahankan log audit untuk keamanan organisasi, namun hapus asosiasi pengguna (set `user_id` menjadi NULL). | |
| No Account Deletion | Sederhanakan untuk versi v1 dengan tidak menyediakan fitur penghapusan akun pengguna terlebih dahulu. | |

**User's choice:** Cascade Delete.
**Notes:** Menyelaraskan dengan peraturan privasi ketat untuk tidak menyisakan rekam jejak metadata berkas dari pengguna yang telah meminta penghapusan akun.

---

## Pencatatan Status & Kegagalan Pekerjaan (Job Logging & Status)

| Option | Description | Selected |
|--------|-------------|----------|
| Post-execution only | Log baru ditulis ke basis data setelah proses masking selesai sepenuhnya. Mencatat apakah status akhir 'SUCCESS' atau 'FAILED'. Lebih sederhana dan meminimalkan beban tulis ke database. | ✓ |
| Real-time Lifecycle | Entri dibuat di awal request dengan status 'PROCESSING', kemudian di-update menjadi 'SUCCESS' atau 'FAILED' setelah selesai. | |
| Success Logs Only | Hanya mencatat log jika proses masking berhasil diselesaikan secara penuh. | |

**User's choice:** Post-execution only.
**Notes:** Dipilih demi efisiensi penulisan basis data SQLite lokal, karena tidak memerlukan pembaruan status perantara.

---

## Detail Pencatatan Kegagalan (FAILED)

| Option | Description | Selected |
|--------|-------------|----------|
| Error Message Singkat | Menyimpan string deskripsi kesalahan singkat (misalnya 'Format berkas rusak' atau 'Kolom tidak cocok') pada kolom `error_message` untuk membantu proses debug pengguna. | ✓ |
| Metadata Only | Hanya mencatat status 'FAILED' tanpa penjelasan detail kesalahan demi privasi maksimum. | |
| You decide | Berikan keleluasaan kepada agen AI untuk menentukan format pencatatan kesalahan secara otomatis. | |

**User's choice:** Error Message Singkat.
**Notes:** Menyeimbangkan kebutuhan kemudahan analisis/debugging kesalahan oleh pengguna dengan tetap menjaga kepatuhan privasi (metadata bebas dari data mentah/PII).

---

## Navigasi & Tata Letak UI Dashboard (UI Navigation & Layout)

| Option | Description | Selected |
|--------|-------------|----------|
| Top Navigation Tabs | Menambahkan tab navigasi ('Masking Engine' & 'Riwayat Audit') di bagian header untuk perpindahan halaman yang bersih dan terstruktur. | ✓ |
| Single Page Toggle Button | Menggunakan satu tombol toggle (misalnya 'Lihat Riwayat' / 'Kembali') untuk mengganti konten halaman secara instan. | |
| Direct Embed (Inline) | Menampilkan tabel riwayat audit langsung di bagian bawah halaman utama (di bawah area drag-and-drop) tanpa navigasi terpisah. | |

**User's choice:** Top Navigation Tabs.
**Notes:** Pola standar yang memisahkan area kerja utama dengan dasbor riwayat audit demi kenyamanan navigasi pengguna.

---

## Detail Kolom & Aturan Masking per Pekerjaan

| Option | Description | Selected |
|--------|-------------|----------|
| Read-only Table with Detail Modal | Tabel utama menampilkan ringkasan riwayat. Terdapat tombol 'Detail' pada setiap baris untuk membuka popup modal berisi rincian kolom & aturan masking-nya. | ✓ |
| Accordion Row Expand | Baris tabel riwayat dapat diklik untuk diekspansi ke bawah (accordion style) guna memunculkan daftar kolom & aturan masking. | |
| Plain Table Only | Hanya tampilkan data log dasar di tabel utama tanpa fitur untuk melihat detail aturan per kolom. | |

**User's choice:** Read-only Table with Detail Modal.
**Notes:** Memungkinkan visualisasi detail yang nyaman tanpa memadati baris tabel riwayat utama.

---

## Tampilan Statistik Ringkasan (Aggregate Metrics)

| Option | Description | Selected |
|--------|-------------|----------|
| Tiga Kartu Metrik Ringkasan | Menampilkan: (1) Total Berkas Diproses, (2) Total Baris Disanitasi, dan (3) Rasio Keberhasilan (Sukses vs Gagal). | ✓ |
| Satu Metrik Sederhana | Hanya menampilkan satu angka ringkasan utama, yaitu 'Total Berkas Berhasil Diproses'. | |
| Tanpa Statistik Agregat | Langsung menampilkan tabel daftar riwayat pekerjaan saja tanpa kartu metrik di atasnya. | |

**User's choice:** Tiga Kartu Metrik Ringkasan.
**Notes:** Membantu pengguna melihat statistik dan performa penyamaran mereka secara ringkas dan komunikatif.

---

## Kalkulasi Metrik Ringkasan

| Option | Description | Selected |
|--------|-------------|----------|
| Backend Aggregation Endpoint | Membuat endpoint khusus di backend (misalnya `/api/jobs/stats`) untuk menghitung statistik agregat secara efisien langsung menggunakan query SQL (COUNT, SUM) pada database. | ✓ |
| Frontend Calculation | Menggunakan endpoint list data log yang sudah ada, lalu frontend menghitung statistik agregat di sisi browser menggunakan Javascript. | |
| You decide | Berikan keleluasaan kepada agen AI untuk memilih metode integrasi kalkulasi yang paling optimal. | |

**User's choice:** Backend Aggregation Endpoint.
**Notes:** Menghindari beban rendering di browser saat data riwayat pekerjaan membesar, dengan menyerahkan proses agregasi langsung ke SQLite backend.

---

## the agent's Discretion

- Rincian gaya desain kartu metrik (penggunaan warna HSL/indigo, styling hover).
- Transisi pop-up modal detail di frontend.
- Implementasi query session SQLite untuk join kueri data jobs & details di backend.

## Deferred Ideas

- None.
