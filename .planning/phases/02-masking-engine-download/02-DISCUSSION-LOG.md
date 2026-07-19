# Phase 2: Masking Engine & Download - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 02-masking-engine-download
**Areas discussed:** Lokalisasi Faker, Algoritma Perturbasi Numerik, Pola Pengacakan ID, Mekanisme Streaming Download

---

## Lokalisasi Faker (Faker Localization)

### Kebijakan Locale untuk generator Faker yang akan dipasang?

| Option | Description | Selected |
|--------|-------------|----------|
| Kombinasi id_ID & en_US | Gunakan nama/telepon Indonesia, fallback ke global untuk field lain seperti domain/email | ✓ |
| Hanya id_ID | Semua data tiruan menggunakan format Indonesia | |
| Hanya en_US | Semua data tiruan menggunakan format global/internasional | |

**User's choice:** Kombinasi id_ID & en_US
**Notes:** -

### Bagaimana format nomor telepon Indonesia (Fake Phone) yang dihasilkan?

| Option | Description | Selected |
|--------|-------------|----------|
| Dinamis campuran | Acak antara format lokal '08xxxxxx' dan format internasional '+628xxxxxx' | ✓ |
| Seragam Internasional | Selalu diawali dengan '+628xxxxxx' | |
| Seragam Lokal | Selalu diawali dengan '08xxxxxx' | |

**User's choice:** Dinamis campuran
**Notes:** -

---

## Algoritma Perturbasi Numerik (Numeric Perturbation)

### Bagaimana penanganan tipe data numerik saat dilakukan perturbasi?

| Option | Description | Selected |
|--------|-------------|----------|
| Smart Typing | Bulatkan ke integer terdekat jika nilai asli berupa integer; pertahankan desimal jika nilai asli desimal/float | ✓ |
| Selalu Float | Konversi semua nilai hasil perturbasi menjadi bilangan desimal (misal dengan 2 angka di belakang koma) | |
| Selalu Integer | Selalu bulatkan hasil perturbasi menjadi bilangan bulat terdekat tanpa desimal | |

**User's choice:** Smart Typing
**Notes:** -

### Bagaimana penanganan sel kosong atau nilai non-numerik di kolom numerik saat perturbasi?

| Option | Description | Selected |
|--------|-------------|----------|
| Lewati & Pertahankan | Lewati sel kosong atau non-numerik tersebut dan biarkan nilainya tetap sama seperti aslinya | ✓ |
| Ganti dengan Default | Ganti sel kosong/non-numerik dengan angka default (misal 0) lalu terapkan perturbasi | |
| Gagal & Laporkan | Berikan error validasi ke pengguna bahwa kolom numerik berisi data non-numerik | |

**User's choice:** Lewati & Pertahankan
**Notes:** -

---

## Pola Pengacakan ID (ID Anonymization Strategy)

### Bagaimana cara pengacakan (anonymizing) ID/Nomor unik yang diinginkan?

| Option | Description | Selected |
|--------|-------------|----------|
| Format-preserving Scrambling | Acak digit angka dengan angka baru (0-9) dan huruf dengan huruf baru (A-Z/a-z), mempertahankan tanda hubung/titik serta panjang aslinya | ✓ |
| Hash SHA-256 | Ubah setiap ID unik menjadi hash satu arah SHA-256 (menjamin konsistensi jika nilai yang sama diacak berulang) | |
| UUID Acak | Ganti setiap ID secara acak dengan UUID baru (seperti '550e8400-e29b-41d4-a716-446655440000') | |

**User's choice:** Format-preserving Scrambling
**Notes:** -

### Apakah hasil pengacakan ID yang sama dalam satu file harus konsisten (deterministik)?

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministik per File | Nilai ID yang sama di file yang sama akan selalu diacak menjadi hasil yang sama (mempertahankan relasi dan integritas data untuk analisis) | ✓ |
| Acak Independen | Setiap sel diacak secara terpisah tanpa memedulikan baris lain (ID yang sama di baris berbeda akan mendapat hasil acak yang berbeda) | |

**User's choice:** Deterministik per File
**Notes:** -

---

## Mekanisme Streaming Download (Streaming Download)

### Bagaimana penamaan berkas hasil masking yang diunduh oleh pengguna?

| Option | Description | Selected |
|--------|-------------|----------|
| Suffix '_masked' sebelum ekstensi | Contoh: 'data_karyawan_masked.xlsx' | ✓ |
| Prefix 'masked_' sebelum nama file | Contoh: 'masked_data_karyawan.xlsx' | |
| Nama file asli persis | Contoh: 'data_karyawan.xlsx' | |

**User's choice:** Suffix '_masked' sebelum ekstensi
**Notes:** -

### Bagaimana penanganan error eksekusi masking di tengah proses pengolahan file?

| Option | Description | Selected |
|--------|-------------|----------|
| Transactional Fail-fast | Hentikan seluruh proses masking seketika, bersihkan RAM buffer, dan kembalikan pesan error HTTP 500/400 (tidak mengirim file setengah matang demi keamanan) | ✓ |
| Partial Masking (Best Effort) | Abaikan baris yang bermasalah (lewati/kosongkan) dan lanjutkan proses masking baris lainnya agar file tetap dapat diunduh, dengan catatan log/peringatan | |

**User's choice:** Transactional Fail-fast
**Notes:** -

---

## the agent's Discretion

Tidak ada area khusus yang diserahkan sepenuhnya kepada AI ("You decide"); semua keputusan di atas dipilih dan disepakati oleh pengguna.

---

## Deferred Ideas

Tidak ada ide tertunda yang dicatat selama sesi diskusi ini.
