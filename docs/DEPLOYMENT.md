# Panduan Penerapan / Deployment Guide

Dokumen ini menjelaskan langkah-langkah untuk menyebarkan (deploy) aplikasi **SecureData Web** dalam lingkungan produksi dan pengembangan menggunakan Docker Compose, serta penjelasan mengenai konfigurasi variabel lingkungan (environment variables).

This document outlines the steps to deploy **SecureData Web** in production and development environments using Docker Compose, along with environment variable configurations.

---

## 1. Persyaratan Sistem / Prerequisites

Pastikan perangkat lunak berikut telah terinstal pada server atau mesin target:
Ensure the following software is installed on the target server/machine:

* **Docker** (v20.10+)
* **Docker Compose** (v2.0+)

---

## 2. Variabel Lingkungan / Environment Variables

Aplikasi dikonfigurasi menggunakan variabel lingkungan. Berikut adalah variabel kunci yang digunakan:
The application is configured using environment variables. The key variables used are:

### Backend Config (`backend/.env`)

| Variabel / Variable | Tipe / Type | Deskripsi / Description | Default / Contoh |
| :--- | :--- | :--- | :--- |
| `PROJECT_NAME` | String | Nama aplikasi / Name of the project | `SecureData Web` |
| `PORT` | Integer | Port internal uvicorn / Internal uvicorn port | `8000` |
| `CORS_ALLOWED_ORIGINS` | JSON List | Asal CORS yang diizinkan / Allowed CORS origins | `["http://localhost:5173"]` |
| `DATABASE_URL` | String | URL Database (SQLite/PostgreSQL) / Database URL | `sqlite:///datamask.db` |
| `JWT_SECRET_KEY` | String | Kunci rahasia JWT / JWT signing secret key | `secret-key-for-dev-purposes-change-in-prod` |
| `JWT_ALGORITHM` | String | Algoritma tanda tangan JWT / JWT signature algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Integer | Masa berlaku token akses (menit) / Token expiration | `1440` (24 Jam) |

### Frontend Config (`frontend/.env` atau Docker Env)

| Variabel / Variable | Deskripsi / Description | Contoh / Example |
| :--- | :--- | :--- |
| `VITE_API_URL` | URL Endpoint API Backend / Backend API endpoint URL | `http://localhost:8000` |

---

## 3. Deployment Menggunakan Docker Compose / Deployment using Docker Compose

Docker Compose mengotomatisasi pembangunan dan startup kontainer backend dan frontend secara bersamaan.
Docker Compose automates the build and startup of both backend and frontend containers.

### Perintah Menjalankan Aplikasi / Commands to Run App

1. **Jalankan Pembangunan & Jalankan Layanan / Build & Run Services**:
   ```bash
   docker compose up --build -d
   ```
   *Bendera `-d` menjalankan layanan di latar belakang (detached mode).*
   *The `-d` flag runs services in the background (detached mode).*

2. **Periksa Status Layanan / Check Service Status**:
   ```bash
   docker compose ps
   ```

3. **Melihat Log Kontainer / View Container Logs**:
   ```bash
   docker compose logs -f
   ```

4. **Menghentikan Layanan / Stop Services**:
   ```bash
   docker compose down
   ```

---

## 4. Konfigurasi Port & Volume / Port & Volume Configurations

### Port Mapping

* **Frontend**: Dapat diakses melalui port `5173` (`http://localhost:5173`).
* **Backend**: Dapat diakses melalui port `8000` (`http://localhost:8000`).

### Volume & Data Persistence

Aplikasi memproses file sensitif secara transient di RAM buffer dan tidak menyimpannya ke disk. Namun, metadata audit log dan informasi akun pengguna disimpan dalam SQLite Database.
The application processes sensitive files transiently in RAM buffers and does not save them to disk. However, audit log metadata and user account details are stored in the SQLite Database.

Secara default di `docker-compose.yml`, volume lokal di-mount ke kontainer untuk memfasilitasi persistensi database selama pengembangan:
By default in `docker-compose.yml`, local volumes are mounted to the container to facilitate database persistence during development:

* **Backend Volume**: `./backend:/workspace`
  * Berkas SQLite DB (`datamask.db` atau `test.db` / `test_jobs.db`) akan di-persist di direktori lokal `./backend` pada host mesin Anda.
  * SQLite DB files will be persisted in the local `./backend` directory on the host machine.
* **Frontend Volume**: `./frontend:/workspace`

---

## 5. Keamanan & Production Hardening / Security Guidelines

1. **Ganti JWT Secret Key**: Pastikan Anda mengganti `JWT_SECRET_KEY` dengan string acak yang kuat sebelum dijalankan di produksi.
   Change the `JWT_SECRET_KEY` with a strong random string before deploying to production.
2. **Batasi CORS**: Ubah `CORS_ALLOWED_ORIGINS` hanya ke domain frontend spesifik Anda (misalnya `["https://datamask.perusahaan.com"]`).
   Restrict `CORS_ALLOWED_ORIGINS` to your specific frontend domain.
3. **Konfigurasi SSL/TLS**: Jalankan aplikasi di balik reverse proxy (seperti Nginx atau Traefik) untuk menangani enkripsi SSL/TLS (HTTPS).
   Run the application behind a reverse proxy (e.g., Nginx or Traefik) to handle SSL/TLS (HTTPS) encryption.
