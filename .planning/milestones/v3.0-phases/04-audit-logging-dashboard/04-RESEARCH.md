# Phase 4: Audit Logging & Dashboard - Technical Research

**Date:** 2026-07-19
**Phase:** 4

## 1. Database Schema Design (SQLModel)

Kami akan membuat dua tabel baru menggunakan SQLModel: `masking_jobs` dan `job_details`.

### Tabel `masking_jobs` (MaskingJob)
Mencatat riwayat eksekusi pekerjaan penyamaran.
- `id`: `str` (UUID, Primary Key)
- `user_id`: `str` (Foreign Key ke `users.id` dengan `ondelete="CASCADE"`, Index)
- `file_name`: `str` (Nama berkas asli, misal `data.csv`)
- `file_size_bytes`: `int` (Ukuran berkas dalam byte)
- `row_count`: `Optional[int]` (Jumlah total baris data yang diproses, null jika gagal di awal)
- `status`: `str` (`"SUCCESS"` atau `"FAILED"`)
- `error_message`: `Optional[str]` (Deskripsi kesalahan singkat jika status gagal)
- `created_at`: `datetime` (Waktu pencatatan, default `datetime.utcnow`)

### Tabel `job_details` (JobDetail)
Mencatat detail kolom dan aturan penyamaran yang digunakan untuk setiap pekerjaan.
- `id`: `str` (UUID, Primary Key)
- `job_id`: `str` (Foreign Key ke `masking_jobs.id` dengan `ondelete="CASCADE"`, Index)
- `column_name`: `str` (Nama kolom yang disamarkan)
- `rule_name`: `str` (Nama aturan penyamaran langsung sebagai string, e.g. `"Fake Name"`, `"Fake Email"`, `"Perturb Numeric"`)

### Cascade Delete & Relationship
Relasi didefinisikan secara deklaratif di SQLModel:
- Hapus pengguna (`User`) -> Hapus semua `MaskingJob` terkait (`ondelete="CASCADE"`).
- Hapus pekerjaan (`MaskingJob`) -> Hapus semua `JobDetail` terkait (`ondelete="CASCADE"`).

---

## 2. API Endpoints

### 2.1. Audit Logging Trigger (`/api/mask`)
Ketika penyamaran file dieksekusi di `/api/mask`:
1. Jika proses berhasil, buat entri `MaskingJob` baru dengan status `"SUCCESS"`. Untuk setiap kolom yang disamarkan, buat entri `JobDetail` dengan `rule_name` yang sesuai. Simpan transaksi ke basis data.
2. Jika proses gagal (misalnya gagal membaca berkas, kegagalan saat Pandas melakukan transformasi data), tangkap Exception, buat entri `MaskingJob` baru dengan status `"FAILED"`, isi `error_message` dengan pesan singkat (e.g. `str(e)` terbatas/dibersihkan dari info sensitif), lalu kembalikan HTTP Exception.

### 2.2. Query Endpoints
Kami akan menambahkan router baru di `backend/app/api/endpoints/jobs.py`:
- `GET /api/jobs`: Mengambil daftar pekerjaan milik pengguna yang sedang login (`current_user`). Diurutkan berdasarkan `created_at` secara descending. Endpoint ini harus menerima parameter pagination (misal `skip` dan `limit`).
- `GET /api/jobs/stats`: Mengembalikan statistik agregat pekerjaan untuk dashboard pengguna yang login:
  - `total_files`: Jumlah file yang diproses (sukses).
  - `total_rows`: Jumlah baris yang disanitasi (sukses).
  - `success_rate`: Persentase pekerjaan yang sukses terhadap total pekerjaan.
- `GET /api/jobs/{job_id}/details`: Mengambil detail kolom-kolom yang disamarkan untuk pekerjaan tertentu (jika milik `current_user`).

---

## 3. UI Navigation & Dashboard Components

### 3.1. Header Navigation
Di `frontend/src/App.tsx`, kami akan menambahkan state `activeTab`:
```tsx
const [activeTab, setActiveTab] = useState<'masking' | 'audit'>('masking');
```
Di header, kami akan merender dua tombol tab:
- **Masking Engine**: Menampilkan form upload & preview tabel.
- **Riwayat Audit**: Menampilkan dashboard audit log.

### 3.2. Dashboard Lay Out
Dashboard Riwayat Audit berisi:
1. **Summary Cards (Statistik)**:
   - Total Berkas Diproses (sukses)
   - Total Baris Disanitasi (sukses)
   - Rasio Keberhasilan (sukses/total, persen)
2. **Riwayat Tabel**:
   - Kolom: Waktu (Datetime terformat), Nama Berkas, Ukuran Berkas, Baris, Status (Badge Hijau/Merah), Aksi (Tombol Detail jika sukses, tombol Error jika gagal).
3. **Modal Detail**:
   - Jika tombol "Detail" diklik, buka Modal popup yang menampilkan tabel berkolom "Nama Kolom" dan "Aturan Penyamaran".
   - Jika status pekerjaan gagal, tombol "Detail" bisa menampilkan pesan kesalahan (error_message) yang terjadi.

---

## 4. Verification Plan

### 4.1. Unit & Integration Tests (Backend)
- Membuat test di `backend/app/tests/test_jobs.py` untuk menguji:
  1. Endpoint `/api/jobs` mengembalikan data riwayat yang benar untuk user yang login.
  2. Endpoint `/api/jobs/stats` mengembalikan agregasi yang akurat.
  3. Pemasukan log secara otomatis ketika penyamaran di `/api/mask` berhasil atau gagal.
  4. Cascade delete berjalan ketika user dihapus dari basis data.

### 4.2. Manual Verification
- Menjalankan docker-compose lokal (build dan up) jika berlaku, memverifikasi fungsionalitas UI dashboard secara langsung di browser dengan mengunggah beberapa berkas (sukses & sengaja digagalkan).
