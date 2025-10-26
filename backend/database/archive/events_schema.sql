-- ============================================================================
-- EVENTS TABLE - Event Sourcing Foundation
-- ============================================================================
-- This table is the immutable log of all state changes in the system.
-- AI agents and system operations post events here, and the Database Manager
-- translates these events into state table updates.
--
-- Key Principles:
-- 1. Events are IMMUTABLE (never updated or deleted)
-- 2. Events are the SOURCE OF TRUTH
-- 3. Current state tables are DERIVED from events
-- 4. Events enable complete audit trail and time-travel debugging
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Main Events Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    -- Identity
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_number BIGSERIAL UNIQUE NOT NULL,  -- Sequential number for ordering

    -- Event Classification
    event_type VARCHAR(100) NOT NULL,        -- e.g., 'product.created', 'order.placed'
    aggregate_type VARCHAR(50) NOT NULL,     -- e.g., 'product', 'order', 'customer'
    aggregate_id UUID NOT NULL,              -- ID of the entity this event affects

    -- Event Data
    data JSONB NOT NULL,                     -- Event payload (the actual data)
    metadata JSONB DEFAULT '{}'::jsonb,      -- Additional context

    -- Attribution
    created_by VARCHAR(100) NOT NULL,        -- 'user:{uuid}', 'agent:{name}', 'system'
    user_id UUID REFERENCES auth.users(id),  -- User who initiated (if applicable)

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Event Versioning (for schema evolution)
    event_version INTEGER DEFAULT 1,

    -- Processing Status
    processed BOOLEAN DEFAULT FALSE,         -- Has Database Manager processed this?
    processed_at TIMESTAMPTZ,
    processing_error TEXT,                   -- Error message if processing failed

    -- Causality (for event chains)
    correlation_id UUID,                     -- Links related events together
    causation_id UUID,                       -- The event that caused this event

    -- Idempotency
    idempotency_key VARCHAR(255) UNIQUE      -- Prevents duplicate event processing
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Primary query patterns
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by);
CREATE INDEX IF NOT EXISTS idx_events_unprocessed ON events(processed) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_events_correlation ON events(correlation_id) WHERE correlation_id IS NOT NULL;

-- GIN index for JSONB queries
CREATE INDEX IF NOT EXISTS idx_events_data ON events USING GIN(data);
CREATE INDEX IF NOT EXISTS idx_events_metadata ON events USING GIN(metadata);

-- ============================================================================
-- Event Stream View (for humans/agents to read)
-- ============================================================================

CREATE OR REPLACE VIEW event_stream AS
SELECT
    id,
    event_number,
    event_type,
    aggregate_type,
    aggregate_id,
    data,
    metadata,
    created_by,
    created_at,
    processed,
    processed_at,
    correlation_id,
    causation_id
FROM events
ORDER BY event_number DESC;

-- ============================================================================
-- Aggregate Event History View (events for a specific entity)
-- ============================================================================

CREATE OR REPLACE FUNCTION get_aggregate_events(
    p_aggregate_type VARCHAR,
    p_aggregate_id UUID
)
RETURNS TABLE (
    event_number BIGINT,
    event_type VARCHAR,
    data JSONB,
    created_by VARCHAR,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.event_number,
        e.event_type,
        e.data,
        e.created_by,
        e.created_at
    FROM events e
    WHERE e.aggregate_type = p_aggregate_type
      AND e.aggregate_id = p_aggregate_id
    ORDER BY e.event_number ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Row Level Security (RLS)
-- ============================================================================

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- Staff can view all events
CREATE POLICY "Staff can view all events"
    ON events FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.user_id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    );

-- Agents (via service role) can insert events
-- Note: Agents authenticate with service_role key, not as users
-- So we'll allow inserts from service_role in application code

-- Users can view events related to their own actions
CREATE POLICY "Users can view their own events"
    ON events FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- ============================================================================
-- Event Type Catalog (for documentation and validation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS event_types (
    event_type VARCHAR(100) PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    description TEXT,
    schema JSONB,                            -- JSON Schema for validation
    example JSONB,                           -- Example event payload
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed initial event types
INSERT INTO event_types (event_type, aggregate_type, description, example) VALUES
-- Product Events
('product.created', 'product', 'New product created in catalog',
 '{"product_id": "uuid", "sku": "SUBM-05HP-DOM-SS-50LPM-20M", "name": "0.5HP Submersible Pump", "base_price": 5999.00}'::jsonb),

('product.updated', 'product', 'Product details updated',
 '{"product_id": "uuid", "changes": {"base_price": 5499.00}, "previous": {"base_price": 5999.00}}'::jsonb),

('product.price_changed', 'product', 'Product price changed',
 '{"product_id": "uuid", "old_price": 5999.00, "new_price": 5499.00, "reason": "competitor_match"}'::jsonb),

('product.stock_updated', 'product', 'Product stock quantity updated',
 '{"product_id": "uuid", "old_quantity": 100, "new_quantity": 95, "reason": "order_placed"}'::jsonb),

('product.deactivated', 'product', 'Product marked as inactive',
 '{"product_id": "uuid", "reason": "discontinued"}'::jsonb),

-- Order Events
('order.created', 'order', 'New order placed by customer',
 '{"order_id": "uuid", "customer_id": "uuid", "total": 5999.00, "items": [{"product_id": "uuid", "quantity": 1}]}'::jsonb),

('order.payment_received', 'order', 'Payment received for order',
 '{"order_id": "uuid", "amount": 5999.00, "payment_method": "razorpay", "transaction_id": "pay_xyz"}'::jsonb),

('order.status_changed', 'order', 'Order status updated',
 '{"order_id": "uuid", "old_status": "pending", "new_status": "processing", "changed_by": "user:uuid"}'::jsonb),

('order.fulfilled', 'order', 'Order shipped to customer',
 '{"order_id": "uuid", "tracking_number": "DHL123", "shipped_at": "2025-10-26T10:00:00Z"}'::jsonb),

('order.cancelled', 'order', 'Order cancelled',
 '{"order_id": "uuid", "reason": "customer_request", "refund_amount": 5999.00}'::jsonb),

-- Customer Events
('customer.registered', 'customer', 'New customer account created',
 '{"customer_id": "uuid", "email": "customer@example.com", "name": "John Doe"}'::jsonb),

('customer.profile_updated', 'customer', 'Customer profile updated',
 '{"customer_id": "uuid", "changes": {"phone": "+91-9876543210"}}'::jsonb),

-- Dealer Events
('dealer.application_submitted', 'dealer', 'New dealer application submitted',
 '{"dealer_id": "uuid", "business_name": "Pump World", "email": "dealer@example.com"}'::jsonb),

('dealer.approved', 'dealer', 'Dealer application approved',
 '{"dealer_id": "uuid", "approved_by": "user:uuid", "approved_at": "2025-10-26T10:00:00Z"}'::jsonb),

('dealer.pricing_updated', 'dealer', 'Dealer-specific pricing updated',
 '{"dealer_id": "uuid", "product_id": "uuid", "dealer_price": 4999.00, "retail_price": 5999.00}'::jsonb),

-- Category Events
('category.created', 'category', 'New product category created',
 '{"category_id": "uuid", "name": "Submersible Pumps", "slug": "submersible-pumps"}'::jsonb),

('category.updated', 'category', 'Category details updated',
 '{"category_id": "uuid", "changes": {"description": "High-quality submersible water pumps"}}'::jsonb),

-- Inventory Events
('inventory.adjusted', 'inventory', 'Inventory quantity manually adjusted',
 '{"product_id": "uuid", "adjustment": -5, "reason": "damaged_goods", "adjusted_by": "user:uuid"}'::jsonb),

('inventory.low_stock_alert', 'inventory', 'Product stock below threshold',
 '{"product_id": "uuid", "current_stock": 5, "threshold": 10, "suggested_reorder": 50}'::jsonb),

-- Agent Decision Events
('agent.decision_proposed', 'decision', 'AI agent proposed a decision requiring approval',
 '{"decision_id": "uuid", "agent": "category_agent", "decision_type": "price_change", "proposal": {"product_id": "uuid", "new_price": 5299.00}, "confidence": 0.85, "reasoning": "Competitor pricing analysis"}'::jsonb),

('agent.decision_approved', 'decision', 'Human approved agent decision',
 '{"decision_id": "uuid", "approved_by": "user:uuid", "approved_at": "2025-10-26T10:00:00Z"}'::jsonb),

('agent.decision_rejected', 'decision', 'Human rejected agent decision',
 '{"decision_id": "uuid", "rejected_by": "user:uuid", "reason": "Price too low", "rejected_at": "2025-10-26T10:00:00Z"}'::jsonb)

ON CONFLICT (event_type) DO NOTHING;

-- ============================================================================
-- Trigger to update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_event_types_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_event_types_updated_at
    BEFORE UPDATE ON event_types
    FOR EACH ROW
    EXECUTE FUNCTION update_event_types_updated_at();

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function to post an event (simplified - real implementation in application code)
CREATE OR REPLACE FUNCTION post_event(
    p_event_type VARCHAR,
    p_aggregate_type VARCHAR,
    p_aggregate_id UUID,
    p_data JSONB,
    p_created_by VARCHAR,
    p_user_id UUID DEFAULT NULL,
    p_correlation_id UUID DEFAULT NULL,
    p_idempotency_key VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_event_id UUID;
BEGIN
    INSERT INTO events (
        event_type,
        aggregate_type,
        aggregate_id,
        data,
        created_by,
        user_id,
        correlation_id,
        idempotency_key
    ) VALUES (
        p_event_type,
        p_aggregate_type,
        p_aggregate_id,
        p_data,
        p_created_by,
        p_user_id,
        p_correlation_id,
        p_idempotency_key
    )
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE events IS 'Immutable event log - source of truth for all state changes';
COMMENT ON COLUMN events.event_type IS 'Dotted notation: aggregate.action (e.g., product.created)';
COMMENT ON COLUMN events.aggregate_type IS 'Type of entity affected (product, order, customer, etc.)';
COMMENT ON COLUMN events.aggregate_id IS 'UUID of the specific entity instance';
COMMENT ON COLUMN events.data IS 'Event payload - contains the actual event data';
COMMENT ON COLUMN events.metadata IS 'Additional context like IP address, user agent, timestamps';
COMMENT ON COLUMN events.created_by IS 'Format: user:{uuid}, agent:{name}, or system';
COMMENT ON COLUMN events.processed IS 'Has Database Manager processed this event into state tables?';
COMMENT ON COLUMN events.correlation_id IS 'Groups related events (e.g., all events in one order flow)';
COMMENT ON COLUMN events.causation_id IS 'The event that triggered this event (causal chain)';
COMMENT ON COLUMN events.idempotency_key IS 'Unique key to prevent duplicate event processing';

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant SELECT to authenticated users (filtered by RLS)
GRANT SELECT ON events TO authenticated;
GRANT SELECT ON event_stream TO authenticated;

-- Grant SELECT on event_types to authenticated users
GRANT SELECT ON event_types TO authenticated;

-- Service role (for agents) needs full access - handled in application code

-- ============================================================================
-- Done!
-- ============================================================================

-- Verify the setup
SELECT 'Events table created successfully!' AS status,
       COUNT(*) AS event_types_seeded
FROM event_types;
