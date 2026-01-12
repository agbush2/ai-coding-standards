# PostgreSQL Standards (The "How")
Implementation of: /data_standards.md

## Relationship to Standards

This file provides the PostgreSQL-specific implementation ("How") for the data standards defined in `/data_standards.md` ("What").

## 1. Types & Extensions

- **UUID**: Use `uuid-ossp` or `pgcrypto` extension.
- **JSON**: Use `JSONB` (binary) over `JSON` for indexing support.
- **Text**: Use `TEXT` instead of `VARCHAR(n)` unless length constraint is business-critical.
- **Money**: Use `NUMERIC` or `DECIMAL`, never `FLOAT` or `MONEY` type.

## 2. Indexing Strategy

- **Foreign Keys**: Must be indexed explicitly (Postgres does not do this automatically).
- **Uniqueness**: Use `UNIQUE INDEX` constraints.
- **Partial Indexes**: Use `WHERE deleted_at IS NULL` for soft-delete tables.
- **GIN Indexes**: Mandatory for querying `JSONB` columns.

## 3. Naming & Conventions

- **Limit**: 63 characters max length.
- **Reserved Words**: Avoid Postgres reserved words (e.g., `user`, `order`, `group`). Quote if unavoidable, but prefer renaming (e.g., `app_users`).

## 4. Performance Patterns

- **Pagination**: Use Keyset Pagination (Seek Method) over `OFFSET/LIMIT` for large datasets.
- **Connections**: Use a connection pooler (PgBouncer) in production.

## 5. Example: Table Definition

```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_cents INTEGER NOT NULL, -- Store currency in smallest unit
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index FKs
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
-- Index JSONB
CREATE INDEX idx_order_items_metadata ON order_items USING GIN (metadata);
```
