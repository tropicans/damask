Entity Relationship Diagram (ERD)
Untuk arsitektur berbasis web, kita memerlukan database ringan untuk menyimpan data pengguna, konfigurasi bawaan (default mapping rule), dan audit log demi kepatuhan keamanan perusahaan.

Berikut adalah rancangan struktur data logisnya.

Representasi Teks ERD (Relasi Kontrak Data)
 [User] 1 -------- 0..* [MaskingJob]
                           1
                           |
                           | 1..*
                     [JobDetail]
                           *
                           | 1
                      [MaskingRule]
Penjelasan Detail Tabel & Skema
1. Tabel users
Menyimpan informasi pengguna yang memiliki akses ke aplikasi ini.

user_id (UUID, Primary Key)

username (VARCHAR)

email (VARCHAR, Unique)

password_hash (VARCHAR)

created_at (TIMESTAMP)

2. Tabel masking_rules
Menyimpan definisi taksonomi masking yang tersedia di sistem (berfungsi sebagai master data).

rule_id (INT, Primary Key)

rule_name (VARCHAR) - Contoh: "Fake Name", "Fake Email", "Numeric Perturbation"

description (TEXT)

3. Tabel masking_jobs
Mencatat riwayat aktivitas eksekusi masking berkas untuk kebutuhan audit (tidak menyimpan isi file).

job_id (UUID, Primary Key)

user_id (UUID, Foreign Key ke users.user_id)

file_name (VARCHAR) - Nama berkas asli, misal: "data_penjualan.xlsx"

file_size_kb (INT)

total_rows (INT)

status (VARCHAR) - Contoh: "Success", "Failed"

processed_at (TIMESTAMP)

4. Tabel job_details
Mencatat kolom apa saja yang disamarkan dalam satu aktivitas pengerjaan (job), berguna untuk melihat tren kolom sensitif apa yang paling sering diproses.

detail_id (UUID, Primary Key)

job_id (UUID, Foreign Key ke masking_jobs.job_id)

column_name (VARCHAR) - Nama kolom yang dideteksi, misal: "no_hp"

rule_id (INT, Foreign Key ke masking_rules.rule_id)