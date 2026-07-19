# Spesifikasi API / API Specification

Dokumen ini menjelaskan spesifikasi API HTTP untuk layanan backend **SecureData Web**.
This document describes the HTTP API specifications for the **SecureData Web** backend service.

---

## 1. Konfigurasi Dasar / General Configurations

* **Base URL**: `http://localhost:8000/api`
* **Format Payload**: JSON (kecuali untuk unggahan berkas menggunakan `multipart/form-data`)
  Payload Format: JSON (except for file uploads using `multipart/form-data`)
* **Headers Umum**: 
  - `Authorization`: `Bearer <token_jwt>` (diperlukan untuk endpoint terproteksi / required for protected endpoints)

---

## 2. API Otentikasi / Authentication Endpoints (Prefix: `/auth`)

### 2.1. Pendaftaran Pengguna / Register User
Mendaftarkan akun pengguna baru ke sistem.
Registers a new user account.

* **URL**: `/auth/register`
* **Method**: `POST`
* **Request Body** (JSON):
  ```json
  {
    "username": "budi_developer",
    "email": "budi@perusahaan.com",
    "password": "PasswordSangatRahasia123!"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "id": "1f8e136b-67be-4074-a63e-32ea8cb3d790",
    "username": "budi_developer",
    "email": "budi@perusahaan.com",
    "created_at": "2026-07-19T04:00:00Z"
  }
  ```
* **Response (400 Bad Request)**:
  - Mengembalikan detail jika email sudah terdaftar atau skema masukan tidak valid.
    Returns error details if the email is already registered or schema is invalid.
  ```json
  {
    "detail": "Email sudah terdaftar."
  }
  ```

### 2.2. Masuk Pengguna / Login
Verifikasi kredensial pengguna dan mengembalikan token akses JWT.
Verifies credentials and returns a JWT access token.

* **URL**: `/auth/login`
* **Method**: `POST`
* **Request Body** (JSON):
  ```json
  {
    "email": "budi@perusahaan.com",
    "password": "PasswordSangatRahasia123!"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "1f8e136b-67be-4074-a63e-32ea8cb3d790",
      "username": "budi_developer",
      "email": "budi@perusahaan.com",
      "created_at": "2026-07-19T04:00:00Z"
    }
  }
  ```
* **Response (400 Bad Request)**:
  ```json
  {
    "detail": "Email atau kata sandi salah."
  }
  ```

### 2.3. Informasi Pengguna Aktif / Current User Info
Mengembalikan informasi profil dari token JWT yang dilampirkan.
Returns profile information for the current authenticated user.

* **URL**: `/auth/me`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Response (200 OK)**:
  ```json
  {
    "id": "1f8e136b-67be-4074-a63e-32ea8cb3d790",
    "username": "budi_developer",
    "email": "budi@perusahaan.com",
    "created_at": "2026-07-19T04:00:00Z"
  }
  ```
* **Response (401 Unauthorized)**:
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

---

## 3. API Pratinjau Berkas / File Preview Endpoints (Prefix: `/preview`)

### 3.1. Dapatkan Pratinjau Berkas / Get File Preview
Mengunggah berkas untuk dianalisis struktur kolomnya dan mengambil data sampel pratinjau.
Uploads a file to inspect its columns and obtain sample rows.

* **URL**: `/preview/preview`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Request Body** (`multipart/form-data`):
  - `file`: Berkas biner (`.csv`, `.xlsx`, `.xls` maksimal 50MB)
* **Response (200 OK)**:
  ```json
  {
    "filename": "data_karyawan.xlsx",
    "size_bytes": 10240,
    "headers": ["id", "nama_karyawan", "surel", "nomor_kontak"],
    "preview_rows": [
      ["1", "Budi Utomo", "budi@perusahaan.com", "08123456789"],
      ["2", "Siti Aminah", "siti@perusahaan.com", "08567891234"],
      ["3", "Joko Susilo", "joko@perusahaan.com", "+62811122233"]
    ],
    "recommendations": {
      "id": "No Masking",
      "nama_karyawan": "Fake Name",
      "surel": "Fake Email",
      "nomor_kontak": "Fake Phone"
    }
  }
  ```
* **Response (400 Bad Request)**:
  - Mengembalikan detail kesalahan jika format file tidak didukung.
  ```json
  {
    "detail": "Format file tidak didukung. Hanya .csv dan .xlsx yang didukung."
  }
  ```
* **Response (413 Payload Too Large)**:
  - Ukuran file melebihi batas 50MB.
  ```json
  {
    "detail": "File terlalu besar. Maksimum ukuran file adalah 50MB."
  }
  ```

---

## 4. API Penyamaran Berkas / File Masking Endpoints (Prefix: `/mask`)

### 4.1. Masking Berkas / Mask File
Mengunggah berkas bersama dengan konfigurasi pemetaan aturan masking, menyamarkan data secara in-memory, dan langsung memicu download berkas terproses.
Uploads a file with masking configurations, applies masking in memory, and returns the processed file as a download stream.

* **URL**: `/mask/mask`
* **Method**: `POST`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Request Body** (`multipart/form-data`):
  - `file`: Berkas biner (`.csv`, `.xlsx`, `.xls`)
  - `rules`: JSON String berisi pemetaan aturan kolom, misal:
    `{"nama_karyawan": "Fake Name", "surel": "Fake Email", "nomor_kontak": "Fake Phone"}`
* **Response (200 OK)**:
  - Aliran biner file ter-masking (Binary stream of masked file).
  - **Headers**:
    - `Content-Type`: `text/csv` atau `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
    - `Content-Disposition`: `attachment; filename=data_karyawan_masked.xlsx`
    - `Access-Control-Expose-Headers`: `Content-Disposition`
* **Response (400 Bad Request)**:
  ```json
  {
    "detail": "Gagal memproses penyamaran berkas: Kolom 'gaji' tidak ditemukan."
  }
  ```

---

## 5. API Riwayat & Statistik / Job History & Stats Endpoints (Prefix: `/jobs`)

### 5.1. Daftar Riwayat Pekerjaan / List Jobs History
Mengembalikan daftar riwayat aktivitas masking milik pengguna terautentikasi (dipaginasi).
Returns paginated list of masking job history for the authenticated user.

* **URL**: `/jobs/`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Query Parameters**:
  - `skip`: Integer (default `0`, nilai minimum `0`)
  - `limit`: Integer (default `10`, nilai minimum `1`, nilai maksimum `100`)
* **Response (200 OK)**:
  ```json
  [
    {
      "id": "e44cb89d-7f8e-49b0-9cf6-04db801b7a2d",
      "user_id": "1f8e136b-67be-4074-a63e-32ea8cb3d790",
      "file_name": "data_karyawan.xlsx",
      "file_size_bytes": 10240,
      "row_count": 150,
      "status": "SUCCESS",
      "error_message": null,
      "created_at": "2026-07-19T04:15:00Z"
    }
  ]
  ```

### 5.2. Statistik Pekerjaan / Get Jobs Stats
Mengembalikan akumulasi statistik volume masking pengguna.
Returns aggregated statistics of masking activity for the user.

* **URL**: `/jobs/stats`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Response (200 OK)**:
  ```json
  {
    "total_files": 12,
    "total_rows": 2400,
    "success_rate": 92.31
  }
  ```

### 5.3. Rincian Kolom Pekerjaan / Get Job Details
Mendapatkan detail kolom apa saja yang disamarkan dalam satu pengerjaan tertentu.
Returns columns and rules processed for a specific job.

* **URL**: `/jobs/{job_id}/details`
* **Method**: `GET`
* **Headers**: `Authorization: Bearer <token_jwt>`
* **Response (200 OK)**:
  ```json
  [
    {
      "id": "89c8913b-aa56-4299-a541-11d4d3d8ca8f",
      "job_id": "e44cb89d-7f8e-49b0-9cf6-04db801b7a2d",
      "column_name": "nama_karyawan",
      "rule_name": "Fake Name"
    },
    {
      "id": "90e5138a-f5e6-4ff3-98ca-22e3e5bc617b",
      "job_id": "e44cb89d-7f8e-49b0-9cf6-04db801b7a2d",
      "column_name": "surel",
      "rule_name": "Fake Email"
    }
  ]
  ```
* **Response (403 Forbidden)**:
  - Mengembalikan kesalahan jika mencoba mengakses pekerjaan milik pengguna lain.
  ```json
  {
    "detail": "Anda tidak memiliki akses ke data pekerjaan penyamaran ini."
  }
  ```
* **Response (404 Not Found)**:
  ```json
  {
    "detail": "Pekerjaan penyamaran tidak ditemukan."
  }
  ```
