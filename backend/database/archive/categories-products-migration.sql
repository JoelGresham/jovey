-- ============================================================================
-- CATEGORY AND PRODUCT MANAGEMENT MIGRATION
-- Replaces existing products table with new category-based structure
-- ============================================================================

-- Drop existing products table and related objects if they exist
DROP TRIGGER IF EXISTS update_products_updated_at ON products;
DROP POLICY IF EXISTS "public_read_active_products" ON products;
DROP POLICY IF EXISTS "category_staff_manage_products" ON products;
DROP TABLE IF EXISTS dealer_product_pricing CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- ============================================================================
-- CATEGORIES TABLE (Hierarchical)
-- ============================================================================

CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for categories
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug);
CREATE INDEX IF NOT EXISTS idx_categories_is_active ON categories(is_active);
CREATE INDEX IF NOT EXISTS idx_categories_sort_order ON categories(sort_order);

-- Enable RLS on categories
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- RLS: Everyone can read active categories
CREATE POLICY "public_read_active_categories" ON categories
    FOR SELECT
    USING (is_active = true);

-- RLS: Authenticated users can insert categories
CREATE POLICY "authenticated_insert_categories" ON categories
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- RLS: Authenticated users can update categories
CREATE POLICY "authenticated_update_categories" ON categories
    FOR UPDATE
    TO authenticated
    USING (true);

-- RLS: Authenticated users can delete categories
CREATE POLICY "authenticated_delete_categories" ON categories
    FOR DELETE
    TO authenticated
    USING (true);

-- Trigger for updated_at
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PRODUCTS TABLE
-- ============================================================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    sku VARCHAR(100) UNIQUE,
    description TEXT,
    short_description VARCHAR(500),
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,

    -- Pricing
    base_price DECIMAL(10, 2) NOT NULL,
    sale_price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2),

    -- Inventory
    stock_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    is_in_stock BOOLEAN DEFAULT true,

    -- Product details
    specifications JSONB DEFAULT '{}'::jsonb,
    features JSONB DEFAULT '[]'::jsonb,
    images JSONB DEFAULT '[]'::jsonb,

    -- SEO & Display
    meta_title VARCHAR(200),
    meta_description VARCHAR(500),
    is_featured BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,

    -- Manufacturing details
    manufacturer VARCHAR(100),
    model_number VARCHAR(100),
    warranty_months INTEGER DEFAULT 12,

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES user_profiles(id),

    CONSTRAINT positive_base_price CHECK (base_price >= 0),
    CONSTRAINT positive_stock CHECK (stock_quantity >= 0)
);

-- Indexes for products
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_is_featured ON products(is_featured);
CREATE INDEX idx_products_base_price ON products(base_price);
CREATE INDEX idx_products_created_at ON products(created_at DESC);

-- Full-text search index
CREATE INDEX idx_products_search ON products
    USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Enable RLS on products
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- RLS: Everyone can read active products
CREATE POLICY "public_read_active_products" ON products
    FOR SELECT
    USING (is_active = true);

-- RLS: Authenticated users can manage products
CREATE POLICY "authenticated_manage_products" ON products
    FOR ALL
    TO authenticated
    USING (true);

-- Trigger for updated_at
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DEALER PRODUCT PRICING TABLE (for wholesale pricing)
-- ============================================================================

CREATE TABLE dealer_product_pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dealer_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    dealer_price DECIMAL(10, 2) NOT NULL,
    min_quantity INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(dealer_id, product_id, min_quantity),
    CONSTRAINT positive_dealer_price CHECK (dealer_price >= 0)
);

-- Indexes
CREATE INDEX idx_dealer_pricing_dealer ON dealer_product_pricing(dealer_id);
CREATE INDEX idx_dealer_pricing_product ON dealer_product_pricing(product_id);

-- Enable RLS
ALTER TABLE dealer_product_pricing ENABLE ROW LEVEL SECURITY;

-- RLS: Dealers can read their own pricing
CREATE POLICY "dealers_read_own_pricing" ON dealer_product_pricing
    FOR SELECT
    TO authenticated
    USING (dealer_id = auth.uid());

-- RLS: Staff can manage all pricing
CREATE POLICY "staff_manage_pricing" ON dealer_product_pricing
    FOR ALL
    TO authenticated
    USING (true);

-- Trigger for updated_at
CREATE TRIGGER update_dealer_pricing_updated_at
    BEFORE UPDATE ON dealer_product_pricing
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get full category path
CREATE OR REPLACE FUNCTION get_category_path(category_uuid UUID)
RETURNS TEXT AS $$
DECLARE
    result TEXT := '';
    current_id UUID := category_uuid;
    current_name TEXT;
    parent_uuid UUID;
BEGIN
    WHILE current_id IS NOT NULL LOOP
        SELECT name, parent_id INTO current_name, parent_uuid
        FROM categories
        WHERE id = current_id;

        IF result = '' THEN
            result := current_name;
        ELSE
            result := current_name || ' > ' || result;
        END IF;

        current_id := parent_uuid;
    END LOOP;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample categories
INSERT INTO categories (name, slug, description, sort_order) VALUES
    ('Submersible Pumps', 'submersible-pumps', 'Pumps designed to operate while submerged in water', 1),
    ('Monoblock Pumps', 'monoblock-pumps', 'Single-piece pumps for surface applications', 2),
    ('Openwell Pumps', 'openwell-pumps', 'Pumps for open wells and sumps', 3)
ON CONFLICT (slug) DO NOTHING;

-- Insert subcategories under Submersible
DO $$
DECLARE
    submersible_id UUID;
BEGIN
    SELECT id INTO submersible_id FROM categories WHERE slug = 'submersible-pumps';

    IF submersible_id IS NOT NULL THEN
        INSERT INTO categories (name, slug, description, parent_id, sort_order) VALUES
            ('Domestic Submersible', 'domestic-submersible', 'For household water supply', submersible_id, 1),
            ('Agricultural Submersible', 'agricultural-submersible', 'For irrigation and farming', submersible_id, 2),
            ('Industrial Submersible', 'industrial-submersible', 'Heavy-duty industrial applications', submersible_id, 3)
        ON CONFLICT (slug) DO NOTHING;
    END IF;
END $$;

-- Insert sample product
DO $$
DECLARE
    domestic_sub_id UUID;
BEGIN
    SELECT id INTO domestic_sub_id FROM categories WHERE slug = 'domestic-submersible';

    IF domestic_sub_id IS NOT NULL THEN
        INSERT INTO products (
            name, slug, sku, description, short_description, category_id,
            base_price, stock_quantity, is_in_stock,
            specifications, features, is_featured, is_active,
            manufacturer, model_number, warranty_months
        ) VALUES (
            '0.5 HP Domestic Submersible Pump',
            '05hp-domestic-submersible',
            'PUMP-DOM-05HP-001',
            'High-quality 0.5 HP submersible pump ideal for domestic water supply. Features stainless steel body and efficient motor.',
            'Efficient 0.5 HP pump for home water supply',
            domestic_sub_id,
            8500.00,
            50,
            true,
            '{"power": "0.5 HP", "voltage": "220V", "flow_rate": "30 LPM", "head": "50 meters", "material": "Stainless Steel", "motor_type": "Single Phase"}'::jsonb,
            '["Corrosion resistant stainless steel body", "Energy efficient motor", "Thermal overload protection", "Low noise operation", "Easy installation"]'::jsonb,
            true,
            true,
            'Jovey Pumps',
            'JP-DOM-05-2024',
            24
        )
        ON CONFLICT (slug) DO NOTHING;
    END IF;
END $$;

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW products_with_category AS
SELECT
    p.*,
    c.name as category_name,
    c.slug as category_slug,
    get_category_path(p.category_id) as category_path
FROM products p
LEFT JOIN categories c ON p.category_id = c.id;
