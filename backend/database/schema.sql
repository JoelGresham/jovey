-- Jovey Database Schema
-- AI-Native Business Operating System
-- Version: 0.1.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- EVENTS TABLE (Event Store)
-- Core of event-sourced architecture
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Indexes for fast event queries
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by);

-- Enable Row Level Security
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Staff can read all events
CREATE POLICY "staff_read_all_events" ON events
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.user_type = 'staff'
        )
    );

-- RLS Policy: Agents and staff can insert events
CREATE POLICY "staff_insert_events" ON events
    FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.user_type = 'staff'
        )
    );

-- ============================================================================
-- USER PROFILES TABLE
-- Extends Supabase auth.users with business logic
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('consumer', 'dealer', 'staff')),

    -- Common fields
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(50),

    -- Dealer-specific fields
    company_name VARCHAR(255),
    dealer_tier VARCHAR(20) CHECK (dealer_tier IN ('standard', 'premium', 'platinum')),
    dealer_discount_percent DECIMAL(5,2) DEFAULT 0.00,
    dealer_status VARCHAR(20) DEFAULT 'pending' CHECK (dealer_status IN ('pending', 'active', 'suspended', 'inactive')),

    -- Staff-specific fields
    staff_role VARCHAR(50),
    function_access TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_type ON user_profiles(user_type);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_dealer_status ON user_profiles(dealer_status) WHERE user_type = 'dealer';

-- Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read their own profile
CREATE POLICY "users_read_own_profile" ON user_profiles
    FOR SELECT
    TO authenticated
    USING (auth.uid() = id);

-- RLS Policy: Users can update their own profile
CREATE POLICY "users_update_own_profile" ON user_profiles
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id);

-- RLS Policy: Staff can read all profiles
CREATE POLICY "staff_read_all_profiles" ON user_profiles
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles up
            WHERE up.id = auth.uid()
            AND up.user_type = 'staff'
        )
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PRODUCTS TABLE (Category Management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),

    -- Specifications
    specifications JSONB DEFAULT '{}'::jsonb,

    -- Pricing
    base_price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),

    -- Media
    images TEXT[] DEFAULT ARRAY[]::TEXT[],
    documents TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Status
    active BOOLEAN DEFAULT true,

    -- Event sourcing metadata
    version INTEGER DEFAULT 1,
    last_event_id UUID REFERENCES events(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(active);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Enable RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Anyone can read active products
CREATE POLICY "public_read_active_products" ON products
    FOR SELECT
    TO authenticated
    USING (active = true);

-- RLS Policy: Staff with category_management access can manage products
CREATE POLICY "category_staff_manage_products" ON products
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.user_type = 'staff'
            AND 'category_management' = ANY(user_profiles.function_access)
        )
    );

-- Trigger for updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DEALER PRODUCT PRICING
-- Custom pricing for specific dealers
-- ============================================================================

CREATE TABLE IF NOT EXISTS dealer_product_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    custom_price DECIMAL(10,2) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(dealer_id, product_id)
);

-- Enable RLS
ALTER TABLE dealer_product_pricing ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Dealers can see their own pricing
CREATE POLICY "dealers_read_own_pricing" ON dealer_product_pricing
    FOR SELECT
    TO authenticated
    USING (
        dealer_id = auth.uid()
    );

-- RLS Policy: Staff can manage all pricing
CREATE POLICY "staff_manage_pricing" ON dealer_product_pricing
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.user_type = 'staff'
        )
    );

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create initial staff user (to be created after first auth signup)
-- You'll need to manually promote your first user to staff after signup

COMMENT ON TABLE events IS 'Event store - immutable log of all system events';
COMMENT ON TABLE user_profiles IS 'User profiles extending Supabase auth with business logic';
COMMENT ON TABLE products IS 'Product catalog for water pumps';
COMMENT ON TABLE dealer_product_pricing IS 'Custom pricing for dealer accounts';
