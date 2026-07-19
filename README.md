# SecureData Web (LLM Data Masker Web Tool)

SecureData Web adalah aplikasi web internal/lokal yang memungkinkan pengguna mengunggah berkas CSV atau Excel (XLS/XLSX), mengonfigurasi aturan penyamaran (masking rules) kustom per kolom, dan mengunduh versi berkas yang telah aman secara anonim. Alat ini dirancang untuk mencegah kebocoran data sensitif (PII atau data finansial) ke LLM eksternal atau sistem cloud dengan memproses data secara eksklusif di dalam memori (RAM buffer) dan hanya mencatat metadata audit.

SecureData Web is a local/internal web application that allows users to upload CSV, XLS, and XLSX files containing sensitive personal identifiable information (PII) or financial data, configure custom masking rules per column, and download a safely anonymized version of the file. It prevents data leakage to external LLMs and cloud systems by processing uploads strictly in-memory and logging only job execution metadata.

---

## Fitur Utama / Key Features

1. **In-Memory Buffer Processing**: Data berkas diproses langsung dalam memori sementara (RAM) dan tidak disimpan di disk server / file system server.
2. **Auto Column Masking Recommendation**: Sistem mendeteksi nama kolom dan secara otomatis merekomendasikan jenis masking menggunakan pencocokan regex dari berkas konfigurasi.
3. **Flexible Masking Strategies**:
   - **Fake Name**: Mengganti nama asli dengan nama acak (kombinasi nama Indonesia/Global).
   - **Fake Email**: Mengganti email dengan format alamat email acak.
   - **Fake Phone**: Mengganti nomor telepon dengan format nomor telepon acak (lokal/internasional).
   - **Anonymize ID/Number**: Mengacak digit angka/karakter dengan konsistensi nilai yang sama (scrambling).
   - **Perturb Numeric**: Mengacak angka numerik/finansial dengan variasi acak sekitar $\pm 20\%$.
4. **Audit Dashboard**: Dasbor audit lokal untuk meninjau riwayat pekerjaan penyamaran tanpa menyimpan isi data.

---

## Arsitektur Sistem / System Architecture

Aplikasi ini menggunakan pemisahan yang jelas antara Frontend (React SPA) dan Backend (FastAPI).
The application uses a clean decoupling of Frontend (React SPA) and Backend (FastAPI).

```
   +----------------------+               +------------------------+
   |   React.js SPA       |  HTTP/JSON    |   FastAPI Backend      |
   |   (Vite/Tailwind)    | <===========> |   (Pandas/Faker/SQL)   |
   |   Port: 5173         |               |   Port: 8000           |
   +----------------------+               +------------------------+
              ^                                       |
              |                                       v
      (Uploads File & Rules)                (Local SQLite database)
                                            (Audit Logs: test.db)
```

---

## Panduan Memulai / Quickstart

### Metode A: Docker Compose (Disukai / Preferred)

Gunakan Docker Compose untuk membangun dan menjalankan aplikasi backend dan frontend secara bersamaan.
Use Docker Compose to build and run both backend and frontend applications concurrently.

```bash
# Jalankan kontainer / Run containers
docker compose up --build -d

# Akses aplikasi / Access application
# Frontend: http://localhost:5173
# Backend API Docs: http://localhost:8000/docs
```

---

### Metode B: Instalasi Lokal (Pengembangan / Local Development)

#### 1. Persiapan Backend / Backend Setup
Backend menggunakan Python 3.11+ dan Poetry untuk manajemen paket.
The backend uses Python 3.11+ and Poetry for package management.

```bash
cd backend

# Instalasi dependensi / Install dependencies
poetry install

# Aktifkan virtual environment / Activate virtual env
poetry shell

# Menjalankan server backend / Run backend server
poetry run uvicorn app.main:app --reload --port 8000
```

#### 2. Persiapan Frontend / Frontend Setup
Frontend menggunakan Node.js 20.x dan npm.
The frontend uses Node.js 20.x and npm.

```bash
cd frontend

# Instalasi dependensi / Install dependencies
npm install

# Jalankan server pengembangan / Run development server
npm run dev
```

Akses frontend di `http://localhost:5173`.

---

## Pengujian / Testing

### Backend Tests
Menjalankan pengujian unit dan integrasi untuk backend:
To run unit and integration tests for backend:

```bash
cd backend
$env:PYTHONPATH="."
poetry run pytest
```

---

## Dokumentasi Pendukung / Further Documentation

Detail dokumentasi teknis dapat dilihat di direktori `/docs`:
Detailed technical documentation can be found in the `/docs` directory:

* [docs/ARCHITECTURE.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/docs/ARCHITECTURE.md) — Struktur arsitektur dan pola desain.
* [docs/API-SPEC.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/docs/API-SPEC.md) — Rincian skema endpoint API.
* [docs/DEPLOYMENT.md](file:///c:/Users/X1%20Carbon/Downloads/Projects/self-hosted-ai-starter-kit/Dev/datamask/docs/DEPLOYMENT.md) — Panduan deployment produksi.
