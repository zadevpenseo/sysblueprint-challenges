# Tantangan 01: Penanganan Concurrency dan Stok Flash Sale

## Konteks Bisnis
Sebuah platform e-commerce menyelenggarakan promosi kilat (*flash sale*) untuk produk elektronik edisi terbatas. Sebanyak 500 unit produk akan diperebutkan oleh lebih dari 100.000 pengguna aktif secara serentak dalam rentang waktu 3 menit pertama. 

Permasalahan umum pada sistem terdahulu adalah terjadinya *overselling* (jumlah pesanan yang berhasil dibayar melebihi kuota fisik stok yang tersedia) dan *deadlock* basis data saat ribuan transaksi konkuren berusaha mengunci baris stok produk yang sama.

---

## Sasaran Teknis
Rancang skema basis data relasional dan strategi konkurensi yang menjamin:
1. **Zero Overselling**: Kuota stok fisik tidak pernah bernilai negatif dalam kondisi beban puncak.
2. **Reservasi Waktu Terbatas**: Pengguna yang berhasil masuk tahap *checkout* diberikan tenggat waktu pembayaran (misalnya 15 menit). Apabila pembayaran tidak diselesaikan, stok otomatis dilepaskan kembali ke *pool* publik.
3. **Audit Trail Lengkap**: Setiap mutasi reservasi, konfirmasi pembayaran, dan pembatalan tercatat secara kronologis untuk kebutuhan rekonsiliasi finansial.
4. **Idempotensi Pesanan**: Pencegahan duplikasi pesanan ketika pengguna menekan tombol *checkout* berulang kali karena jaringan lambat.

---

## Batasan dan Asumsi Sistem
- **Basis Data Target**: PostgreSQL 15+ (atau SQLite STRICT / MySQL 8.0+ dengan InnoDB).
- **Traffic Puncak**: 10.000 request/detik pada titik sentuh *cart reservation*.
- **Waktu Kedaluwarsa Reservasi**: 900 detik (15 menit).
- **Ketersediaan**: Skema harus mendukung pengurutan topologis bebas siklik (*Acyclic DAG*).

---

## Berkas yang Wajib Diserahkan
Kirimkan solusi Anda ke dalam folder `submissions/<nama-anda>-flashsale/` dengan berkas berikut:
1. `schema.sql`: Skema DDL lengkap mencakup tabel, relasi foreign key, tipe data, indeks performa, dan check constraints.
2. `ERD.md`: Diagram relasi entitas dalam format Mermaid.
3. `DATA_DICTIONARY.md`: Dokumentasi kamus data untuk setiap kolom, tipe data, status nullability, dan deskripsi fungsinya.
4. `ADR-001.md`: Dokumen Architecture Decision Record yang memaparkan analisis komparatif antara *Pessimistic Locking* (`SELECT FOR UPDATE`), *Optimistic Concurrency Control* (version column), dan *Token/Voucher-based Reservation*.
