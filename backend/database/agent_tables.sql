-- ============================================================================
-- AI AGENT INFRASTRUCTURE TABLES
-- ============================================================================
-- These tables support the AI agent system for autonomous decision-making

-- Drop existing tables if they exist (for clean re-run)
DROP TABLE IF EXISTS agent_decisions CASCADE;
DROP TABLE IF EXISTS agent_messages CASCADE;

-- ============================================================================
-- AGENT MESSAGES TABLE
-- ============================================================================
-- Stores messages between agents for peer-to-peer communication

CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(50) NOT NULL,           -- e.g., "agent:category"
    to_agent VARCHAR(50) NOT NULL,             -- e.g., "agent:procurement"
    message_type VARCHAR(50) NOT NULL,         -- e.g., "request", "response", "notification"
    payload JSONB NOT NULL,                    -- Message data
    correlation_id UUID,                       -- Links request/response pairs
    read_at TIMESTAMPTZ,                       -- When message was read
    responded_at TIMESTAMPTZ,                  -- When response was sent
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add comment
COMMENT ON TABLE agent_messages IS 'Peer-to-peer communication between AI agents';

-- Create indexes
CREATE INDEX idx_agent_messages_to_agent ON agent_messages(to_agent, read_at);
CREATE INDEX idx_agent_messages_correlation ON agent_messages(correlation_id);

-- ============================================================================
-- AGENT DECISIONS TABLE
-- ============================================================================
-- Tracks decisions made by agents and their approval status

CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,           -- Which agent made the decision
    decision_type VARCHAR(100) NOT NULL,       -- Type of decision (e.g., "price_adjustment")

    -- Decision details
    context JSONB NOT NULL,                    -- What data the agent considered
    decision JSONB NOT NULL,                   -- What the agent decided to do
    rationale TEXT,                            -- Why the agent made this decision
    confidence_score DECIMAL(3,2),             -- Agent's confidence (0.00 to 1.00)

    -- Approval workflow
    requires_approval BOOLEAN DEFAULT TRUE,
    approved BOOLEAN,                          -- NULL = pending, TRUE = approved, FALSE = rejected
    approved_by UUID REFERENCES user_profiles(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,                     -- If rejected, why?

    -- Execution tracking
    executed BOOLEAN DEFAULT FALSE,
    executed_at TIMESTAMPTZ,
    execution_result JSONB,                    -- Result of executing the decision

    -- Event linkage
    decision_event_id UUID REFERENCES events(id),  -- Event posted when decision was made
    execution_event_id UUID REFERENCES events(id), -- Event posted when decision was executed

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_agent_decisions_agent ON agent_decisions(agent_name, created_at);
CREATE INDEX idx_agent_decisions_approval ON agent_decisions(requires_approval, approved, created_at);
CREATE INDEX idx_agent_decisions_execution ON agent_decisions(executed, created_at);

-- Add comment
COMMENT ON TABLE agent_decisions IS 'Tracks AI agent decisions and human approval workflow';

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_agent_decisions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agent_decisions_updated_at
    BEFORE UPDATE ON agent_decisions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_decisions_updated_at();

-- ============================================================================
-- ROW-LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_decisions ENABLE ROW LEVEL SECURITY;

-- Agent Messages Policies
CREATE POLICY "Staff can view all agent messages"
    ON agent_messages FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    );

CREATE POLICY "Service role can manage agent messages"
    ON agent_messages FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- Agent Decisions Policies
CREATE POLICY "Staff can view all agent decisions"
    ON agent_decisions FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    );

CREATE POLICY "Staff can approve/reject decisions"
    ON agent_decisions FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_profiles.id = auth.uid()
              AND user_profiles.user_type = 'staff'
        )
    );

CREATE POLICY "Service role can manage agent decisions"
    ON agent_decisions FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================

-- Run this to verify tables were created successfully:
SELECT 'agent_messages' AS table_name, COUNT(*) AS row_count FROM agent_messages
UNION ALL
SELECT 'agent_decisions' AS table_name, COUNT(*) AS row_count FROM agent_decisions;

-- SUCCESS message
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS! AI Agent tables created successfully';
    RAISE NOTICE 'Tables: agent_messages, agent_decisions';
    RAISE NOTICE 'Next: Run this SQL in your Supabase SQL Editor';
END $$;
