# Tinjauan Arsitektur / Architectural Overview

Dokumen ini menjelaskan desain arsitektur, pola desain, aliran data, dan keputusan teknis yang diambil dalam implementasi **SecureData Web**.

This document describes the architectural design, design patterns, data flows, and technical decisions made in the implementation of **SecureData Web**.

---

## 1. Arsitektur Tingkat Tinggi / High-Level Architecture

SecureData Web dirancang dengan pola **Decoupled Architecture** (Arsitektur Terpisah) yang memisahkan area tanggung jawab antara antarmuka pengguna dan logika pemrosesan data:
SecureData Web is designed using a **Decoupled Architecture** pattern that cleanly separates the frontend user interface from the backend data processing engine:

1. **Frontend (React SPA)**: Dibangun menggunakan React 18, Vite, TypeScript, dan Tailwind CSS. Berfungsi sebagai antarmuka konfigurasi visual bagi pengguna untuk mengunggah berkas, menetapkan aturan, dan memantau riwayat audit.
   Built using React 18, Vite, TypeScript, and Tailwind CSS. Acts as the visual configuration interface for users to upload files, map rules, and monitor audit logs.
2. **Backend (FastAPI)**: Layanan API stateless berbasis Python yang mengeksekusi operasi parsing berkas, deteksi nama kolom berbasis regex, dan masking data menggunakan library Pandas dan Faker.
   A stateless Python-based API service that executes file parsing, regex-based column auto-detection, and data masking operations using Pandas and Faker.
3. **Database (SQLite / SQLModel)**: Menyimpan informasi kredensial pengguna dan audit log metadata eksekusi masking. SQLite digunakan untuk tahap pengembangan lokal.
   Stores user credentials and masking execution audit logs. SQLite is used for local development.

---

## 2. Aliran Data & Keamanan Pemrosesan Memori / Data Flow & In-Memory Security

Untuk memenuhi standar keamanan perlindungan data (GDPR / UU PDP), sistem menerapkan aturan ketat: **Tidak boleh ada berkas data sensitif asli atau berkas hasil masking yang disimpan secara permanen di server backend.**
To comply with security and data protection standards (GDPR / UU PDP), the system enforces a strict rule: **No sensitive raw uploaded files or processed masked files may be stored permanently on the backend server's disk.**

### Aliran Masking Data / Masking Data Flow

```
User (Browser)                  FastAPI Backend (RAM Buffer)                  SQLite (DB)
     |                                      |                                      |
     |--- 1. POST /api/preview/preview ---->| (Membaca file ke BytesIO buffer)     |
     |    (Upload file & dapat pratinjau)   | (Mengambil 3 baris pertama)          |
     |<-- 2. Mengembalikan pratinjau -------|                                      |
     |                                      |                                      |
     |--- 3. POST /api/mask/mask ---------->| (Membaca file ke BytesIO buffer)     |
     |    (Upload file & masking rules)     | (Mengubah DF dengan MaskingEngine)   |
     |                                      | (Simpan hasil ke BytesIO output)     |
     |                                      |--- 4. Tulis metadata audit log ----->|
     |                                      |       (Sukses/Gagal + total baris)   |
     |<-- 5. Stream unduhan berkas ---------|                                      |
     |    (attachment; filename_masked)     |                                      |
```

1. **BytesIO Buffers**: Berkas yang diunggah (`UploadFile`) dibaca langsung ke dalam buffer biner Python `io.BytesIO`.
   Uploaded files are read directly into Python `io.BytesIO` binary streams in RAM.
2. **Pandas Processing**: `pandas.read_csv()` atau `pandas.read_excel()` dipanggil untuk membaca buffer memori tersebut menjadi DataFrame.
   Pandas parses the memory buffer into a DataFrame.
3. **Immediate Cleanup**: Segera setelah data DataFrame disamarkan, hasilnya ditulis kembali ke buffer `io.BytesIO` keluaran dan dialirkan kembali ke browser menggunakan `StreamingResponse`. Buffer memori segera dilepaskan setelah koneksi ditutup.
   Once masked, the DataFrame is written to an output `io.BytesIO` buffer and streamed back via `StreamingResponse`. Memory buffers are released immediately after the connection terminates.

---

## 3. Pola Desain: Strategy Pattern / Design Pattern: Strategy Pattern

Logika penyamaran data mengimplementasikan **Strategy Pattern** untuk mendukung ekstensibilitas aturan penyamaran baru di masa depan.
The data masking engine utilizes the **Strategy Pattern** to support easy extension of masking rules:

* **Context**: Fungsi `mask_dataframe` di [masker.py](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/backend/app/services/masker.py) mengiterasi kolom-kolom DataFrame dan mencocokkan setiap aturan yang dipilih dengan fungsi strategi penyamaran yang sesuai.
  Iterates over columns and applies the correct strategy dynamically based on user configuration.
* **Strategies**:
  - `No Masking`: Mengabaikan penyamaran dan membiarkan data asli.
  - `Fake Name`: Menghasilkan nama acak (lokal Indonesia / global) via `Faker.name()`.
  - `Fake Email`: Menghasilkan alamat email acak unik via `Faker.ascii_free_email()`.
  - `Fake Phone`: Menghasilkan nomor telepon acak dengan kombinasi format lokal `08...` dan internasional `+628...`.
  - `Anonymize ID/Number`: Menyandikan digit angka/huruf secara konsisten menggunakan caching memori lokal (`scramble_id` dengan cache) agar nilai masukan yang sama selalu menghasilkan keluaran acak yang sama dalam satu berkas pengerjaan.
  - `Perturb Numeric`: Menyimpangkan nilai numerik dengan rentang variasi acak sebesar $\pm 20\%$ untuk kebutuhan data keuangan (misal: gaji atau volume transaksi).

---

## 4. Desain Basis Data & Audit Log / Database Design & Audit Logs

Aplikasi menggunakan database SQLite untuk menyimpan informasi administratif dan metadata kepatuhan (compliance). Penggunaan SQLModel mengabstraksi pemetaan tabel SQLite ke objek Python.
The application uses SQLite to store administrative and compliance metadata, mapped via SQLModel.

### Skema Relasi / Entity-Relationship Schema

```
  +------------------+             +----------------------+
  |      users       |             |     masking_jobs     |
  +------------------+             +----------------------+
  | id (PK)          |1--------0..*| id (PK)              |
  | username         |             | user_id (FK -> users)|
  | email            |             | file_name            |
  | password_hash    |             | file_size_bytes      |
  | created_at       |             | row_count            |
  +------------------+             | status               |
                                   | error_message        |
                                   | created_at           |
                                   +----------------------+
                                               | 1
                                               |
                                               | 1..*
                                   +----------------------+
                                   |     job_details      |
                                   +----------------------+
                                   | id (PK)              |
                                   | job_id (FK -> jobs)  |
                                   | column_name          |
                                   | rule_name            |
                                   +----------------------+
```

* **Cascade Delete**: Relasi asing (foreign key) dari tabel `users` ke `masking_jobs`, serta dari `masking_jobs` ke `job_details` diatur dengan opsi `ondelete="CASCADE"`. Menghapus akun pengguna akan secara otomatis menghapus seluruh log pengerjaan dan detail kolom yang terkait untuk kepatuhan privasi data.
  Foreign keys are configured with `ondelete="CASCADE"`. Deleting a user automatically purges all related jobs and job details to maintain complete data privacy.
