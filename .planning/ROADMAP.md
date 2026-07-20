# Roadmap: SecureData Web

## Milestones

- ✅ **v1.0 MVP** - Phases 1-4 (shipped 2026-07-19)
- ✅ **v2.0 add documentation** - Phase 5 (shipped 2026-07-19)
- ✅ **v3.0 secured the app** - Phases 6-8 (shipped 2026-07-19)
- ✅ **v4.0 data reversion** - Phases 9-10 (shipped 2026-07-19)
- 🚧 **v5.0 production readiness** - Phases 11-14 (planning)

---

## Phases

<details>
<summary>✅ v1.0–v4.0 (Phases 1-10) - SHIPPED</summary>

Previous milestones archived in `.planning/milestones/`.

</details>

---

### 🚧 v5.0 Production Readiness (Planned)

#### Phase 11: Auth Policy & Invite Registration

- **Goal**: Enforce password policy di backend dan frontend, implementasikan invite-based registration system, dan tambahkan brute-force protection (account lockout).
- **Depends on**: Phase 10
- **Requirements**: PROD-04, PROD-05, PROD-06, PROD-07, PROD-14
- **Success Criteria**:
  1. Registrasi tanpa invite code yang valid ditolak dengan pesan error yang jelas.
  2. Admin dapat membuat invite link sekali pakai dengan waktu kedaluwarsa 48 jam (default).
  3. Backend menolak password yang tidak memenuhi policy (min 8 char, uppercase+digit) dengan HTTP 422.
  4. UI registrasi menampilkan indikator kekuatan password real-time.
  5. Akun terkunci 15 menit setelah 5 kali gagal login berturut-turut.
- **Plans**: 3/3 plans executed
- [x] 11-01-PLAN.md
- [x] 11-02-PLAN.md
- [x] 11-03-PLAN.md

#### Phase 12: User Management & Audit Trail

- **Goal**: Buat halaman admin UI untuk manajemen user (list, promote/demote, deactivate) dan implementasikan login history + failed login tracking di Audit Dashboard.
- **Depends on**: Phase 11
- **Requirements**: PROD-01, PROD-02, PROD-03, PROD-12, PROD-13
- **Success Criteria**:
  1. Halaman admin menampilkan daftar semua user dengan role dan status aktif/non-aktif.
  2. Admin dapat mengubah role user atau menonaktifkan akun melalui tombol aksi di UI.
  3. Setiap event login berhasil dan gagal dicatat ke DB (timestamp, IP, user agent, status).
  4. Audit Dashboard menampilkan tab "Login History" dan "Failed Attempts" untuk admin.
- **Plans**: 3/3 plans executed
- [x] 12-01-PLAN.md
- [x] 12-02-PLAN.md
- [x] 12-03-PLAN.md

#### Phase 13: PostgreSQL Migration

- **Goal**: Migrasi database dari SQLite ke PostgreSQL, update `docker-compose.prod.yml` dengan PostgreSQL service, dan pastikan semua existing tests passing dengan DB baru.
- **Depends on**: Phase 12
- **Requirements**: PROD-08, PROD-09
- **Success Criteria**:
  1. `DATABASE_URL` di `.env` dapat dikonfigurasi ke PostgreSQL connection string.
  2. `docker-compose.prod.yml` menyertakan PostgreSQL service dengan volume persisten dan health check.
  3. Semua 35+ backend tests passing dengan PostgreSQL sebagai database.
  4. SQLite tetap digunakan untuk development (`.env.example` mendokumentasikan keduanya).
- **Plans**: 2/2 plans executed
- [x] 13-01-PLAN.md
- [x] 13-02-PLAN.md

#### Phase 14: HTTPS & Production Deployment Guide

- **Goal**: Buat panduan deployment produksi lengkap dengan konfigurasi Nginx reverse proxy dan SSL/TLS, serta template konfigurasi siap pakai.
- **Depends on**: Phase 13
- **Requirements**: PROD-10, PROD-11
- **Success Criteria**:
  1. `docs/DEPLOYMENT-PROD.md` mencakup langkah-langkah setup VPS, Docker, Nginx, dan Certbot.
  2. `nginx/nginx.conf` template tersedia di repository dan siap dikustomisasi.
  3. Environment variable checklist (production secrets, DB URL, CORS origins) terdokumentasi.
  4. Dokumentasi mencakup cara memperpanjang SSL certificate secara otomatis.
- **Plans**: 2 plans (Planned)

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------||
| 1. Foundation & Preview Engine | v1.0 | 3/3 | Complete | 2026-07-19 |
| 2. Masking Engine & Download | v1.0 | 3/3 | Complete | 2026-07-19 |
| 3. User Authentication | v1.0 | 2/2 | Complete | 2026-07-19 |
| 4. Audit Logging & Dashboard | v1.0 | 2/2 | Complete | 2026-07-19 |
| 5. Documentation Suite | v2.0 | 3/3 | Complete | 2026-07-19 |
| 6. Cookie-based Auth & CSRF | v3.0 | 2/2 | Complete | 2026-07-19 |
| 7. Secure Headers & Limits | v3.0 | 2/2 | Complete | 2026-07-19 |
| 8. Input & Role Security | v3.0 | 2/2 | Complete | 2026-07-19 |
| 9. Reversion Key & Backend | v4.0 | 3/3 | Complete | 2026-07-19 |
| 10. Revert UI & Auditing | v4.0 | 3/3 | Complete | 2026-07-19 |
| 11. Auth Policy & Invite Reg | v5.0 | 3/3 | Complete | 2026-07-20 |
| 12. User Management & Audit Trail | v5.0 | 3/3 | Complete | 2026-07-20 |
| 13. PostgreSQL Migration | v5.0 | 2/2 | Complete | 2026-07-20 |
| 14. HTTPS & Deployment Guide | v5.0 | 0/2 | Planned | — |

---
*Roadmap updated: 2026-07-20*

