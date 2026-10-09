-- SysBlueprint Architecture Challenge 01: Solution Reference
-- Target: PostgreSQL 15+ / SQLite STRICT / MySQL 8.0+
-- Karakteristik: Zero Overselling, Two-Phase Reservation, Audit Ledger Mutasi

-- 1. Tabel Produk Flash Sale
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    sku VARCHAR(64) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    base_price DECIMAL(14, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. Tabel Inventaris Terisolasi dengan Constraint Proteksi Stok Fisik
CREATE TABLE inventory_pools (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL UNIQUE,
    total_physical_qty INT NOT NULL,
    allocated_qty INT DEFAULT 0 NOT NULL,
    reserved_qty INT DEFAULT 0 NOT NULL,
    version_id INT DEFAULT 1 NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_physical_positive CHECK (total_physical_qty >= 0),
    CONSTRAINT chk_allocated_bounds CHECK (allocated_qty >= 0 AND allocated_qty <= total_physical_qty),
    CONSTRAINT chk_reserved_bounds CHECK (reserved_qty >= 0 AND (allocated_qty + reserved_qty) <= total_physical_qty),
    CONSTRAINT fk_inv_pool_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 3. Tabel Reservasi Waktu Terbatas (Masa Aktif 15 Menit)
CREATE TABLE stock_reservations (
    id VARCHAR(36) PRIMARY KEY,
    reservation_token VARCHAR(64) NOT NULL UNIQUE,
    user_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    quantity INT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE' NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_reservation_qty CHECK (quantity > 0),
    CONSTRAINT chk_reservation_status CHECK (status IN ('ACTIVE', 'CONFIRMED', 'EXPIRED', 'RELEASED')),
    CONSTRAINT fk_reservation_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- 4. Tabel Pesanan Finansial
CREATE TABLE sales_orders (
    id VARCHAR(36) PRIMARY KEY,
    order_number VARCHAR(64) NOT NULL UNIQUE,
    user_id VARCHAR(36) NOT NULL,
    reservation_id VARCHAR(36) NOT NULL UNIQUE,
    total_amount DECIMAL(14, 2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'PENDING' NOT NULL,
    placed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_order_status CHECK (payment_status IN ('PENDING', 'PAID', 'CANCELLED', 'REFUNDED')),
    CONSTRAINT fk_order_reservation FOREIGN KEY (reservation_id) REFERENCES stock_reservations(id) ON DELETE RESTRICT
);

-- 5. Tabel Buku Besar Mutasi Stok (Immutable Audit Ledger)
CREATE TABLE inventory_mutation_logs (
    id VARCHAR(36) PRIMARY KEY,
    inventory_pool_id VARCHAR(36) NOT NULL,
    reference_id VARCHAR(36) NOT NULL,
    mutation_type VARCHAR(32) NOT NULL,
    delta_allocated INT DEFAULT 0 NOT NULL,
    delta_reserved INT DEFAULT 0 NOT NULL,
    notes TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_mutation_type CHECK (mutation_type IN ('RESERVE_HOLD', 'RESERVE_RELEASE', 'PAYMENT_ALLOCATE', 'MANUAL_ADJUST')),
    CONSTRAINT fk_mutation_pool FOREIGN KEY (inventory_pool_id) REFERENCES inventory_pools(id) ON DELETE RESTRICT
);

-- Indeks Kueri Performa Transaksi
CREATE INDEX idx_reservations_lookup ON stock_reservations (user_id, status);
CREATE INDEX idx_reservations_expiry ON stock_reservations (status, expires_at);
CREATE INDEX idx_orders_user ON sales_orders (user_id, payment_status);
CREATE INDEX idx_mutation_pool ON inventory_mutation_logs (inventory_pool_id, recorded_at);
