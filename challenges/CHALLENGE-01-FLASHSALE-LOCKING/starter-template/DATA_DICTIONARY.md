# Kamus Data (Starter Template)

Dokumentasikan setiap entitas tabel, kolom, batasan nilai, dan kegunaannya pada bagian di bawah ini.

## 1. Tabel `products`

| Nama Kolom | Tipe Data | Nullable | Nilai Default | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Primary Key pengenal produk |
| `name` | VARCHAR(255) | TIDAK | - | Nama dagang produk |
| `price` | DECIMAL(14, 2) | TIDAK | - | Harga satuan resmi |
| `total_stock` | INT | TIDAK | - | Total kuota awal |
| `created_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu pencatatan produk |

## 2. Tabel `orders`

| Nama Kolom | Tipe Data | Nullable | Nilai Default | Keterangan |
|:---|:---|:---:|:---:|:---|
| `id` | VARCHAR(36) | TIDAK | - | Primary Key pesanan |
| `product_id` | VARCHAR(36) | TIDAK | - | Foreign Key ke tabel products |
| `user_id` | VARCHAR(36) | TIDAK | - | Pengenal pembeli |
| `status` | VARCHAR(32) | TIDAK | - | Status transaksi |
| `created_at` | TIMESTAMPTZ | TIDAK | CURRENT_TIMESTAMP | Waktu pesanan dibuat |
