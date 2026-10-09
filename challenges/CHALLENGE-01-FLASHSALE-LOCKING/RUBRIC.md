# Rubrik Penilaian: Tantangan 01 (Flash Sale Concurrency)

Evaluasi dilakukan menggunakan sistem penilaian terbobot dengan skala 0 hingga 100 poin. Penguji otomatis dan tim kurator memeriksa aspek teknis dan analitis berikut:

---

## Rincian Bobot Penilaian

### 1. Integritas DDL dan Relasi Basis Data (Bobot: 35 Poin)
- **Sintaksis Valid (10 Poin)**: DDL SQL dapat dieksekusi tanpa galat pada mesin basis data target.
- **Topological DAG (10 Poin)**: Skema bebas dari ketergantungan siklik (*circular foreign keys*) dan dapat di-create serta di-drop secara deterministik.
- **Constraint Proteksi Stok (10 Poin)**: Terdapat `CHECK (available_qty >= 0)` atau struktur reservasi terisolasi yang secara matematis mencegah kuota minus di level basis data.
- **Indeks Performa (5 Poin)**: Terdapat indeks komposit pada kolom-kolom penentu kueri transaksi (misalnya `(product_id, status)` atau `(reservation_token, expires_at)`).

### 2. Penanganan Konkurensi & Siklus Hidup Reservasi (Bobot: 30 Poin)
- **Status Machine Lengkap (10 Poin)**: Model mendukung transisi status yang jelas: `RESERVED`, `CONFIRMED`, `EXPIRED`, `CANCELLED`.
- **Mekanisme Kedaluwarsa Waktu (10 Poin)**: Terdapat penanda waktu kedaluwarsa (`expires_at`) yang memungkinkan pekerja latar belakang (*sweeper*) mengembalikan stok tanpa mengunci transaksi aktif.
- **Audit Ledger Mutasi (10 Poin)**: Perubahan stok dicatat dalam bentuk buku besar mutasi (*inventory log*), bukan sekadar menimpa nilai kolom *in-place*.

### 3. Kelengkapan Kamus Data dan ERD (Bobot: 15 Poin)
- **Diagram Mermaid ERD (8 Poin)**: Diagram ERD valid secara visual, memuat seluruh kardinalitas relasi secara akurat.
- **Kamus Data Komprehensif (7 Poin)**: Kamus data menjabarkan setiap tabel, tipe data, indeks, dan batasan nilai (*nullability* dan *default*).

### 4. Analisis Keputusan Arsitektur (ADR) (Bobot: 20 Poin)
- **Kontekstualisasi Masalah (5 Poin)**: Menjelaskan trade-off antara latensi baca vs konsistensi tulis pada beban 10.000 req/detik.
- **Komparasi Alternatif Solusi (10 Poin)**: Membandingkan secara mendalam antara:
  - Pessimistic Locking (`SELECT FOR UPDATE NOWAIT`)
  - Optimistic Concurrency Control (OCC dengan nomor versi)
  - In-Memory Reservation Cache dengan rekonsiliasi asinkron
- **Justifikasi Keputusan (5 Poin)**: Pilihan arsitektur didasari data performa dan mitigasi risiko kegagalan sistem.

---

## Matriks Predikat

- **Distinction (90 s.d. 100 Poin)**: Seluruh kriteria terpenuhi dengan sempurna. Memiliki skema mutasi yang rapi, proteksi tingkat tinggi terhadap race condition, dan ADR analitis berkualitas industri. Solusi dipublikasikan di Showcase Komunitas.
- **Merit (75 s.d. 89 Poin)**: DDL valid dan proteksi stok berfungsi baik. ADR memadai meski analisis alternatif kurang komprehensif.
- **Pass (60 s.d. 74 Poin)**: DDL dapat berjalan, namun penanganan race condition belum optimal atau dokumentasi belum lengkap.
- **Needs Revision (< 60 Poin)**: Terdapat galat sintaks SQL, potensi overselling di level skema, atau berkas wajib tidak ditemukan.
