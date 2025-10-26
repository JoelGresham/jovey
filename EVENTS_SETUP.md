# Event Sourcing Setup Guide

**Date:** 2025-10-26
**Status:** ✅ Event Sourcing Foundation Complete

---

## Overview

This guide covers the event sourcing infrastructure that has been implemented in the Jovey platform. Event sourcing is the foundation of the AI-native architecture, where all state changes are recorded as immutable events.

---

## What is Event Sourcing?

**Traditional Architecture:**
```
User Action → Direct Database Update → State Changed
```

**Event Sourcing Architecture:**
```
User/Agent Action → Post Event → Event Stored (immutable)
                                    ↓
                            Database Manager Processes Event
                                    ↓
                            State Tables Updated
```

### Key Benefits

1. **Complete Audit Trail** - Every change is recorded with who, what, when, why
2. **Time Travel** - Replay events to see state at any point in time
3. **Event Replay** - Rebuild state from scratch by replaying events
4. **Agent Coordination** - AI agents communicate through events
5. **Debugging** - See exact sequence of events that led to current state

---

## Architecture Components

### 1. Events Table (Immutable Log)

The `events` table is the source of truth for all state changes:

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    event_number BIGSERIAL UNIQUE,      -- Sequential ordering
    event_type VARCHAR(100),             -- e.g., 'product.created'
    aggregate_type VARCHAR(50),          -- e.g., 'product'
    aggregate_id UUID,                   -- Which entity
    data JSONB,                          -- Event payload
    metadata JSONB,                      -- Context
    created_by VARCHAR(100),             -- Who made the change
    user_id UUID,                        -- User if applicable
    created_at TIMESTAMPTZ,              -- When
    processed BOOLEAN,                   -- Has DB Manager processed?
    correlation_id UUID,                 -- Group related events
    causation_id UUID,                   -- What caused this event
    idempotency_key VARCHAR(255)         -- Prevent duplicates
);
```

### 2. Event Types Catalog

Pre-defined event types with schemas and examples:

- **Product Events:** `product.created`, `product.updated`, `product.price_changed`, `product.stock_updated`
- **Order Events:** `order.created`, `order.payment_received`, `order.status_changed`, `order.fulfilled`
- **Customer Events:** `customer.registered`, `customer.profile_updated`
- **Dealer Events:** `dealer.application_submitted`, `dealer.approved`, `dealer.pricing_updated`
- **Agent Events:** `agent.decision_proposed`, `agent.decision_approved`, `agent.decision_rejected`

### 3. Event API Endpoints

All available at `/api/v1/events/`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/events` | POST | Post a new event |
| `/api/v1/events` | GET | Query event stream with filters |
| `/api/v1/events/types` | GET | Get event type catalog |
| `/api/v1/events/stats` | GET | Get event statistics |
| `/api/v1/events/unprocessed` | GET | Get unprocessed events (for DB Manager) |
| `/api/v1/events/{id}` | GET | Get specific event |
| `/api/v1/events/{id}/processing` | PUT | Update processing status |
| `/api/v1/events/aggregate/{type}/{id}/history` | GET | Get event history for entity |

---

## Setup Instructions

### Step 1: Run Events Schema in Supabase

The events schema SQL is ready at: `backend/database/events_schema.sql`

**Manual Setup (Required):**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy the entire contents of `backend/database/events_schema.sql`
6. Paste into the SQL Editor
7. Click **Run**

**What This Creates:**
- `events` table (main event log)
- `event_types` table (catalog with 20+ seeded event types)
- Helper functions (`post_event`, `get_aggregate_events`)
- Views (`event_stream`)
- RLS policies (staff can view all, users can view their own)
- Indexes for performance

### Step 2: Verify Backend is Running

The events API endpoints are already integrated into the backend:

```bash
# Backend should show events as active
curl http://localhost:8000/api/v1/status

# Response should include:
{
  "features": {
    "auth": "active",
    "database": "active",
    "events": "active",     ← This should be present
    "agents": "pending"
  }
}
```

### Step 3: Test Event Posting

Once the events table is created in Supabase, you can test posting events:

```bash
# Get authentication token first
TOKEN="your_jwt_token_here"

# Post a test event
curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "product.created",
    "aggregate_type": "product",
    "aggregate_id": "123e4567-e89b-12d3-a456-426614174000",
    "data": {
      "sku": "SUBM-05HP-DOM-SS-50LPM-20M",
      "name": "0.5HP Submersible Pump",
      "base_price": 5999.00
    },
    "created_by": "user:test"
  }'
```

---

## Event Format

### Event Type Naming Convention

Format: `aggregate.action`

Examples:
- `product.created` - New product added
- `order.placed` - Customer placed order
- `price.changed` - Price was updated
- `agent.decision_proposed` - AI agent made recommendation

### Event Data Structure

```json
{
  "event_type": "product.created",
  "aggregate_type": "product",
  "aggregate_id": "uuid-here",
  "data": {
    // Actual event data - what changed
    "sku": "SUBM-05HP-DOM-SS-50LPM-20M",
    "name": "0.5HP Submersible Pump",
    "base_price": 5999.00
  },
  "metadata": {
    // Optional context
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "source": "web_ui"
  },
  "created_by": "user:uuid" | "agent:category_agent" | "system",
  "correlation_id": "uuid",  // Optional - groups related events
  "causation_id": "uuid",    // Optional - what caused this event
  "idempotency_key": "unique-key"  // Optional - prevent duplicates
}
```

### Created By Format

- `user:{uuid}` - Human user action
- `agent:{agent_name}` - AI agent action
- `system` - System-initiated action

---

## Usage Examples

### 1. Posting Events from Code

```python
from app.functions.events.services import EventService
from app.functions.events.models import EventCreate
from uuid import UUID

# Create event
event_data = EventCreate(
    event_type="product.created",
    aggregate_type="product",
    aggregate_id=product_id,
    data={
        "sku": "SUBM-05HP-DOM-SS-50LPM-20M",
        "name": "0.5HP Submersible Pump",
        "base_price": 5999.00
    },
    created_by=f"user:{user_id}"
)

# Post event
event = await EventService.post_event(event_data, user_id)
```

### 2. Querying Events

```python
from app.functions.events.models import EventStreamQuery

# Get all unprocessed events
query = EventStreamQuery(processed=False, limit=100)
events = await EventService.get_events(query)

# Get events for a specific product
query = EventStreamQuery(
    aggregate_type="product",
    aggregate_id=product_id,
    limit=50
)
events = await EventService.get_events(query)
```

### 3. Getting Entity History

```python
# Get complete history for a product
history = await EventService.get_aggregate_history(
    aggregate_type="product",
    aggregate_id=product_id
)

# History is in chronological order (oldest first)
for event in history:
    print(f"{event.created_at}: {event.event_type} - {event.data}")
```

---

## Next Steps

### 1. Build Database Manager (Next Task)

The Database Manager is a critical component that:
- Monitors the event stream for unprocessed events
- Translates events into state table operations
- Executes state table updates
- Marks events as processed
- Handles processing errors

**Location:** Will be built at `/app/functions/database_manager/`

**UI:** Staff portal will have a "Database Manager" tab showing:
- Event stream viewer
- Processing status
- Event-to-transaction mapping
- Manual event processing controls

### 2. Create AI Agents

Once Database Manager is built, AI agents can:
- Post events instead of direct database writes
- React to events from other agents
- Propose decisions that require human approval
- Gradually gain autonomy as confidence builds

**First Agent:** Category Management Agent (pricing analysis)

### 3. Add Real-time Communication

Use Supabase Real-time to:
- Subscribe to event stream changes
- Notify agents when relevant events occur
- Update UI in real-time when events are processed
- Enable agent-to-agent communication

---

## Event Sourcing Best Practices

### 1. Events are Immutable

**Never** update or delete events. If you need to correct something:
- Post a new compensating event
- Example: `product.price_corrected` event to fix wrong price

### 2. Events Record Facts, Not Intentions

**Good:** `order.placed` (fact - order was placed)
**Bad:** `order.will_be_shipped` (intention - not yet happened)

### 3. Event Data Should Be Self-Contained

Include all information needed to process the event:

**Good:**
```json
{
  "event_type": "price.changed",
  "data": {
    "old_price": 5999.00,
    "new_price": 5499.00,
    "reason": "competitor_match",
    "effective_date": "2025-10-27"
  }
}
```

**Bad:**
```json
{
  "event_type": "price.changed",
  "data": {
    "new_price": 5499.00
    // Missing old_price, reason, etc.
  }
}
```

### 4. Use Correlation IDs for Related Events

Group related events together:

```json
{
  "event_type": "order.created",
  "correlation_id": "order-flow-123",
  ...
}

{
  "event_type": "payment.received",
  "correlation_id": "order-flow-123",  // Same ID
  "causation_id": "event-id-of-order-created",
  ...
}
```

---

## Troubleshooting

### Events Not Being Created

1. Check events table exists in Supabase:
   ```sql
   SELECT COUNT(*) FROM events;
   ```

2. Check RLS policies allow inserts

3. Verify authentication token is valid

### Events Not Being Processed

1. Check Database Manager is running
2. Look for processing errors:
   ```sql
   SELECT * FROM events
   WHERE processed = false
   AND processing_error IS NOT NULL;
   ```

3. Check Database Manager logs

### Performance Issues

1. Verify indexes exist:
   ```sql
   SELECT indexname FROM pg_indexes
   WHERE tablename = 'events';
   ```

2. Consider archiving old events

3. Use pagination when querying large event streams

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/database/events_schema.sql` | Complete events table schema |
| `backend/app/functions/events/models.py` | Pydantic models for events |
| `backend/app/functions/events/services.py` | Event business logic |
| `backend/app/functions/events/routes.py` | Event API endpoints |
| `backend/app/functions/events/__init__.py` | Module initialization |
| `EVENTS_SETUP.md` | This guide |

---

## API Documentation

Full API documentation with interactive testing available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Look for the "Events" tag in the API documentation.

---

## Status

- ✅ Events table schema designed and ready
- ✅ Event API endpoints implemented
- ✅ Event types catalog seeded
- ✅ Backend integration complete
- ⏳ Events table needs to be created in Supabase (manual step)
- ⏳ Database Manager function (next task)
- ⏳ AI agents (future task)
- ⏳ Real-time subscriptions (future task)

---

## Questions?

The event sourcing system is designed to be the foundation for the AI-native architecture. All future AI agents will post events rather than directly modifying the database, ensuring a complete audit trail and enabling sophisticated agent coordination.

**Next:** Build the Database Manager function to process events and update state tables!
