# Database Schema Files

This directory contains the SQL schema files for the Jovey platform.

---

## 📋 Current/Active Files

### `schema.sql`
**Purpose:** Main database schema for the e-commerce platform

**Creates:**
- `user_profiles` - User accounts (consumer, dealer, staff)
- `categories` - Product categories
- `products` - Product catalog
- `orders` - Order records
- `order_items` - Order line items
- `order_status_history` - Order status tracking
- `dealer_product_pricing` - Custom dealer pricing

**When to use:** Initial database setup or if you need to recreate the main tables

**Status:** ✅ Active - This is the working schema for the e-commerce platform

---

### `events_final.sql` ⭐
**Purpose:** Event sourcing foundation for AI-native architecture

**Creates:**
- `events` - Immutable event log (source of truth)
- `event_types` - Catalog of event types (22 pre-seeded)
- `event_stream` - View for querying events
- Helper functions: `post_event()`, `get_aggregate_events()`
- Row-level security policies
- Indexes for performance

**When to use:** To enable event sourcing and Database Manager functionality

**Status:** ✅ Active - **USE THIS FILE** for event sourcing setup

**Instructions:** See `/QUICK_SQL_SETUP.md` or `/RUN_THIS_SQL.md` in project root

---

### `migrate_events_table.sql`
**Purpose:** Migration script for existing events table

**What it does:**
- Renames `processed` → `is_processed` if needed
- Updates indexes
- Preserves existing data
- Safe to run multiple times (idempotent)

**When to use:** Only if you already have an events table with data and need to migrate it

**Status:** ✅ Active - Use for migration only (not fresh install)

---

## 📦 Archive Directory

The `archive/` folder contains superseded versions of schema files:

- `events_schema.sql` - Original events schema (had bugs)
- `events_schema_clean.sql` - Second attempt (had RLS bug)
- `events_schema_fixed.sql` - Third attempt (still had issues)
- `run_events_schema.py` - Python script attempt (not needed)
- `schema-fixed.sql` - Old main schema version
- `schema-rls-fixed.sql` - RLS policy fixes
- `categories-products-*.sql` - Old category/product schemas
- `orders-schema.sql` - Old orders schema

**Status:** ⚠️ Archived - Don't use these, kept for reference only

---

## 🚀 Setup Order

If setting up from scratch:

1. **Run `schema.sql`** first (creates main e-commerce tables)
2. **Run `events_final.sql`** second (enables event sourcing)
3. Done! ✅

---

## 🔄 If You Need to Reset

### Reset Main Schema:
```sql
-- WARNING: Deletes all data!
DROP TABLE IF EXISTS order_status_history CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS dealer_product_pricing CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Then run schema.sql
```

### Reset Events:
```sql
-- WARNING: Deletes all events!
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS event_types CASCADE;

-- Then run events_final.sql
```

---

## 📝 Notes

- All SQL files use `CREATE TABLE IF NOT EXISTS` for safety
- RLS (Row Level Security) is enabled on all tables
- The events table is separate from main schema (can exist independently)
- Event sourcing is optional - the e-commerce platform works without it

---

## 🆘 Troubleshooting

**Error: "relation already exists"**
- Use the reset commands above and re-run the schema

**Error: "column does not exist"**
- Make sure you're using `events_final.sql` not the archived versions

**Events not working**
- Verify events table exists: `SELECT COUNT(*) FROM events;`
- Check backend status: `curl http://localhost:8000/api/v1/status`

---

**Last Updated:** 2025-10-26
**Current Version:** Events Final (working)
