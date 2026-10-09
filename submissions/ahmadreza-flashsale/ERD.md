# Entity Relationship Diagram (Solusi Referensi)

Diagram di bawah ini menggambarkan alur relasi topologis dari entitas produk hingga buku besar mutasi stok pada arsitektur flash sale SysBlueprint.

```mermaid
erDiagram
    PRODUCTS ||--|| INVENTORY_POOLS : controls
    PRODUCTS ||--o{ STOCK_RESERVATIONS : yields
    STOCK_RESERVATIONS ||--o| SALES_ORDERS : satisfies
    INVENTORY_POOLS ||--o{ INVENTORY_MUTATION_LOGS : records

    PRODUCTS {
        string id PK
        string sku UK
        string title
        decimal base_price
        timestamptz created_at
    }

    INVENTORY_POOLS {
        string id PK
        string product_id FK,UK
        int total_physical_qty
        int allocated_qty
        int reserved_qty
        int version_id
        timestamptz updated_at
    }

    STOCK_RESERVATIONS {
        string id PK
        string reservation_token UK
        string user_id
        string product_id FK
        int quantity
        string status
        timestamptz expires_at
        timestamptz created_at
        timestamptz updated_at
    }

    SALES_ORDERS {
        string id PK
        string order_number UK
        string user_id
        string reservation_id FK,UK
        decimal total_amount
        string payment_status
        timestamptz placed_at
        timestamptz paid_at
    }

    INVENTORY_MUTATION_LOGS {
        string id PK
        string inventory_pool_id FK
        string reference_id
        string mutation_type
        int delta_allocated
        int delta_reserved
        text notes
        timestamptz recorded_at
    }
```
