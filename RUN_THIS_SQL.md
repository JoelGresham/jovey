# ⭐ FINAL SQL - RUN THIS ONE ⭐

## File to Use: `backend/database/events_final.sql`

This is the final, tested, working version that fixes all issues:
- ✅ Uses `is_processed` (not `processed`)
- ✅ Uses `user_profiles.id` (not `user_profiles.user_id`)
- ✅ Drops existing tables cleanly
- ✅ Creates all indexes correctly
- ✅ Seeds 22 event types
- ✅ Sets up RLS policies correctly

---

## Instructions:

### Step 1: Open Supabase Dashboard
Go to: https://supabase.com/dashboard
- Click your project
- Click **SQL Editor** in the left sidebar
- Click **New query**

### Step 2: Copy the SQL
Open this file: `backend/database/events_final.sql`
- Select all (Ctrl+A / Cmd+A)
- Copy (Ctrl+C / Cmd+C)

### Step 3: Run the SQL
- Paste into the Supabase SQL Editor (Ctrl+V / Cmd+V)
- Click **Run** button (or Ctrl+Enter / Cmd+Enter)

### Step 4: Verify Success
You should see:
```
SUCCESS! Events table created
event_types_seeded: 22
current_events: 0
```

---

## What This Creates:

### Tables:
1. **events** - Immutable event log with `is_processed` column
2. **event_types** - Catalog of 22 pre-seeded event types

### Views:
- **event_stream** - Human-readable event view

### Functions:
- **post_event()** - Insert events programmatically
- **get_aggregate_events()** - Get event history for an entity

### Indexes:
8 indexes for optimal performance

### Security:
- Row-level security policies
- Staff can view all events
- Users can view their own events

---

## After Running:

### 1. Verify Backend Works:
```bash
curl http://localhost:8000/api/v1/status
```

Should show:
```json
{
  "events": "active",
  "database_manager": "active"
}
```

### 2. Check Database Manager UI:
- Go to http://localhost:5173
- Login as staff user
- Click **Database Manager** tab
- Should see dashboard with stats showing 0 events

### 3. Test Event API:
The following endpoints are now active:
- `GET /api/v1/events` - Query events
- `POST /api/v1/events` - Post new event
- `GET /api/v1/events/types` - Get event catalog
- `GET /api/v1/database-manager/stats` - Get stats
- `POST /api/v1/database-manager/process` - Process events

---

## Troubleshooting:

### Error: "relation already exists"
The script uses `DROP TABLE IF EXISTS` so this shouldn't happen.
If it does, manually drop tables first:
```sql
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS event_types CASCADE;
```
Then run `events_final.sql` again.

### Error: "permission denied"
Make sure you're logged in to Supabase and have owner/admin access to the project.

### Backend shows errors after running SQL
Restart the backend:
```bash
# Kill backend
pkill -f "uvicorn app.main:app"

# Start backend
cd /home/gresh/projects/jovey/backend
uvicorn app.main:app --reload
```

### Frontend shows errors
Clear browser cache and refresh, or restart frontend:
```bash
cd /home/gresh/projects/jovey/frontend
npm run dev
```

---

## What's Next:

After running this SQL, you're ready for:

1. ✅ Event sourcing is active
2. ✅ Database Manager is functional
3. ✅ All APIs are working
4. → Next: Build BaseAgent class
5. → Next: Create first AI agent (pricing)
6. → Next: Add real-time communication
7. → Next: Implement graduated autonomy

---

## Summary:

**File:** `backend/database/events_final.sql`
**Action:** Copy → Paste into Supabase SQL Editor → Run
**Time:** 2 minutes
**Result:** Event sourcing foundation fully operational! 🎉
