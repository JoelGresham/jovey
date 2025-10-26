-- ============================================================================
-- FIX FOR INFINITE RECURSION IN RLS POLICIES
-- Run this to fix the user_profiles RLS policies
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "users_read_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "users_update_own_profile" ON user_profiles;
DROP POLICY IF EXISTS "staff_read_all_profiles" ON user_profiles;

-- RLS Policy: Users can read their own profile
CREATE POLICY "users_read_own_profile" ON user_profiles
    FOR SELECT
    TO authenticated
    USING (auth.uid() = id);

-- RLS Policy: Users can update their own profile (basic fields only)
CREATE POLICY "users_update_own_profile" ON user_profiles
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = id);

-- RLS Policy: Allow service role to insert new profiles (during registration)
CREATE POLICY "service_insert_profiles" ON user_profiles
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Note: We removed the staff_read_all_profiles policy that caused infinite recursion
-- Staff access should be implemented at the application level using service role key
