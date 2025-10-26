# Jovey Technical Architecture
## Detailed System Design

**Version:** 1.0
**Date:** 2025-10-25
**Status:** Initial Design

---

## Executive Summary

This document defines the technical architecture for Jovey, an AI-native business operating system for a household water pump manufacturing and e-commerce company. The system uses a modern tech stack combining FastAPI (Python backend), React (frontend), Supabase (database/auth/real-time), and Claude API (AI agents).

### Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend API | FastAPI (Python) | Business logic, AI orchestration, event processing |
| Frontend | React | User interface for all access tiers |
| Database | Supabase (PostgreSQL) | Event sourcing, data persistence |
| Authentication | Supabase Auth | Multi-tier access control |
| Real-time | Supabase Real-time | Agent communication, live updates |
| Storage | Supabase Storage | Product images, documents |
| AI Engine | Claude API (Anthropic) | AI agent decision-making |
| Hosting | TBD (start simple) | DigitalOcean/Render/Railway initially |

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Consumer   │  │    Dealer    │  │    Staff     │          │
│  │   Web App    │  │  B2B Portal  │  │  Dashboard   │          │
│  │   (React)    │  │   (React)    │  │   (React)    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────────┐
│                     API GATEWAY LAYER                             │
├────────────────────────────┼──────────────────────────────────────┤
│                            │                                       │
│                    ┌───────▼────────┐                            │
│                    │   FastAPI      │                            │
│                    │   Backend      │                            │
│                    │   (Python)     │                            │
│                    └───────┬────────┘                            │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌──────────────┐    ┌─────────────┐
│   SUPABASE    │    │  AI AGENTS   │    │  EXTERNAL   │
│  (Database +  │    │   (Claude    │    │   SERVICES  │
│   Auth +      │    │     API)     │    │  (Shipping, │
│   Real-time + │    │              │    │   Payment)  │
│   Storage)    │    │              │    │             │
└───────────────┘    └──────────────┘    └─────────────┘
```

### Request Flow

**Human User Request (e.g., View Products):**
1. User → React App → FastAPI Backend
2. FastAPI checks auth with Supabase
3. FastAPI queries Supabase database
4. FastAPI returns data to React
5. React renders UI

**AI Agent Decision (e.g., Reorder Inventory):**
1. Agent (Claude API) reads data from Supabase via FastAPI
2. Agent analyzes and makes decision
3. Agent posts EVENT to FastAPI
4. FastAPI validates and writes event to Supabase
5. Database Manager processes event → database update
6. Other agents notified via Supabase Real-time
7. Staff dashboard updates in real-time

---

## Core Architecture Patterns

### 1. Event-Sourced Data Model

**Key Principle:** Agents POST events (what happened), not direct data writes

**Event Flow:**
```
Agent Decision
    ↓
Post Event (via FastAPI endpoint)
    ↓
Event stored in events table (immutable log)
    ↓
Database Manager processes event
    ↓
Updates application state tables
    ↓
Other agents notified (via real-time subscriptions)
```

**Database Schema (Conceptual):**

```sql
-- Events table (immutable append-only log)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,  -- e.g., 'order', 'product', 'inventory'
    aggregate_id UUID NOT NULL,           -- ID of the entity this event affects
    data JSONB NOT NULL,                  -- Event payload
    metadata JSONB,                       -- Agent info, timestamp, etc.
    created_by VARCHAR(100),              -- Agent or user who created event
    created_at TIMESTAMP DEFAULT NOW(),
    version INTEGER                       -- For event versioning
);

-- Example: Application state table (derived from events)
CREATE TABLE products (
    id UUID PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2),
    active BOOLEAN DEFAULT true,
    -- Event sourcing metadata
    version INTEGER,                      -- Current version (for optimistic locking)
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Example: Current state is always derivable from events
-- If products table lost, can rebuild from events table
```

**Event Types (Examples):**
- `product.created`
- `product.price_updated`
- `order.placed`
- `order.fulfilled`
- `inventory.adjusted`
- `purchase_order.created`
- `invoice.generated`
- `payment.received`

**Benefits:**
- Complete audit trail (who did what, when)
- Can replay events to rebuild state
- Multiple projections from same events
- Time-travel debugging possible
- Prevents data conflicts between agents

---

### 2. Functional Page Architecture

Each business function has:
1. **Database tables** (for that function's data)
2. **FastAPI routes** (API endpoints for that function)
3. **React pages** (UI for humans)
4. **AI Agent** (automated decision-making)
5. **Event handlers** (respond to events from other functions)

**Example: Category Management Function**

```
category_management/
├── models.py           # Pydantic models + Supabase schema
├── routes.py           # FastAPI endpoints
├── agent.py            # Category Management AI agent
├── events.py           # Event handlers for this function
└── services.py         # Business logic services

frontend/pages/
└── category/
    ├── ProductCatalog.jsx    # Staff view
    └── PricingStrategy.jsx   # Staff view
```

---

### 3. AI Agent Architecture

**Agent Components:**

```python
# Conceptual agent structure

class BaseAgent:
    """Base class for all AI agents"""

    def __init__(self, function_name: str):
        self.function_name = function_name
        self.claude_client = Claude(api_key=settings.CLAUDE_API_KEY)
        self.supabase = get_supabase_client()

    async def read_data(self, query: str) -> dict:
        """Agents can READ all data"""
        return await self.supabase.query(query)

    async def post_event(self, event_type: str, data: dict) -> UUID:
        """Agents POST events (not direct writes)"""
        event = {
            "event_type": event_type,
            "data": data,
            "created_by": f"agent:{self.function_name}",
            "metadata": {"agent_version": "1.0", "timestamp": now()}
        }
        return await self.supabase.table("events").insert(event)

    async def make_decision(self, context: dict) -> dict:
        """Use Claude API to make decisions"""
        prompt = self._build_prompt(context)
        response = await self.claude_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096
        )
        return self._parse_response(response)

    async def message_agent(self, target_agent: str, message: str) -> dict:
        """Send message to another agent via real-time channel"""
        # Implementation using Supabase real-time
        pass


class CategoryAgent(BaseAgent):
    """Category Management AI Agent"""

    async def monitor_competitor_pricing(self):
        """Continuously monitor market pricing"""
        # Read current products
        products = await self.read_data("SELECT * FROM products")

        # Analyze market (could use web scraping, APIs, etc.)
        market_data = await self._fetch_market_data()

        # Use Claude to analyze and recommend
        context = {
            "products": products,
            "market_data": market_data,
            "current_strategy": await self._get_current_strategy()
        }
        decision = await self.make_decision(context)

        # If price change recommended
        if decision["action"] == "adjust_price":
            # Post event for human approval
            await self.post_event(
                event_type="price_adjustment.recommended",
                data={
                    "product_id": decision["product_id"],
                    "current_price": decision["current_price"],
                    "recommended_price": decision["recommended_price"],
                    "rationale": decision["rationale"],
                    "requires_approval": True
                }
            )
```

**Agent Communication Pattern:**

```python
# Example: Production Agent needs materials from Procurement Agent

# Production Agent
async def check_material_availability(self, bom: dict):
    """Production Agent checks with Procurement"""

    # Read current material inventory
    materials = await self.read_data(
        "SELECT * FROM raw_materials WHERE component_id IN (...)"
    )

    # If insufficient, message Procurement Agent
    if not self._sufficient_materials(materials, bom):
        response = await self.message_agent(
            target_agent="procurement",
            message={
                "type": "material_request",
                "components_needed": bom["components"],
                "quantity_needed": 100,
                "urgency": "high",
                "production_order_id": self.current_order_id
            }
        )

        # Procurement Agent receives message, checks inventory,
        # either confirms availability or posts PO event
        return response
```

---

### 4. Authentication & Authorization

**Using Supabase Auth + Row-Level Security (RLS)**

**Access Tiers:**
1. **Consumer (B2C)** - End customers
2. **Dealer (B2B)** - Wholesale accounts
3. **Staff** - Internal team members (function-specific access)

**Implementation:**

```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users PRIMARY KEY,
    user_type VARCHAR(20) NOT NULL,  -- 'consumer', 'dealer', 'staff'
    -- Consumer/Dealer fields
    company_name VARCHAR(255),       -- For dealers
    dealer_tier VARCHAR(20),         -- 'standard', 'premium', etc.
    -- Staff fields
    staff_role VARCHAR(50),          -- 'category_manager', 'fulfillment_operator', etc.
    function_access TEXT[],          -- Array of functions this staff can access
    -- Common fields
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Row-Level Security Policy Examples

-- Consumers can only see active products
CREATE POLICY "consumers_read_active_products"
ON products FOR SELECT
TO authenticated
USING (
    active = true
    AND (SELECT user_type FROM user_profiles WHERE id = auth.uid()) = 'consumer'
);

-- Dealers see products + their custom pricing
CREATE POLICY "dealers_read_products"
ON products FOR SELECT
TO authenticated
USING (
    active = true
    AND (SELECT user_type FROM user_profiles WHERE id = auth.uid()) = 'dealer'
);

-- Staff can see all products if they have category_management access
CREATE POLICY "staff_read_all_products"
ON products FOR SELECT
TO authenticated
USING (
    (SELECT user_type FROM user_profiles WHERE id = auth.uid()) = 'staff'
    AND 'category_management' = ANY(
        (SELECT function_access FROM user_profiles WHERE id = auth.uid())
    )
);

-- Dealers can only see their own orders
CREATE POLICY "dealers_read_own_orders"
ON orders FOR SELECT
TO authenticated
USING (
    customer_id = auth.uid()
    AND (SELECT user_type FROM user_profiles WHERE id = auth.uid()) = 'dealer'
);

-- Staff with fulfillment access can see all orders
CREATE POLICY "fulfillment_staff_read_all_orders"
ON orders FOR SELECT
TO authenticated
USING (
    (SELECT user_type FROM user_profiles WHERE id = auth.uid()) = 'staff'
    AND 'fulfillment' = ANY(
        (SELECT function_access FROM user_profiles WHERE id = auth.uid())
    )
);
```

**FastAPI Middleware:**

```python
from fastapi import Depends, HTTPException
from supabase import Client

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Validate token and get user info"""
    supabase: Client = get_supabase_client()
    user = supabase.auth.get_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    return user

async def require_staff_access(
    function: str,
    user: dict = Depends(get_current_user)
) -> dict:
    """Require staff access to specific function"""
    profile = await get_user_profile(user.id)
    if profile.user_type != "staff":
        raise HTTPException(status_code=403, detail="Staff access required")
    if function not in profile.function_access:
        raise HTTPException(status_code=403, detail=f"No access to {function}")
    return user

# Usage in routes
@router.get("/products/pricing-strategy")
async def get_pricing_strategy(
    user: dict = Depends(lambda: require_staff_access("category_management"))
):
    """Only Category Management staff can access"""
    # Implementation
```

---

### 5. Real-Time Communication

**Using Supabase Real-time for:**
1. Agent-to-agent communication
2. Live dashboard updates for staff
3. Order status updates for customers

**Implementation:**

```python
# Backend: Subscribe to agent messages channel
async def agent_listener():
    """Listen for agent messages"""
    supabase = get_supabase_client()

    # Subscribe to agent_messages channel
    channel = supabase.channel("agent_messages")

    def handle_message(payload):
        """Handle incoming agent message"""
        target_agent = payload["new"]["target_agent"]
        message = payload["new"]["message"]

        # Route to appropriate agent
        if target_agent == "procurement":
            await procurement_agent.handle_message(message)
        elif target_agent == "production":
            await production_agent.handle_message(message)
        # ... etc

    channel.on("postgres_changes",
               event="INSERT",
               schema="public",
               table="agent_messages",
               callback=handle_message)

    channel.subscribe()
```

```javascript
// Frontend: Subscribe to order updates
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// Customer/Dealer subscribes to their order status
const orderChannel = supabase
  .channel(`order:${orderId}`)
  .on('postgres_changes',
      { event: 'UPDATE', schema: 'public', table: 'orders', filter: `id=eq.${orderId}` },
      (payload) => {
        // Update UI with new order status
        setOrderStatus(payload.new.status)
      })
  .subscribe()

// Staff subscribes to all events for their function
const eventsChannel = supabase
  .channel('category-events')
  .on('postgres_changes',
      { event: '*', schema: 'public', table: 'events', filter: 'aggregate_type=eq.product' },
      (payload) => {
        // Update dashboard in real-time
        updateDashboard(payload.new)
      })
  .subscribe()
```

---

## Database Schema Design

### Core Tables

#### Events Table (Event Store)
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,           -- e.g., 'product.created'
    aggregate_type VARCHAR(50) NOT NULL,         -- e.g., 'product', 'order'
    aggregate_id UUID NOT NULL,                  -- ID of entity affected
    data JSONB NOT NULL,                         -- Event payload
    metadata JSONB,                              -- Agent info, correlation_id, etc.
    created_by VARCHAR(100),                     -- 'agent:category' or 'user:uuid'
    created_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1,

    -- Indexing for fast queries
    INDEX idx_events_aggregate (aggregate_type, aggregate_id),
    INDEX idx_events_type (event_type),
    INDEX idx_events_created_at (created_at DESC)
);
```

#### User Profiles
```sql
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users PRIMARY KEY,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('consumer', 'dealer', 'staff')),

    -- Dealer-specific
    company_name VARCHAR(255),
    dealer_tier VARCHAR(20),
    dealer_discount_percent DECIMAL(5,2),

    -- Staff-specific
    staff_role VARCHAR(50),
    function_access TEXT[],

    -- Common
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Products (Category Management)
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),                        -- 'tank_pump', 'pressure_pump'

    -- Specifications (JSONB for flexibility)
    specifications JSONB,                        -- { "flow_rate": "...", "pressure": "..." }

    -- Pricing
    base_price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),                         -- For margin calculations

    -- Images and media
    images TEXT[],                              -- Array of Supabase Storage URLs
    documents TEXT[],                           -- Manuals, spec sheets

    -- Status
    active BOOLEAN DEFAULT true,

    -- Event sourcing metadata
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dealer-specific pricing
CREATE TABLE dealer_product_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id UUID REFERENCES user_profiles(id),
    product_id UUID REFERENCES products(id),
    custom_price DECIMAL(10,2),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(dealer_id, product_id)
);
```

#### Orders (Customer Management + Fulfillment)
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,   -- Human-readable order number

    -- Customer info
    customer_id UUID REFERENCES user_profiles(id),
    customer_type VARCHAR(20),                   -- 'consumer' or 'dealer'

    -- Order details
    status VARCHAR(50) NOT NULL,                 -- 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    items JSONB NOT NULL,                        -- Array of order items

    -- Pricing
    subtotal DECIMAL(10,2) NOT NULL,
    tax DECIMAL(10,2),
    shipping DECIMAL(10,2),
    total DECIMAL(10,2) NOT NULL,

    -- Shipping
    shipping_address JSONB NOT NULL,
    tracking_number VARCHAR(100),
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,

    -- Payment
    payment_status VARCHAR(50),                  -- 'pending', 'paid', 'partial', 'refunded'
    payment_terms VARCHAR(50),                   -- 'immediate' (B2C), 'net_30' (B2B)

    -- Metadata
    notes TEXT,
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Inventory (Procurement + Fulfillment + Forecasting)
```sql
-- Raw materials (Procurement)
CREATE TABLE raw_materials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component_name VARCHAR(255) NOT NULL,
    component_sku VARCHAR(50) UNIQUE NOT NULL,
    supplier_id UUID REFERENCES suppliers(id),
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    unit_cost DECIMAL(10,2),
    reorder_point INTEGER,                       -- Trigger for reordering
    reorder_quantity INTEGER,
    last_ordered_at TIMESTAMP,
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Finished goods inventory (Fulfillment)
CREATE TABLE finished_goods_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    warehouse_location VARCHAR(50),
    quantity_available INTEGER NOT NULL DEFAULT 0,
    quantity_reserved INTEGER NOT NULL DEFAULT 0,  -- Reserved for orders
    quantity_in_transit INTEGER NOT NULL DEFAULT 0, -- From production
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(product_id, warehouse_location)
);

-- Inventory targets (Forecasting)
CREATE TABLE inventory_targets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    target_quantity INTEGER NOT NULL,
    safety_stock INTEGER NOT NULL,
    forecast_demand INTEGER,
    forecast_period VARCHAR(20),                 -- 'weekly', 'monthly'
    last_updated_by VARCHAR(100),                -- 'agent:forecasting'
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(product_id)
);
```

#### Suppliers (Procurement)
```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    payment_terms VARCHAR(50),                   -- 'net_30', 'net_60'
    lead_time_days INTEGER,                      -- Typical lead time
    quality_rating DECIMAL(3,2),                 -- 0.00 to 5.00
    active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id UUID REFERENCES suppliers(id),
    status VARCHAR(50) NOT NULL,                 -- 'draft', 'sent', 'confirmed', 'received', 'cancelled'
    items JSONB NOT NULL,                        -- Array of PO items
    total_cost DECIMAL(10,2) NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    notes TEXT,
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Agent Communication
```sql
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(50) NOT NULL,             -- 'category', 'procurement', etc.
    to_agent VARCHAR(50) NOT NULL,
    message_type VARCHAR(50) NOT NULL,           -- 'request', 'response', 'notification'
    payload JSONB NOT NULL,
    correlation_id UUID,                         -- For request-response pairing
    read_at TIMESTAMP,
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_agent_messages_to (to_agent, read_at)
);

CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    decision_type VARCHAR(100) NOT NULL,
    context JSONB NOT NULL,                      -- What data the agent considered
    decision JSONB NOT NULL,                     -- What the agent decided
    rationale TEXT,                              -- Why the agent made this decision
    requires_approval BOOLEAN DEFAULT true,
    approved BOOLEAN,
    approved_by UUID REFERENCES user_profiles(id),
    approved_at TIMESTAMP,
    executed BOOLEAN DEFAULT false,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Invoices & Payments (AR)
```sql
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    order_id UUID REFERENCES orders(id),
    customer_id UUID REFERENCES user_profiles(id),
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,                 -- 'draft', 'sent', 'paid', 'overdue', 'cancelled'
    due_date DATE NOT NULL,
    paid_date DATE,
    payment_method VARCHAR(50),
    notes TEXT,
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    payment_date TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Structure

### FastAPI Project Structure

```
backend/
├── main.py                          # FastAPI app entry point
├── config.py                        # Configuration settings
├── dependencies.py                  # Shared dependencies (auth, db, etc.)
│
├── core/
│   ├── __init__.py
│   ├── events.py                    # Event store interface
│   ├── database.py                  # Supabase client
│   └── auth.py                      # Authentication utilities
│
├── agents/
│   ├── __init__.py
│   ├── base.py                      # BaseAgent class
│   ├── category.py                  # Category Management Agent
│   ├── customer_management.py       # Customer Management Agent
│   ├── fulfillment.py               # Fulfillment Agent
│   ├── procurement.py               # Procurement Agent
│   └── orchestrator.py              # Agent communication orchestration
│
├── functions/
│   ├── category_management/
│   │   ├── __init__.py
│   │   ├── models.py                # Pydantic models
│   │   ├── routes.py                # API endpoints
│   │   ├── services.py              # Business logic
│   │   └── events.py                # Event handlers
│   │
│   ├── customer_management/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── services.py
│   │   └── events.py
│   │
│   ├── fulfillment/
│   │   └── ... (same structure)
│   │
│   ├── accounts_receivable/
│   │   └── ... (same structure)
│   │
│   └── database_manager/
│       ├── __init__.py
│       └── event_processor.py       # Processes events → DB updates
│
└── tests/
    └── ... (test files)
```

### API Endpoint Structure

**Base URL:** `https://api.jovey.com` (or localhost:8000 in dev)

**Authentication:** All endpoints require Bearer token (Supabase JWT)

#### Category Management Endpoints

```
GET    /api/v1/category/products              # List all products
GET    /api/v1/category/products/{id}         # Get product details
POST   /api/v1/category/products              # Create product (staff only)
PUT    /api/v1/category/products/{id}         # Update product (staff only)
DELETE /api/v1/category/products/{id}         # Deactivate product (staff only)

GET    /api/v1/category/pricing-strategy      # Get pricing strategy (staff only)
POST   /api/v1/category/pricing/update        # Update pricing (staff only, requires approval)

GET    /api/v1/category/market-intelligence   # Market pricing data (staff only)
GET    /api/v1/category/recommendations       # Agent recommendations (staff only)
```

#### Customer Management Endpoints

```
# B2C Customer endpoints
POST   /api/v1/customers/register             # Register new customer
GET    /api/v1/customers/profile              # Get customer profile
PUT    /api/v1/customers/profile              # Update profile

# Orders
POST   /api/v1/orders                         # Create order
GET    /api/v1/orders                         # List customer's orders
GET    /api/v1/orders/{id}                    # Get order details
PUT    /api/v1/orders/{id}/cancel             # Cancel order

# B2B Dealer endpoints
POST   /api/v1/dealers/apply                  # Apply to become dealer
GET    /api/v1/dealers/pricing                # Get dealer-specific pricing
GET    /api/v1/dealers/orders                 # Dealer order history
POST   /api/v1/dealers/orders/bulk            # Bulk order placement

# Staff endpoints
GET    /api/v1/customers (staff)              # List all customers (staff)
GET    /api/v1/dealers (staff)                # List all dealers (staff)
POST   /api/v1/dealers/{id}/approve (staff)   # Approve dealer application
```

#### Fulfillment Endpoints

```
GET    /api/v1/fulfillment/orders             # Orders to fulfill (staff)
GET    /api/v1/fulfillment/orders/{id}        # Order details (staff)
POST   /api/v1/fulfillment/orders/{id}/pick   # Mark order picked (staff)
POST   /api/v1/fulfillment/orders/{id}/pack   # Mark order packed (staff)
POST   /api/v1/fulfillment/orders/{id}/ship   # Mark order shipped (staff)

GET    /api/v1/fulfillment/inventory          # Current inventory levels (staff)
POST   /api/v1/fulfillment/inventory/adjust   # Adjust inventory (staff)
```

#### Accounts Receivable Endpoints

```
GET    /api/v1/ar/invoices                    # List invoices (staff)
GET    /api/v1/ar/invoices/{id}               # Invoice details (staff or customer)
POST   /api/v1/ar/invoices/{id}/send          # Send invoice to customer (staff)
POST   /api/v1/ar/invoices/{id}/record-payment # Record payment (staff)

GET    /api/v1/ar/reports/aging               # Aging report (staff)
GET    /api/v1/ar/reports/revenue             # Revenue report (staff)
```

#### Events Endpoints (Database Manager)

```
GET    /api/v1/events                         # Query events (staff)
GET    /api/v1/events/{id}                    # Get specific event (staff)
POST   /api/v1/events                         # Post new event (agents + staff)

GET    /api/v1/events/stream                  # Real-time event stream (SSE) (staff)
```

#### Agent Endpoints

```
POST   /api/v1/agents/decisions               # Agent posts decision for approval
GET    /api/v1/agents/decisions               # List pending decisions (staff)
POST   /api/v1/agents/decisions/{id}/approve  # Approve agent decision (staff)
POST   /api/v1/agents/decisions/{id}/reject   # Reject agent decision (staff)

GET    /api/v1/agents/messages                # Agent message log (staff)
POST   /api/v1/agents/message                 # Send message to agent (staff)
```

---

## Frontend Architecture

### React Project Structure

```
frontend/
├── public/
│   └── ... (static assets)
│
├── src/
│   ├── App.jsx                      # Main app component
│   ├── index.jsx                    # Entry point
│   │
│   ├── config/
│   │   ├── supabase.js              # Supabase client setup
│   │   └── constants.js             # App constants
│   │
│   ├── contexts/
│   │   ├── AuthContext.jsx          # Authentication state
│   │   └── RealtimeContext.jsx      # Real-time subscriptions
│   │
│   ├── hooks/
│   │   ├── useAuth.js               # Authentication hook
│   │   ├── useSupabase.js           # Supabase operations
│   │   └── useRealtime.js           # Real-time subscriptions
│   │
│   ├── components/
│   │   ├── common/                  # Shared components
│   │   │   ├── Layout.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── Loading.jsx
│   │   │   └── ErrorBoundary.jsx
│   │   │
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   │
│   │   └── ... (function-specific components)
│   │
│   ├── pages/
│   │   ├── consumer/                # B2C pages
│   │   │   ├── Home.jsx
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   ├── Cart.jsx
│   │   │   ├── Checkout.jsx
│   │   │   ├── OrderHistory.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── dealer/                  # B2B pages
│   │   │   ├── DealerDashboard.jsx
│   │   │   ├── DealerProducts.jsx
│   │   │   ├── BulkOrder.jsx
│   │   │   ├── OrderHistory.jsx
│   │   │   └── Resources.jsx
│   │   │
│   │   └── staff/                   # Staff function pages
│   │       ├── Dashboard.jsx        # Business Overview
│   │       │
│   │       ├── category/            # Category Management
│   │       │   ├── ProductCatalog.jsx
│   │       │   ├── PricingStrategy.jsx
│   │       │   ├── MarketIntelligence.jsx
│   │       │   └── AgentRecommendations.jsx
│   │       │
│   │       ├── customers/           # Customer Management
│   │       │   ├── CustomerList.jsx
│   │       │   ├── DealerManagement.jsx
│   │       │   ├── SupportTickets.jsx
│   │       │   └── Analytics.jsx
│   │       │
│   │       ├── fulfillment/         # Fulfillment
│   │       │   ├── OrderQueue.jsx
│   │       │   ├── InventoryView.jsx
│   │       │   ├── ShippingManagement.jsx
│   │       │   └── Returns.jsx
│   │       │
│   │       ├── ar/                  # Accounts Receivable
│   │       │   ├── InvoiceList.jsx
│   │       │   ├── PaymentTracking.jsx
│   │       │   ├── AgingReport.jsx
│   │       │   └── RevenueAnalytics.jsx
│   │       │
│   │       ├── database/            # Database Manager
│   │       │   ├── EventStream.jsx
│   │       │   ├── EventDetail.jsx
│   │       │   └── DataIntegrity.jsx
│   │       │
│   │       └── platform/            # Platform Manager
│   │           ├── SystemRoadmap.jsx
│   │           ├── ChangeRequests.jsx
│   │           └── Documentation.jsx
│   │
│   ├── services/
│   │   ├── api.js                   # API client
│   │   ├── products.js              # Product API calls
│   │   ├── orders.js                # Order API calls
│   │   └── ... (other services)
│   │
│   └── utils/
│       ├── formatting.js
│       ├── validation.js
│       └── helpers.js
│
└── package.json
```

### Frontend Technology Stack

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x",
    "@supabase/supabase-js": "^2.x",
    "@tanstack/react-query": "^5.x",         // Data fetching and caching
    "zustand": "^4.x",                        // State management
    "tailwindcss": "^3.x",                    // Styling
    "shadcn-ui": "latest",                    // UI components
    "recharts": "^2.x",                       // Charts for dashboards
    "date-fns": "^3.x",                       // Date utilities
    "zod": "^3.x",                            // Validation
    "react-hook-form": "^7.x"                 // Form handling
  }
}
```

---

## Development Phases

### Phase 0: Project Setup (Week 1)

**Goals:**
- Initialize repositories
- Set up development environment
- Configure Supabase project
- Create basic project scaffolding

**Tasks:**
1. Create Supabase project
2. Initialize FastAPI backend project
3. Initialize React frontend project
4. Set up version control (Git)
5. Configure development environment
6. Create initial database schema (tables, RLS policies)
7. Set up Claude API integration
8. Create basic authentication flow

**Deliverables:**
- Running FastAPI server (localhost:8000)
- Running React app (localhost:3000)
- Supabase project configured
- Basic authentication working (login/register)

---

### Phase 1: Core Infrastructure (Weeks 2-3)

**Goals:**
- Implement event-sourcing foundation
- Build Database Manager function
- Create base agent architecture

**Tasks:**
1. **Event Store Implementation**
   - Create events table and interface
   - Build event posting API
   - Build event query API

2. **Database Manager Function**
   - Event processor service
   - Event-to-database translation logic
   - Database Manager UI (event stream viewer)

3. **Base Agent Architecture**
   - BaseAgent class with Claude integration
   - Agent communication framework
   - Agent decision logging

4. **Authentication & Authorization**
   - Complete user profile management
   - Implement RLS policies
   - Create access control middleware

**Deliverables:**
- Events can be posted and stored
- Database Manager processes events
- Base agent can communicate with Claude API
- Authentication and authorization working

---

### Phase 2: First Business Function - Category Management (Weeks 4-5)

**Goals:**
- Build complete Category Management function
- Prove the functional architecture pattern

**Tasks:**
1. **Database Schema**
   - Products table with RLS
   - Dealer pricing table

2. **Backend API**
   - Product CRUD endpoints
   - Pricing endpoints
   - Event handlers for product events

3. **Category Management Agent**
   - Pricing analysis agent
   - Market intelligence (basic)
   - Decision recommendation system

4. **Frontend Pages**
   - Staff: Product catalog management
   - Staff: Pricing strategy dashboard
   - Consumer: Product listing (public view)
   - Dealer: Product listing with dealer pricing

**Deliverables:**
- Products can be created and managed
- Category Agent can recommend pricing decisions
- Staff can approve/reject recommendations
- Consumers/dealers can view products

---

### Phase 3: Customer Management & Orders (Weeks 6-7)

**Goals:**
- Build Customer Management function
- Enable B2C ordering flow

**Tasks:**
1. **Database Schema**
   - Orders and order items tables
   - Customer profiles enhancement

2. **Backend API**
   - Order creation and management
   - Customer profile management
   - Dealer application workflow

3. **Customer Management Agent**
   - Order processing automation
   - Customer inquiry handling (basic)
   - Dealer onboarding assistance

4. **Frontend Pages**
   - Consumer: Shopping cart and checkout
   - Consumer: Order history
   - Dealer: Bulk ordering
   - Staff: Customer management dashboard
   - Staff: Dealer approval workflow

**Deliverables:**
- Consumers can place orders
- Orders flow through system
- Customer Management Agent assists with basic tasks
- Dealer applications can be submitted and approved

---

### Phase 4: Fulfillment Function (Weeks 8-9)

**Goals:**
- Build Fulfillment function
- Complete order-to-fulfillment flow

**Tasks:**
1. **Database Schema**
   - Inventory tables
   - Shipping tracking

2. **Backend API**
   - Fulfillment workflow endpoints
   - Inventory management
   - Shipping integration (basic)

3. **Fulfillment Agent**
   - Order prioritization
   - Picking optimization
   - Inventory alerts

4. **Frontend Pages**
   - Staff: Order queue and fulfillment workflow
   - Staff: Inventory management
   - Consumer/Dealer: Order tracking

**Deliverables:**
- Orders can be fulfilled
- Inventory tracked accurately
- Fulfillment Agent optimizes workflows
- Customers can track shipments

---

### Phase 5: Accounts Receivable (Week 10)

**Goals:**
- Build AR function
- Complete order-to-payment flow

**Tasks:**
1. **Database Schema**
   - Invoices table
   - Payments table

2. **Backend API**
   - Invoice generation (automated from orders)
   - Payment recording
   - Reporting endpoints

3. **AR Agent**
   - Auto-generate invoices when orders ship
   - Payment reminder automation
   - Aging report alerts

4. **Frontend Pages**
   - Staff: Invoice management
   - Staff: Payment tracking
   - Staff: Aging reports
   - Consumer/Dealer: Invoice viewing

**Deliverables:**
- Invoices auto-generated
- Payments tracked
- AR Agent monitors receivables
- Staff can manage collections

---

### Phase 6: Business Overview & Platform Manager (Weeks 11-12)

**Goals:**
- Build Business Overview dashboard
- Build Platform Manager function
- Complete Phase 1 MVP

**Tasks:**
1. **Business Overview**
   - Aggregate metrics from all functions
   - Executive dashboard UI
   - Real-time updates

2. **Platform Manager**
   - Change request system
   - System documentation interface
   - Roadmap tracking

3. **Integration & Testing**
   - End-to-end testing of full order flow
   - Agent communication testing
   - Performance optimization

4. **Documentation**
   - User guides
   - Agent operation manual
   - API documentation

**Deliverables:**
- Complete Phase 1 MVP operational
- All 7 functions integrated and working
- Business can operate with this system
- Documentation complete

---

## Deployment Strategy

### Development Environment

```
Local Development:
- FastAPI: localhost:8000
- React: localhost:3000
- Supabase: cloud-hosted (dev project)
- Claude API: direct API calls
```

### Staging Environment

```
Staging (for testing):
- Backend: staging.jovey.com (or similar)
- Frontend: app-staging.jovey.com
- Supabase: cloud-hosted (staging project)
- Claude API: direct API calls
```

### Production Environment (Simple Start)

```
Production (Phase 1):
- Backend: DigitalOcean App Platform or Render
  - Docker container with FastAPI
  - Auto-scaling enabled

- Frontend: Vercel or Netlify
  - Static hosting with CDN
  - Auto-deploy from Git

- Database: Supabase (production project)
  - Automated backups
  - Point-in-time recovery

- AI: Claude API (Anthropic)
  - Direct API calls
  - Rate limiting configured
```

**Scaling Path:**
- Phase 1: Simple hosting (DigitalOcean/Render + Vercel)
- Phase 2: Move to AWS/GCP if needed for scale
- Phase 3: Kubernetes for multi-region if needed

---

## Security Considerations

### Application Security

1. **Authentication & Authorization**
   - Supabase JWT tokens for all API calls
   - Row-level security for all tables
   - Function-based access control for staff

2. **API Security**
   - Rate limiting on all endpoints
   - Input validation with Pydantic
   - CORS configured properly

3. **Agent Security**
   - Agents cannot write directly to database (only post events)
   - All agent decisions require human approval initially
   - Agent actions logged and auditable

4. **Data Security**
   - Sensitive data encrypted at rest (Supabase)
   - HTTPS for all traffic
   - Secrets managed via environment variables
   - Regular backups

### Compliance Considerations

- **GDPR** (if selling in EU): Right to erasure, data portability
- **PCI DSS** (payment processing): Use compliant payment processor (Stripe)
- **Data retention**: Event store retention policy (e.g., 7 years for financial events)

---

## Monitoring & Observability

### Metrics to Track

**System Health:**
- API response times
- Error rates
- Database query performance
- Event processing lag

**Business Metrics:**
- Orders per day
- Revenue
- Inventory levels
- Order fulfillment time

**Agent Metrics:**
- Decisions made
- Approval rate (human override rate)
- Decision execution time
- Agent communication volume

### Tools (to be set up)

- **Application Monitoring:** Sentry for error tracking
- **Logging:** Structured logging with JSON
- **Dashboards:** Grafana or similar for metrics
- **Alerting:** PagerDuty or email alerts for critical issues

---

## Cost Estimates (Phase 1)

**Monthly Operating Costs (estimated):**

| Service | Cost (USD/month) |
|---------|------------------|
| Supabase (Pro plan) | $25 |
| FastAPI Hosting (DigitalOcean) | $12-24 |
| React Hosting (Vercel) | $0-20 |
| Claude API (moderate usage) | $100-500 |
| Domain & SSL | $2 |
| **Total** | **$139-571/month** |

**Notes:**
- Claude API costs depend on usage (could be higher with many agents)
- Hosting costs increase with traffic
- Supabase may need higher tier as data grows

---

## Open Questions / To Be Determined

1. **Target Market:** Which country to launch in? (affects regulatory requirements)
2. **Specific Product SKUs:** What exact pump models to start with?
3. **Dealer Terms:** Specific pricing tiers and terms for dealers?
4. **Manufacturing Location:** Where will assembly happen?
5. **Shipping Partners:** Which carriers to integrate with?
6. **Payment Processing:** Stripe, PayPal, or other?
7. **Domain Name:** Is jovey.com available? Alternative?

---

## Next Steps

### Immediate (This Session or Next)

1. ✅ Technology stack decided
2. ✅ Technical architecture documented
3. 🔄 Review and validate this architecture
4. 📋 Initialize project repositories
5. 📋 Set up Supabase project
6. 📋 Create initial database schema
7. 📋 Scaffold FastAPI project
8. 📋 Scaffold React project

### Next Session

- Begin Phase 0: Project Setup
- Create Supabase project
- Initialize code repositories
- Set up development environment
- Build basic authentication flow

---

**Document Version:** 1.0
**Last Updated:** 2025-10-25
**Status:** Initial Design - Ready for Review and Implementation

---

## Appendix: Technology Justification

### Why FastAPI?
- Modern async Python framework
- Excellent for AI integration (Python ML/AI ecosystem)
- Auto-generated OpenAPI documentation
- Strong typing with Pydantic
- Fast development velocity
- Great for complex business logic

### Why React?
- Largest ecosystem and community
- Mature component libraries (shadcn-ui, MUI)
- Excellent for complex UIs
- Strong TypeScript support
- Well-established patterns

### Why Supabase?
- PostgreSQL (battle-tested, perfect for event sourcing)
- Built-in auth (saves weeks of development)
- Real-time subscriptions (perfect for agents + live dashboards)
- Row-level security (multi-tenant from day one)
- Storage included (product images)
- Auto-generated APIs (backup option)
- Great DX (developer experience)
- Affordable at scale

### Why Claude API?
- Best-in-class reasoning for complex decisions
- Excellent instruction-following
- Strong long-context for agent communication
- Good at structured output (important for agent decisions)
- Anthropic's focus on safety aligns with "human oversight" principle

### Why Event Sourcing?
- Complete audit trail (critical for business operations)
- Prevents data conflicts between agents
- Can replay events for debugging
- Multiple projections from same events
- Natural fit for AI-native architecture (agents post events, not writes)
