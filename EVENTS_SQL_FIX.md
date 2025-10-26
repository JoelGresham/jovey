# Events Schema SQL Fix

**Issue:** The original `events_schema.sql` had a column naming inconsistency that caused an error when running in Supabase.

**Error:** `ERROR: 42703: column "processed" does not exist`

## What Was Fixed

Changed the column name from `processed` to `is_processed` throughout the entire codebase for consistency with PostgreSQL naming conventions.

### Files Updated:

**Backend:**
- ✅ `backend/database/events_schema_fixed.sql` - New fixed SQL file
- ✅ `backend/app/functions/events/models.py` - Updated to use `is_processed`
- ✅ `backend/app/functions/events/services.py` - Updated to use `is_processed`
- ✅ `backend/app/functions/database_manager/event_processor.py` - Updated to use `is_processed`
- ✅ `backend/app/functions/database_manager/services.py` - Updated to use `is_processed`

**Frontend:**
- ✅ `frontend/src/pages/staff/DatabaseManager.jsx` - Updated to use `is_processed`

## How to Run the Fixed SQL

### Option 1: Fresh Install (Recommended - No Data Loss Since Table is Empty)

**Use:** `backend/database/events_schema_clean.sql`

This drops and recreates the tables cleanly.

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy the entire contents of `backend/database/events_schema_clean.sql`
6. Paste into the SQL Editor
7. Click **Run**

✅ This is the cleanest approach and will work every time.

### Option 2: Migration Script (If You Have Important Data to Preserve)

**Use:** `backend/database/migrate_events_table.sql`

This intelligently renames the column if needed without data loss.

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy the entire contents of `backend/database/migrate_events_table.sql`
6. Paste into the SQL Editor
7. Click **Run**

This script:
- ✅ Checks if the table exists
- ✅ Renames `processed` → `is_processed` if needed
- ✅ Updates indexes
- ✅ Preserves all existing data
- ✅ Safe to run multiple times (idempotent)

## Verification

After running the SQL, verify it worked:

```sql
-- Should return the table structure
\d events

-- Should show 20+ event types
SELECT COUNT(*) FROM event_types;

-- Should return 0 (no events yet)
SELECT COUNT(*) FROM events;
```

## Testing the System

Once the SQL is run, test the events API:

1. **Backend should be running:**
   ```bash
   curl http://localhost:8000/api/v1/status
   # Should show: "events": "active", "database_manager": "active"
   ```

2. **Check event types catalog:**
   ```bash
   # Login to get token first, then:
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/events/types
   ```

3. **Check Database Manager stats:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/database-manager/stats
   ```

4. **Access the UI:**
   - Go to http://localhost:5173
   - Login as staff user
   - Navigate to **Database Manager** tab
   - Should see the dashboard with 0 events processed

## What Changed

### Column Naming:
- **Old:** `processed` BOOLEAN
- **New:** `is_processed` BOOLEAN

This is more explicit and follows PostgreSQL/Python naming conventions for boolean fields.

### API Changes:
All API query parameters updated:
- **Old:** `?processed=false`
- **New:** `?is_processed=false`

### Model Changes:
```python
# Old
class EventResponse(BaseModel):
    processed: bool

# New
class EventResponse(BaseModel):
    is_processed: bool
```

## Status

- ✅ All backend code updated
- ✅ All frontend code updated
- ✅ Backend running without errors
- ⏳ SQL needs to be run in Supabase (manual step)

## Next Steps

After running the fixed SQL:

1. ✅ Events table will be created
2. ✅ Event types will be seeded
3. ✅ You can start posting events
4. ✅ Database Manager can process events
5. → Ready to build AI agents!

---

**Note:** The old `events_schema.sql` file is still in the repo for reference, but you should use `events_schema_fixed.sql` instead.
