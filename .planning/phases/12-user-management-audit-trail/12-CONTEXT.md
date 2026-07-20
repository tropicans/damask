# Phase 12: User Management & Audit Trail - Context

**Gathered:** 2026-07-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 12 implements the user administration panel and login audit logging:
1. **User Management UI** — Halaman admin untuk mengelola user, termasuk menampilkan daftar semua user (username, email, role, status aktif/non-aktif), mengubah role (promote/demote), dan menonaktifkan/mengaktifkan kembali akun user.
2. **Login Audit Trail** — Mencatat setiap event login berhasil dan gagal ke database (timestamp, IP address, user agent, status).
3. **Audit Dashboard Tabs** — Menampilkan tab "Login History" dan "Failed Attempts" di Audit Dashboard untuk admin.

</domain>

<decisions>
## Implementation Decisions

### User Status & Active Field
- **D-01:** Tambahkan kolom `is_active: bool = Field(default=True, nullable=False)` pada model/tabel `User` di `backend/app/models/user.py`.
- **D-02:** Penonaktifkan akun langsung memblokir akses pengguna. Pada fungsi dependency `get_current_user` di `backend/app/services/auth.py`, jika `not user.is_active`, langsung naikkan `AuthException("Akun Anda dinonaktifkan. Silakan hubungi admin.")`.
- **D-03:** Di endpoint `/login`, jika email yang dimasukkan cocok dengan user yang statusnya tidak aktif (`is_active == False`), kembalikan HTTP 400 Bad Request dengan detail `"Akun Anda dinonaktifkan. Silakan hubungi admin."`.

### Login Audit Trail Storage
- **D-04:** Buat model database baru `LoginAudit` (SQLModel table `login_audits`) untuk melacak riwayat login dengan skema:
  - `id`: str (UUID PK)
  - `email`: str (diindeks, untuk mencatat email yang diinput saat login sukses maupun gagal)
  - `user_id`: Optional[str] (Foreign Key ke `users.id` dengan onDelete="SET NULL", nullable=True)
  - `ip_address`: str (IP client yang melakukan percobaan login)
  - `user_agent`: Optional[str] (Header User-Agent client)
  - `status`: str (Bernilai `"SUCCESS"` atau `"FAILED"`)
  - `created_at`: datetime (Default UTC timestamp)
- **D-05:** Setiap kali request login dilakukan di `/api/auth/login`, buat entri baru di tabel `login_audits` setelah memproses password (baik berhasil maupun gagal).
- **D-06:** Modifikasi `/register` untuk mencatat login pertama jika langsung menset session cookie.

### User Management UI Access & Placement
- **D-07:** Letakkan UI manajemen user pada tab utama terpisah bernama **Manajemen User** di header navigasi `App.tsx`. Tab ini hanya dirender jika `user.role === 'admin'`.
- **D-08:** Halaman Manajemen User akan menampilkan tabel daftar semua user. Kolom yang ditampilkan: Username, Email, Role, Status, dan Aksi.
- **D-09:** Aksi yang dapat dilakukan oleh admin:
  - Tombol toggle status: "Nonaktifkan" jika user aktif, dan "Aktifkan" jika user nonaktif.
  - Dropdown/tombol perubahan peran: Promosi/Demote peran user antara `"admin"`, `"auditor"`, dan `"user"`.

### Role Management & Self-Demotion Safety
- **D-10:** Admin tidak diperbolehkan untuk mengubah perannya sendiri (self-demotion) atau menonaktifkan akunnya sendiri di UI maupun backend API jika dia adalah satu-satunya admin aktif yang tersisa di sistem, guna mencegah lockout total admin.
- **D-11:** Berikan dialog konfirmasi sebelum melakukan aksi perubahan peran atau penonaktifan akun user di frontend.

### the agent's Discretion
- Palet warna dan styling UI Manajemen User mengikuti tema gelap Tailwind (indigo/slate/emerald/red) yang sudah ada di aplikasi.
- Icon untuk aksi menggunakan Lucide-react (misalnya `UserX`, `UserCheck`, `Shield`, `Trash2`).
- Batas pagination default untuk daftar user di frontend adalah 10 data per halaman dengan navigasi halaman (Next/Prev).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Specifications
- `.planning/ROADMAP.md` — Phase 12 goal, success criteria, and dependencies.
- `.planning/REQUIREMENTS.md` — Requirements PROD-01, PROD-02, PROD-03, PROD-12, PROD-13.

### Backend User and Auth System
- `backend/app/models/user.py` — Skema model `User` yang perlu diperluas dengan kolom `is_active` dan tempat menambahkan kelas `LoginAudit`.
- `backend/app/api/endpoints/auth.py` — Endpoint login dan registrasi tempat pencatatan log login audits dan pengecekan status `is_active`.
- `backend/app/services/auth.py` — Implementasi token decoding dan dependency `get_current_user`.
- `backend/app/db.py` — Engine database SQLModel, inisialisasi tabel baru `LoginAudit` pada fungsi `init_db`.

### Frontend Components & Dashboard
- `frontend/src/App.tsx` — Layout utama dan navigasi tab Manajemen User untuk admin.
- `frontend/src/components/AuditDashboard.tsx` — Dashboard audit compliant tempat menambahkan sub-tab baru "Riwayat Login" dan "Percobaan Gagal".
- `frontend/src/api/auth.ts` — API client untuk otentikasi.
- `frontend/src/api/jobs.ts` — API client untuk audit jobs. Tambahkan endpoint baru untuk user management dan login history fetch.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AuditDashboard.tsx`: Sudah memiliki pola tab navigasi, tabel audit, pemformatan tanggal/waktu, dan pagination yang dapat direproduksi untuk sub-tab "Riwayat Login" dan halaman "Manajemen User".
- API Client `client.ts`: Digunakan untuk mengirim request API dengan header otentikasi.

### Established Patterns
- **Role authorization check**: Endpoint admin dilindungi dengan memeriksa peran user saat ini di backend (`current_user.role == "admin"`), jika tidak raise HTTPException 403.
- **Confirmation dialogs**: Tampilkan modal konfirmasi sederhana sebelum melakukan deaktifasi user atau promote/demote peran.

### Integration Points
- `backend/app/models/user.py`: Tambah kolom `is_active` ke `User`, definisikan class `LoginAudit` dan model response/request baru.
- `backend/app/api/endpoints/admin.py` [NEW]: Buat router admin baru `/api/admin/users` untuk list users, update status, dan update role.
- `backend/app/api/endpoints/auth.py`: Catat audit trail logins pada endpoint `/login` dan periksa `is_active`.
- `frontend/src/components/UserManagement.tsx` [NEW]: Halaman admin untuk mengelola user list.
- `frontend/src/api/admin.ts` [NEW]: API client untuk operasi admin (user management, login audits fetch).

</code_context>

<specifics>
## Specific Ideas

- Detail pencatatan login audit: status "SUCCESS" jika password valid, status "FAILED" jika user tidak ditemukan atau password salah.
- Jika login diblokir karena lockout brute-force (IP lockout), catat status "FAILED" dengan alasan/keterangan tambahan jika memungkinkan atau cukup catat status "LOCKED".
- Link halaman manajemen user: Rander menu "Manajemen User" di sidebar/header hanya jika `user.role === 'admin'`.

</specifics>

<deferred>
## Deferred Ideas

- Integrasi email pemberitahuan keamanan ketika ada login gagal berkali-kali — ditunda ke v2.
- Mengirim invite link via email — tetap di luar scope, pengiriman dilakukan via copy-paste.

</deferred>

---

*Phase: 12-User Management & Audit Trail*
*Context gathered: 2026-07-20*
