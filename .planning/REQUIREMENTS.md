# Requirements: SecureData Web — Production Readiness

**Defined:** 2026-07-19  
**Core Value:** Harden SecureData Web untuk digunakan bersama secara aman dalam lingkungan multi-user dengan user management, security policy, dan deployment infrastructure yang production-grade.

---

## v1 Requirements

### User Management (PROD)

- [x] **PROD-01**: Admin dapat melihat daftar semua registered users (nama, email, role, status aktif/non-aktif) melalui halaman admin UI.
- [x] **PROD-02**: Admin dapat mengubah role user (promote ke admin/auditor atau demote ke user biasa) melalui tombol aksi di halaman admin UI.
- [x] **PROD-03**: Admin dapat menonaktifkan (deactivate) akun user sehingga user tersebut tidak dapat login lagi hingga diaktifkan kembali.
- [x] **PROD-04**: User registration memerlukan invite link/code yang valid yang dibuat oleh admin; registrasi langsung tanpa invite ditolak.
- [x] **PROD-05**: Admin dapat membuat invite link sekali pakai dengan batas waktu kedaluwarsa yang dapat dikonfigurasi (default: 48 jam).

### Password & Auth Policy (PROD)

- [x] **PROD-06**: Password baru harus memenuhi kebijakan: minimal 8 karakter, mengandung minimal 1 huruf kapital, 1 huruf kecil, dan 1 angka.
- [x] **PROD-07**: Halaman registrasi menampilkan indikator kekuatan password secara real-time (Lemah / Sedang / Kuat) berdasarkan kebijakan di atas.

### Database Migration (PROD)

- [x] **PROD-08**: Backend mendukung PostgreSQL sebagai database primary dengan konfigurasi `DATABASE_URL` di `.env`.
- [ ] **PROD-09**: Docker Compose production profile (`docker-compose.prod.yml`) menyertakan service PostgreSQL dengan volume persisten dan health check.

### Deployment & HTTPS (PROD)

- [ ] **PROD-10**: Repository menyertakan panduan deployment produksi (`docs/DEPLOYMENT-PROD.md`) mencakup: setup Nginx reverse proxy, konfigurasi SSL/TLS dengan Let's Encrypt (Certbot), dan environment variable checklist.
- [ ] **PROD-11**: Disertakan template konfigurasi Nginx (`nginx/nginx.conf`) yang siap pakai untuk meneruskan traffic HTTPS ke backend dan frontend containers.

### Audit Trail Enhancement (PROD)

- [x] **PROD-12**: Setiap login berhasil dan gagal dicatat ke database (user_id atau email, timestamp, IP address, user agent, dan status success/failed).
- [x] **PROD-13**: Admin dapat melihat riwayat login (login history) dan upaya login gagal (failed attempts) di halaman Audit Dashboard.
- [x] **PROD-14**: Akun user otomatis dikunci sementara (lock 15 menit) setelah 5 kali gagal login berturut-turut dari IP yang sama.

---

## v2 Requirements (Deferred)

- **PROD-V2-01**: Single Sign-On (SSO) integration with Google Workspace / Microsoft Entra ID.
- **PROD-V2-02**: Two-factor authentication (TOTP/FIDO2).
- **PROD-V2-03**: Password expiry and forced rotation policy.
- **PROD-V2-04**: Organization/group concept for tenant isolation.

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Email delivery service (SMTP) | Invite links can be shared via copy-paste for internal tools; email infra adds external dependency |
| OAuth / Social Login | SSO deferred to v2; would require external provider setup |
| Cloud deployment scripts (AWS/GCP/Azure) | Deployment guide covers VPS/bare-metal; cloud-specific IaC out of scope for v5 |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROD-01 | Phase 12 | Complete |
| PROD-02 | Phase 12 | Complete |
| PROD-03 | Phase 12 | Complete |
| PROD-04 | Phase 11 | Complete |
| PROD-05 | Phase 11 | Complete |
| PROD-06 | Phase 11 | Complete |
| PROD-07 | Phase 11 | Complete |
| PROD-08 | Phase 13 | Complete |
| PROD-09 | Phase 13 | Pending |
| PROD-10 | Phase 14 | Pending |
| PROD-11 | Phase 14 | Pending |
| PROD-12 | Phase 12 | Complete |
| PROD-13 | Phase 12 | Complete |
| PROD-14 | Phase 11 | Complete |

**Coverage:**

- v1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-19*
