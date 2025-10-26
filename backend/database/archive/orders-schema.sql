-- ============================================================================
-- ORDERS AND ORDER ITEMS SCHEMA
-- Support for guest and authenticated purchases
-- ============================================================================

-- ============================================================================
-- ORDERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_number VARCHAR(50) UNIQUE NOT NULL,

    -- Customer Information (for both guest and authenticated users)
    user_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_first_name VARCHAR(100) NOT NULL,
    customer_last_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(50),

    -- Shipping Address
    shipping_address_line1 VARCHAR(255) NOT NULL,
    shipping_address_line2 VARCHAR(255),
    shipping_city VARCHAR(100) NOT NULL,
    shipping_state VARCHAR(100) NOT NULL,
    shipping_postal_code VARCHAR(20) NOT NULL,
    shipping_country VARCHAR(100) DEFAULT 'India',

    -- Billing Address (optional, same as shipping if not provided)
    billing_address_line1 VARCHAR(255),
    billing_address_line2 VARCHAR(255),
    billing_city VARCHAR(100),
    billing_state VARCHAR(100),
    billing_postal_code VARCHAR(20),
    billing_country VARCHAR(100) DEFAULT 'India',

    -- Order Totals
    subtotal DECIMAL(10, 2) NOT NULL,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    tax_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,

    -- Order Status
    status VARCHAR(50) DEFAULT 'pending',
    payment_status VARCHAR(50) DEFAULT 'pending',

    -- Notes
    customer_notes TEXT,
    admin_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT positive_amounts CHECK (
        subtotal >= 0 AND
        shipping_cost >= 0 AND
        tax_amount >= 0 AND
        total_amount >= 0
    )
);

-- Indexes for orders
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_number ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_customer_email ON orders(customer_email);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);

-- ============================================================================
-- ORDER ITEMS TABLE
-- Individual products in each order
-- ============================================================================

CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,

    -- Product snapshot (in case product is deleted/changed)
    product_name VARCHAR(200) NOT NULL,
    product_sku VARCHAR(100),
    product_slug VARCHAR(200),

    -- Pricing at time of order
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,

    -- Product details snapshot
    specifications JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT positive_quantity CHECK (quantity > 0),
    CONSTRAINT positive_price CHECK (unit_price >= 0)
);

-- Indexes for order items
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- ============================================================================
-- ORDER STATUS HISTORY
-- Track status changes
-- ============================================================================

CREATE TABLE IF NOT EXISTS order_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    created_by UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for order status history
CREATE INDEX IF NOT EXISTS idx_order_status_history_order_id ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_created_at ON order_status_history(created_at DESC);

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Enable RLS on orders
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Users can read their own orders
CREATE POLICY "users_read_own_orders" ON orders
    FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

-- Anyone can create orders (for guest checkout)
CREATE POLICY "anyone_create_orders" ON orders
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Staff can read all orders
CREATE POLICY "staff_read_all_orders" ON orders
    FOR SELECT
    TO authenticated
    USING (true);

-- Staff can update orders
CREATE POLICY "staff_update_orders" ON orders
    FOR UPDATE
    TO authenticated
    USING (true);

-- Enable RLS on order_items
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

-- Users can read their own order items
CREATE POLICY "users_read_own_order_items" ON order_items
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM orders
            WHERE orders.id = order_items.order_id
            AND orders.user_id = auth.uid()
        )
    );

-- Anyone can create order items (for guest checkout)
CREATE POLICY "anyone_create_order_items" ON order_items
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Staff can read all order items
CREATE POLICY "staff_read_all_order_items" ON order_items
    FOR SELECT
    TO authenticated
    USING (true);

-- Enable RLS on order status history
ALTER TABLE order_status_history ENABLE ROW LEVEL SECURITY;

-- Anyone can read order status history
CREATE POLICY "anyone_read_order_status" ON order_status_history
    FOR SELECT
    TO authenticated
    USING (true);

-- Anyone can insert status history
CREATE POLICY "anyone_create_order_status" ON order_status_history
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger for orders updated_at
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to generate order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS TEXT AS $$
DECLARE
    new_number TEXT;
    counter INTEGER;
BEGIN
    -- Generate order number like JOV-20250126-001
    counter := (SELECT COUNT(*) FROM orders WHERE created_at::date = CURRENT_DATE) + 1;
    new_number := 'JOV-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(counter::TEXT, 3, '0');
    RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate order number on insert
CREATE OR REPLACE FUNCTION set_order_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
        NEW.order_number := generate_order_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_order_number_trigger
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION set_order_number();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Orders with item count and customer info
CREATE OR REPLACE VIEW orders_summary AS
SELECT
    o.*,
    COUNT(oi.id) as item_count,
    SUM(oi.quantity) as total_items
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id;

COMMENT ON TABLE orders IS 'Customer orders (guest and authenticated)';
COMMENT ON TABLE order_items IS 'Individual products in orders';
COMMENT ON TABLE order_status_history IS 'Order status change log';
