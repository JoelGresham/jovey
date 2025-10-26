-- ============================================================================
-- EVENTS TABLE - Event Sourcing Foundation (Clean Install)
-- ============================================================================
-- This version drops existing tables and creates fresh ones
-- USE WITH CAUTION: This will delete all existing event data!
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- DROP EXISTING TABLES (if they exist)
-- ============================================================================

DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS event_types CASCADE;

-- ============================================================================
-- Main Events Table
-- ============================================================================

CREATE TABLE events (
    -- Identity
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_number BIGSERIAL UNIQUE NOT NULL,

    -- Event Classification
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,

    -- Event Data
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Attribution
    created_by VARCHAR(100) NOT NULL,
    user_id UUID,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Event Versioning
    event_version INTEGER DEFAULT 1,

    -- Processing Status
    is_processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    processing_error TEXT,

    -- Causality
    correlation_id UUID,
    causation_id UUID,

    -- Idempotency
    idempotency_key VARCHAR(255) UNIQUE
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_created_at ON events(created_at DESC);
CREATE INDEX idx_events_created_by ON events(created_by);
CREATE INDEX idx_events_unprocessed ON events(is_processed) WHERE is_processed = FALSE;
CREATE INDEX idx_events_correlation ON events(correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX idx_events_data ON events USING GIN(data);
CREATE INDEX idx_events_metadata ON events USING GIN(metadata);

-- ============================================================================
-- Event Stream View
-- ============================================================================

CREATE VIEW event_stream AS
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
    is_processed,
    processed_at,
    correlation_id,
    causation_id
FROM events
ORDER BY event_number DESC;

-- ============================================================================
-- Helper Functions
-- ============================================================================

CREATE FUNCTION get_aggregate_events(
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

CREATE FUNCTION post_event(
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
-- Row Level Security (RLS)
-- ============================================================================

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Staff can view all events"
    ON events FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    );

CREATE POLICY "Users can view their own events"
    ON events FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- ============================================================================
-- Event Type Catalog
-- ============================================================================

CREATE TABLE event_types (
    event_type VARCHAR(100) PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    description TEXT,
    schema JSONB,
    example JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed event types
INSERT INTO event_types (event_type, aggregate_type, description, example) VALUES
('product.created', 'product', 'New product created', '{"sku": "SUBM-05HP", "name": "Pump"}'::jsonb),
('product.updated', 'product', 'Product updated', '{"changes": {"price": 5499}}'::jsonb),
('product.price_changed', 'product', 'Price changed', '{"old_price": 5999, "new_price": 5499}'::jsonb),
('product.stock_updated', 'product', 'Stock updated', '{"old_qty": 100, "new_qty": 95}'::jsonb),
('product.deactivated', 'product', 'Product deactivated', '{"reason": "discontinued"}'::jsonb),
('order.created', 'order', 'Order created', '{"total": 5999, "items": []}'::jsonb),
('order.payment_received', 'order', 'Payment received', '{"amount": 5999}'::jsonb),
('order.status_changed', 'order', 'Status changed', '{"old": "pending", "new": "paid"}'::jsonb),
('order.fulfilled', 'order', 'Order fulfilled', '{"tracking": "DHL123"}'::jsonb),
('order.cancelled', 'order', 'Order cancelled', '{"reason": "customer_request"}'::jsonb),
('customer.registered', 'customer', 'Customer registered', '{"email": "test@example.com"}'::jsonb),
('customer.profile_updated', 'customer', 'Profile updated', '{"changes": {"phone": "+91"}}'::jsonb),
('dealer.application_submitted', 'dealer', 'Application submitted', '{"business": "Pump World"}'::jsonb),
('dealer.approved', 'dealer', 'Dealer approved', '{"approved_by": "staff"}'::jsonb),
('dealer.pricing_updated', 'dealer', 'Pricing updated', '{"product_id": "uuid"}'::jsonb),
('category.created', 'category', 'Category created', '{"name": "Pumps"}'::jsonb),
('category.updated', 'category', 'Category updated', '{"changes": {}}'::jsonb),
('inventory.adjusted', 'inventory', 'Inventory adjusted', '{"adjustment": -5}'::jsonb),
('inventory.low_stock_alert', 'inventory', 'Low stock alert', '{"current": 5}'::jsonb),
('agent.decision_proposed', 'decision', 'AI decision proposed', '{"agent": "pricing"}'::jsonb),
('agent.decision_approved', 'decision', 'Decision approved', '{"approved_by": "user"}'::jsonb),
('agent.decision_rejected', 'decision', 'Decision rejected', '{"reason": "too risky"}'::jsonb);

-- Trigger for updated_at
CREATE FUNCTION update_event_types_updated_at()
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
-- Comments
-- ============================================================================

COMMENT ON TABLE events IS 'Immutable event log - source of truth';
COMMENT ON COLUMN events.is_processed IS 'Has Database Manager processed this?';

-- ============================================================================
-- Permissions
-- ============================================================================

GRANT SELECT ON events TO authenticated;
GRANT SELECT ON event_stream TO authenticated;
GRANT SELECT ON event_types TO authenticated;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT
    'Events table created successfully!' AS status,
    (SELECT COUNT(*) FROM event_types) AS event_types_seeded,
    (SELECT COUNT(*) FROM events) AS events_count;
