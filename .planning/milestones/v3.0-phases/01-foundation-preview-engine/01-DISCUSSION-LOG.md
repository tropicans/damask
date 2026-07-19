# Phase 1: Foundation & Preview Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-19
**Phase:** 1-Foundation & Preview Engine
**Areas discussed:** Format File, Lokasi Regex, Styling CSS, File Besar

---

## Format File

| Option | Description | Selected |
|--------|-------------|----------|
| Hanya dukung .xlsx dan .csv untuk v1 | Menjaga dependensi backend tetap ramping dan aman, menunda .xls ke v2 | ✓ |
| Dukung .xlsx, .csv, dan .xls | Menggunakan xlrd tambahan di backend untuk memproses berkas Excel lama | |
| You decide | Serahkan keputusan teknis ini kepada AI | |

**User's choice:** Hanya dukung .xlsx dan .csv untuk v1 (Menjaga dependensi backend tetap ramping dan aman, menunda .xls ke v2)
**Notes:** Menunda format .xls untuk meminimalkan risiko keamanan pustaka tambahan dan mempercepat deliverable v1.

---

## Lokasi Regex

| Option | Description | Selected |
|--------|-------------|----------|
| Menggunakan file konfigurasi eksternal (JSON/YAML) | Memudahkan perubahan dan kustomisasi aturan regex tanpa menyentuh kode Python backend | ✓ |
| Hardcoded di dalam kode backend Python | Lebih cepat diimplementasikan untuk v1, namun tidak fleksibel jika ada perubahan pola | |
| You decide | Serahkan keputusan teknis ini kepada AI | |

**User's choice:** Menggunakan file konfigurasi eksternal (JSON/YAML) (Memudahkan perubahan dan kustomisasi aturan regex tanpa menyentuh kode Python backend)
**Notes:** Regex akan dimuat secara dinamis oleh backend FastAPI.

---

## Styling CSS

| Option | Description | Selected |
|--------|-------------|----------|
| Menggunakan TailwindCSS v3 | Direkomendasikan jika ingin memakai shadcn/ui dan komponen siap pakai | ✓ |
| Menggunakan Vanilla CSS | Meningkatkan kontrol penuh atas styling, performa super cepat, tanpa dependensi build Tailwind | |
| Menggunakan TailwindCSS v4 | Versi terbaru TailwindCSS dengan CSS-first configuration | |
| You decide | Serahkan keputusan styling kepada AI | |

**User's choice:** Menggunakan TailwindCSS v3 (Direkomendasikan jika ingin memakai shadcn/ui dan komponen siap pakai)
**Notes:** Menyelaraskan dengan STACK.md yang menyebutkan Tailwind & shadcn/ui untuk mempercepat pengembangan antarmuka drag-and-drop.

---

## File Besar

| Option | Description | Selected |
|--------|-------------|----------|
| Lakukan chunk parsing / read_rows terbatas | Membaca hanya beberapa baris pertama untuk CSV/Excel tanpa me-load seluruh 50MB ke RAM saat preview | ✓ |
| Parsing seluruh file saat preview | Lebih sederhana diimplementasikan, memuat seluruh data ke Pandas DataFrame dari awal, namun RAM akan meningkat signifikan saat file berukuran 50MB diunggah | |
| You decide | Serahkan keputusan optimasi ini kepada AI | |

**User's choice:** Lakukan chunk parsing / read_rows terbatas (Membaca hanya beberapa baris pertama untuk CSV/Excel tanpa me-load seluruh 50MB ke RAM saat preview)
**Notes:** Mengoptimalkan RAM server backend dan mencegah pemblokiran event-loop FastAPI.

---

## the agent's Discretion

Tidak ada keputusan yang diserahkan sepenuhnya ke AI discretion.

---

## Deferred Ideas

- Dukungan format Excel lama (`.xls`) ditangguhkan ke v2 (atau fase berikutnya).
