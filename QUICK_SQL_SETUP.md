# Quick SQL Setup Guide

## TL;DR - Just Run This:

1. **Go to:** [Supabase Dashboard](https://supabase.com/dashboard) → Your Project → SQL Editor
2. **Copy:** `backend/database/events_final.sql` ⭐
3. **Paste** into SQL Editor
4. **Click:** Run
5. **Done!** ✅

---

## What This Does:

Creates:
- ✅ `events` table (immutable event log)
- ✅ `event_types` table (with 22 pre-seeded event types)
- ✅ Indexes for performance
- ✅ Helper functions (`post_event`, `get_aggregate_events`)
- ✅ Row-level security policies
- ✅ View (`event_stream`)

---

## Expected Result:

```
SUCCESS! Events table created
event_types_seeded: 22
current_events: 0
```

---

## Files Available:

| File | When to Use |
|------|-------------|
| `events_final.sql` | ✅ **USE THIS** - Final working version |
| `migrate_events_table.sql` | Use if you have data to preserve |
| `events_schema_clean.sql` | Old version - don't use |
| `events_schema_fixed.sql` | Old version - don't use |
| `events_schema.sql` | Original - don't use |

---

## After Running SQL:

### 1. Verify Backend:
```bash
curl http://localhost:8000/api/v1/status
# Should show: "events": "active", "database_manager": "active"
```

### 2. Test in UI:
- Go to http://localhost:5173
- Login as staff
- Click **Database Manager** tab
- Should see dashboard with "0 events processed"

### 3. You're Ready!
Event sourcing foundation is now active and ready for AI agents! 🎉

---

## Troubleshooting:

**Problem:** "Table already exists" error
**Solution:** The script handles this with `DROP TABLE IF EXISTS`

**Problem:** "Permission denied"
**Solution:** Make sure you're in the SQL Editor, not the Table Editor

**Problem:** Backend still shows errors
**Solution:** Restart backend: `pkill -f uvicorn && cd backend && uvicorn app.main:app --reload`

---

## Next Steps:

1. ✅ Run SQL (you're doing this now)
2. ✅ Backend and Database Manager are already built
3. → Build BaseAgent class (next task)
4. → Create first AI agent (pricing agent)
5. → Add real-time communication
6. → Implement graduated autonomy

**Current Progress:** 60% complete on AI-native architecture! 🚀
