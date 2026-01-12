# Data Standards (The "What")
Applies to: All Databases & Data Stores

## Purpose

Define the universal standards for data modeling, storage, and integrity.

## 1. Naming Conventions

- **Tables**: Plural, snake_case (e.g., `users`, `order_items`).
- **Columns**: snake_case (e.g., `first_name`, `created_at`).
- **Booleans**: Prefix with `is_` or `has_` (e.g., `is_active`, `has_permission`).
- **Foreign Keys**: `singular_table_name_id` (e.g., `user_id`).

## 2. Primary Keys & Identity

- **Type**: UUID (v7 preferred for sortability) or BigInt.
- **Constraint**: Every table MUST have a Primary Key.
- **Naming**: Always named `id`.

## 3. Audit Columns

Every mutable table must include:

- `created_at` (Timestamp with Timezone, default NOW)
- `updated_at` (Timestamp with Timezone, auto-updating)
- `deleted_at` (Nullable, for Soft Deletes if applicable)

## 4. Integrity & Constraints

- **Foreign Keys**: Must be enforced at the database level.
- **Not Null**: Default to `NOT NULL` unless optionality is explicitly required.
- **Defaults**: Define defaults in DB schema, not just application code.

## 5. Migrations

- **Version Control**: All schema changes must be versioned migrations.
- **Reversible**: Migrations should ideally be reversible (Up/Down).
- **No Data Loss**: Migrations must never result in accidental data loss.

## 6. Security

- **Encryption**: Sensitive columns (PII) must be encrypted at rest.
- **Least Privilege**: App users should not be `superusers`.
