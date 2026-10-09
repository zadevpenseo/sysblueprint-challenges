# ADR 001: Pengendalian Konkurensi dan Proteksi Stok pada Promosi Kilat

- **Status**: DITERIMA
- **Pengusul**: Tim Rekayasa Arsitektur SysBlueprint
- **Tanggal**: 2026-10-09
- **Domain**: Transaksi Basis Data, Concurrency, E-Commerce

---

## 1. Konteks Masalah
Dalam skenario promosi kilat (*flash sale*), sebanyak 500 unit produk diperebutkan oleh 100.000 pengguna secara serempak. Beban lonjakan ini memicu permasalahan teknis fundamental:
- **Peluang Overselling**: Dua transaksi membaca saldo stok `5` secara bersamaan, lalu keduanya mengurangi stok menjadi `4`, padahal seharusnya berkurang menjadi `3`.
- **Ancaman Deadlock**: Peningkatan frekuensi kueri pembaruan data pada satu baris tabel memicu antrean kunci (*lock contention*) yang berisiko menumbangkan klaster basis data utama.
- **Lonjakan Pembatalan**: Pengguna yang menaruh barang di keranjang namun tidak membayar menyandera inventaris, sehingga kuota riil tidak terserap maksimal.

---

## 2. Pilihan Pendekatan yang Dipertimbangkan

### Opsi A: Pessimistic Locking Murni (`SELECT FOR UPDATE`)
- **Mekanisme**: Mengunci baris `inventory_pools` secara eksklusif sejak transaksi dimulai hingga *commit*.
- **Kelebihan**: Sangat aman secara matematis; konsistensi data terjamin mutlak.
- **Kekurangan**: Menahan koneksi basis data terlalu lama. Pada 10.000 req/detik, kolam koneksi (*connection pool*) cepat habis dan memicu galat *timeout*.

### Opsi B: Optimistic Concurrency Control (OCC dengan Versi)
- **Mekanisme**: Membaca data tanpa kunci, lalu mengeksekusi `UPDATE inventory_pools SET reserved_qty = reserved_qty + 1, version_id = version_id + 1 WHERE id = ? AND version_id = ?`.
- **Kelebihan**: Kueri baca berlangsung tanpa latensi antrean.
- **Kekurangan**: Pada perebutan 500 unit oleh ribuan penawar, tingkat kegagalan (*retry rate*) mendekati 99%, sehingga memboroskan siklus komputasi CPU aplikasi.

### Opsi C: Pola Hibrida Dua Fase (Reservasi Terbatas + Sweep Worker)
- **Mekanisme**: Pembaruan atomik langsung dengan klausul proteksi:
  `UPDATE inventory_pools SET reserved_qty = reserved_qty + ? WHERE id = ? AND (allocated_qty + reserved_qty + ?) <= total_physical_qty;`
  Jika baris terpengaruh bernilai 1, terbitkan token reservasi berbatas waktu 15 menit. Pekerja latar belakang secara periodik membatalkan token kedaluwarsa dan mengembalikan kuota reservasi.
- **Kelebihan**: Waktu penguncian baris berada pada skala milidetik (sub-millisecond), menghindari perlunya penguncian baca, dan memiliki pemulihan otomatis stok terbengkalai.
- **Kekurangan**: Membutuhkan komponen *background worker* untuk menyapu (*sweep*) sesi yang kedaluwarsa.

---

## 3. Keputusan Arsitektur
Kami memutuskan untuk mengadopsi **Opsi C (Pola Hibrida Dua Fase)** yang dipadukan dengan buku besar mutasi nir-ubah (*immutable inventory mutation logs*).

Keputusan ini didasari oleh tiga pertimbangan utama:
1. **Pencegahan Overselling di Level Engine**: Skema dilengkapi *check constraints* `chk_reserved_bounds` yang menjamin basis data menolak transaksi jika akumulasi kuota melebihi kapasitas fisik.
2. **Kemandirian Transaksi**: Transaksi checkout tidak saling menunggu sesi pembayaran pengguna lain, sehingga memangkas latensi tail P99.
3. **Audit Transparansi Finansial**: Setiap mutasi tercatat kronologis, memudahkan pelacakan jika terjadi selisih rekonsiliasi pembayaran.

---

## 4. Konsekuensi dan Mitigasi

- **Konsekuensi Positif**:
  - Nol kemungkinan kuota stok fisik bernilai negatif (*zero overselling guarantee*).
  - Skalabilitas tinggi karena tidak memblokir operasi pembacaan katalog.
  - Alur serah terima stok otomatis kembali terbuka saat pembayaran kedaluwarsa.
- **Trade-off dan Risiko**:
  - Kompleksitas logika aplikasi bertambah karena harus mengelola transisi status reservasi.
  - Beban penulisan ganda ke tabel log mutasi.
- **Mitigasi Teknis**:
  - Indeks komposit `(status, expires_at)` disiapkan pada tabel reservasi agar proses penyisiran pekerja latar belakang berjalan dalam hitungan milidetik.
  - Penulisan log mutasi dilakukan dalam transaksi yang sama menggunakan *batching* saat konfirmasi pembayaran.
