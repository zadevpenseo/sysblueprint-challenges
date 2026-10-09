# Kamus Data Teknis: Flash Sale Concurrency Engine

Dokumen ini memuat spesifikasi terperinci struktur tabel, tipe data, indeks, dan batasan integritas skema basis data penanganan promosi kilat.

---

## 1. Tabel `products`
Menyimpan informasi identitas katalog komoditas.

| Kolom | Tipe Data | Nullable | Nilai Awal | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Kunci primer identitas produk (UUIDv4) |
| `sku` | VARCHAR(64) | TIDAK | - | Kode unik stock keeping unit |
| `title` | VARCHAR(255) | TIDAK | - | Nama komersial produk |
| `base_price` | DECIMAL(14, 2) | TIDAK | - | Nilai nominal harga jual dasar |
| `created_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Cap waktu pendaftaran produk |

---

## 2. Tabel `inventory_pools`
Menjaga kedaulatan kuota fisik dan alokasi stok produk.

| Kolom | Tipe Data | Nullable | Nilai Awal | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Kunci primer entitas inventaris |
| `product_id` | VARCHAR(36) | TIDAK | - | Kunci asing unik merujuk ke tabel products |
| `total_physical_qty` | INT | TIDAK | - | Batas atas stok fisik di gudang |
| `allocated_qty` | INT | TIDAK | 0 | Jumlah unit yang telah lunas terbayar |
| `reserved_qty` | INT | TIDAK | 0 | Jumlah unit yang sedang ditahan masa reservasi |
| `version_id` | INT | TIDAK | 1 | Kolom versi pendukung Optimistic Concurrency Control |
| `updated_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Cap waktu pembaruan saldo stok |

---

## 3. Tabel `stock_reservations`
Menampung penahanan kuota sementara saat pengguna memasuki tahap pembayaran.

| Kolom | Tipe Data | Nullable | Nilai Awal | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Kunci primer sesi reservasi |
| `reservation_token` | VARCHAR(64) | TIDAK | - | Token idempotensi transaksi |
| `user_id` | VARCHAR(36) | TIDAK | - | Pengenal pembeli yang melakukan klaim |
| `product_id` | VARCHAR(36) | TIDAK | - | Kunci asing produk yang dipesan |
| `quantity` | INT | TIDAK | - | Jumlah unit barang yang direservasi |
| `status` | VARCHAR(20) | TIDAK | 'ACTIVE' | Status reservasi (ACTIVE, CONFIRMED, EXPIRED, RELEASED) |
| `expires_at` | TIMESTAMPTZ | TIDAK | - | Waktu kedaluwarsa reservasi (15 menit) |
| `created_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu pencatatan sesi |
| `updated_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu perubahan status sesi |

---

## 4. Tabel `sales_orders`
Mencatat tagihan resmi dan status pembayaran pesanan pembeli.

| Kolom | Tipe Data | Nullable | Nilai Awal | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Kunci primer pesanan penjualan |
| `order_number` | VARCHAR(64) | TIDAK | - | Nomor faktur pesanan pembeli |
| `user_id` | VARCHAR(36) | TIDAK | - | Pengenal pembeli |
| `reservation_id` | VARCHAR(36) | TIDAK | - | Kunci asing unik merujuk ke stock_reservations |
| `total_amount` | DECIMAL(14, 2) | TIDAK | - | Akumulasi nominal kewajiban bayar |
| `payment_status` | VARCHAR(20) | TIDAK | 'PENDING' | Status pembayaran (PENDING, PAID, CANCELLED, REFUNDED) |
| `placed_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu pesanan diterbitkan |
| `paid_at` | TIMESTAMPTZ | YA | NULL | Waktu penyelesaian pelunasan |

---

## 5. Tabel `inventory_mutation_logs`
Buku besar mutasi stok nir-ubah (*append-only audit log*).

| Kolom | Tipe Data | Nullable | Nilai Awal | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Kunci primer rekaman mutasi |
| `inventory_pool_id` | VARCHAR(36) | TIDAK | - | Kunci asing merujuk ke inventory_pools |
| `reference_id` | VARCHAR(36) | TIDAK | - | Pengenal reservasi atau pesanan terkait |
| `mutation_type` | VARCHAR(32) | TIDAK | - | Jenis pergerakan stok |
| `delta_allocated` | INT | TIDAK | 0 | Perubahan saldo kuota terbayar |
| `delta_reserved` | INT | TIDAK | 0 | Perubahan saldo kuota terpesan sementara |
| `notes` | TEXT | YA | NULL | Catatan verifikasi sistem |
| `recorded_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu pencatatan mutasi fisik |
