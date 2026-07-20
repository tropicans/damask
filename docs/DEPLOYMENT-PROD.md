# Panduan Deployment Produksi / Production Deployment Guide

Dokumen ini menjelaskan langkah-langkah untuk menyebarkan (deploy) **SecureData Web** di lingkungan produksi menggunakan Docker Compose, Nginx Reverse Proxy, dan Cloudflare Tunnel untuk perlindungan port serta akses HTTPS aman.

This document outlines the steps to deploy **SecureData Web** in a production environment using Docker Compose, Nginx Reverse Proxy, and Cloudflare Tunnel for port hardening and secure HTTPS access.

---

## 1. Arsitektur Deployment / Deployment Architecture

Aplikasi ini dideploy dengan topologi keamanan berikut:
The application is deployed with the following security topology:

* **Nginx Container:** Bertindak sebagai pintu gerbang HTTP lokal (reverse proxy), meneruskan `/api` ke backend dan semua traffic lainnya ke frontend. Port 80 Nginx hanya terikat ke localhost (`127.0.0.1:80:80`).
  Acts as a local HTTP reverse proxy routing `/api` to the backend and all other traffic to the frontend. Nginx port 80 is bound exclusively to localhost (`127.0.0.1:80:80`).
* **Port Hardening:** Port internal backend (`8000`), frontend (`5173`), dan database (`5432`) **tidak** diekspos ke host maupun internet.
  Internal ports for backend (`8000`), frontend (`5173`), and database (`5432`) are **not** exposed to the host or the internet.
* **Cloudflare Tunnel:** Menghubungkan server VPS secara outbound ke Cloudflare Edge. SSL/TLS diterminasi di Cloudflare, lalu diteruskan ke `http://localhost:80` (Nginx). Port masuk HTTP (80) dan HTTPS (443) pada firewall VPS tetap tertutup.
  Connects the VPS server outbound to the Cloudflare Edge. SSL/TLS is terminated at the Cloudflare Edge, then routed locally to `http://localhost:80` (Nginx). Inbound HTTP (80) and HTTPS (443) ports remain closed on the VPS firewall.

---

## 2. Persiapan VPS & Pengerasan Firewall / VPS Setup & Firewall Hardening

### A. Persyaratan Awal / Prerequisites
Pastikan perangkat lunak berikut terinstal di VPS target:
Ensure the following software is installed on the target VPS:
* **Docker** (v20.10+) & **Docker Compose** (v2.0+)
* **Git**

### B. Pengerasan Firewall dengan UFW / Firewall Hardening with UFW
Untuk mencegah akses langsung dari luar, konfigurasikan UFW untuk hanya mengizinkan akses SSH (port 22). Port 80 dan 443 tetap ditutup karena Cloudflare Tunnel menggunakan koneksi keluar (outbound connection).

To prevent direct external access, configure UFW to allow only SSH (port 22). Ports 80 and 443 remain closed because Cloudflare Tunnel connects outbound.

```bash
# Set default policy
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Izinkan SSH / Allow SSH
sudo ufw allow 22/tcp

# Aktifkan Firewall / Enable Firewall
sudo ufw enable

# Cek status / Check status
sudo ufw status verbose
```

---

## 3. Variabel Lingkungan Produksi / Production Environment Variables

Buat berkas `.env` di direktori utama proyek (root directory) pada VPS Anda.
Create a `.env` file in the project's root directory on your VPS.

```dotenv
# =============================================================================
# SecureData Web — Production Environment Variables
# =============================================================================

# 1. Database (PostgreSQL)
# Ganti dengan password acak dan aman / Change to a secure random password
POSTGRES_PASSWORD=secure_postgres_db_password_change_me

# 2. Keamanan Backend / Backend Security Settings
# Generate dengan: openssl rand -hex 32
JWT_SECRET_KEY=production_jwt_signing_secret_key_change_me

# Set True untuk HTTPS cookie security / Set to True for HTTPS cookie security
COOKIE_SECURE=true

# 3. CORS & URLs
# Ubah ke domain produksi Cloudflare Anda / Set to your production Cloudflare domain
CORS_ALLOWED_ORIGINS=["https://securedata.yourdomain.com"]
FRONTEND_URL=https://securedata.yourdomain.com

# 4. Frontend API Endpoint
VITE_API_URL=https://securedata.yourdomain.com
```

---

## 4. Menjalankan Aplikasi / Running the Application

Jalankan perintah berikut pada direktori utama proyek untuk membangun dan menjalankan seluruh layanan (Database, Backend, Frontend, Nginx) secara aman:

Run the following command in the project root directory to build and start all services (Database, Backend, Frontend, Nginx) securely:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Verifikasi kontainer berjalan dengan benar:
Verify containers are running properly:

```bash
docker compose -f docker-compose.prod.yml ps
```

---

## 5. Konfigurasi Cloudflare Tunnel / Cloudflare Tunnel Integration

Cloudflare Tunnel bertindak sebagai perantara aman tanpa harus membuka port inbound pada VPS.
Cloudflare Tunnel acts as a secure proxy without opening any inbound ports on the VPS.

1. **Buat Tunnel Baru / Create a New Tunnel:**
   Buka dashboard Cloudflare Zero Trust, navigasikan ke **Access** > **Tunnels**, lalu klik **Create a Tunnel**.
   Go to Cloudflare Zero Trust Dashboard, navigate to **Access** > **Tunnels**, and click **Create a Tunnel**.

2. **Instal cloudflared di VPS / Install cloudflared on VPS:**
   Pilih opsi instalasi lingkungan VPS Anda (misalnya Debian/Ubuntu) dan jalankan perintah konektor yang disediakan Cloudflare di VPS Anda.
   Choose your VPS environment (e.g. Debian/Ubuntu) and run the connector commands provided by Cloudflare on your VPS.

3. **Konfigurasi Routing Ingress / Configure Ingress Routing:**
   Di halaman konfigurasi Tunnel, tentukan Public Hostname:
   On the Tunnel configuration page, define the Public Hostname:
   * **Domain:** `securedata.yourdomain.com` (Ganti dengan domain Anda / Replace with your domain)
   * **Service Type:** `HTTP`
   * **URL:** `localhost:80` (Meneruskan traffic ke port localhost Nginx / Forward traffic to localhost port of Nginx)

4. Simpan Tunnel. Aplikasi sekarang dapat diakses secara aman melalui HTTPS di domain Anda.
   Save the Tunnel. Your application is now securely accessible via HTTPS on your domain.

---

## 6. Strategi Cadangan Database (Backups) / Database Backup Strategy

Untuk menjaga keamanan data, port PostgreSQL (`5432`) tidak boleh diekspos ke host atau internet. Proses backup dijalankan menggunakan utilitas `pg_dump` dari dalam kontainer database Docker.

To ensure data security, PostgreSQL port (`5432`) must not be exposed. Backups are executed using `pg_dump` from inside the database container.

### A. Perintah Backup Manual / Manual Backup Command
Jalankan perintah ini di VPS untuk mencadangkan database secara manual:
Run this command on the VPS to back up the database manually:

```bash
# Buat direktori backup / Create backup directory
mkdir -p ~/backups

# Jalankan pg_dump di kontainer / Run pg_dump inside container
docker exec -t $(docker compose -f docker-compose.prod.yml ps -q db) pg_dump -U securedata_user -d securedata > ~/backups/securedata_backup_$(date +%F_%H%M%S).sql
```

### B. Otomatisasi Backup dengan Cron / Automatic Backups via Cron
Anda dapat mengotomatiskan backup database setiap hari pada pukul 02:00 pagi menggunakan Cron.
You can automate database backups daily at 02:00 AM using Cron.

1. Buka konfigurasi crontab:
   Open crontab configuration:
   ```bash
   crontab -e
   ```

2. Tambahkan baris template berikut (pastikan path ke folder proyek sudah benar):
   Add the following template line (ensure path to project folder is correct):
   ```cron
   0 2 * * * cd /path/to/your/project && docker exec -t $(docker compose -f docker-compose.prod.yml ps -q db) pg_dump -U securedata_user -d securedata > ~/backups/securedata_backup_$(date +\%F).sql 2>&1
   ```

---

## 7. Alternatif: Ingress Langsung dengan Let's Encrypt & Certbot / Alternative: Direct Ingress with Let's Encrypt & Certbot

Jika Anda **tidak** menggunakan Cloudflare Tunnel dan ingin melayani traffic HTTPS langsung dari VPS menggunakan Let's Encrypt:

If you are **not** using Cloudflare Tunnel and want to serve HTTPS traffic directly from the VPS using Let's Encrypt:

### A. Ubah Konfigurasi Port / Modify Port Configuration
1. Perbarui `docker-compose.prod.yml` untuk memetakan port Nginx ke seluruh jaringan (`0.0.0.0`) bukan localhost saja:
   Update `docker-compose.prod.yml` to map Nginx ports to the public interface (`0.0.0.0`):
   ```yaml
   # docker-compose.prod.yml (Nginx service ports)
   ports:
     - "80:80"
     - "443:443"
   ```

2. Buka port 80 dan 443 pada firewall UFW VPS:
   Open ports 80 and 443 on the VPS UFW firewall:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

### B. Setup Certbot & Let's Encrypt di Host VPS / Setup Certbot & Let's Encrypt on Host VPS
1. Pasang Certbot di VPS:
   Install Certbot on the VPS:
   ```bash
   sudo apt update
   sudo apt install certbot -y
   ```

2. Generate sertifikat SSL Let's Encrypt:
   Generate Let's Encrypt SSL certificates:
   ```bash
   sudo certbot certonly --standalone -d securedata.yourdomain.com
   ```

3. Mount sertifikat SSL dari VPS ke kontainer Nginx dan sesuaikan `nginx/nginx.conf` Anda untuk mendengarkan port 443 dan menggunakan berkas SSL.
   Mount SSL certificates from the VPS into the Nginx container and modify your `nginx/nginx.conf` to listen on port 443 and utilize SSL certificates.

### C. Otomatisasi Perpanjangan SSL / Auto SSL Renewal Automation
Sertifikat Let's Encrypt berlaku selama 90 hari. Konfigurasikan Cron untuk memperbaruinya secara otomatis:
Let's Encrypt certificates last for 90 days. Configure Cron to automatically renew them:

1. Buka crontab:
   Open crontab:
   ```bash
   crontab -e
   ```

2. Tambahkan baris pembaruan otomatis ini (dijalankan dua kali sehari):
   Add this auto-renewal line (runs twice daily):
   ```cron
   0 */12 * * * certbot renew --quiet --post-hook "docker compose -f /path/to/your/project/docker-compose.prod.yml restart nginx"
   ```
