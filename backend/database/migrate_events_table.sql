-- ============================================================================
-- MIGRATION: Fix events table column naming
-- ============================================================================
-- This migration renames 'processed' to 'is_processed'
-- USE THIS if you want to preserve existing event data
-- ============================================================================

-- Step 1: Check if events table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'events') THEN
        RAISE NOTICE 'Events table exists, proceeding with migration...';

        -- Step 2: Check if we need to rename the column
        IF EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'events'
            AND column_name = 'processed'
        ) THEN
            RAISE NOTICE 'Renaming column: processed -> is_processed';
            ALTER TABLE events RENAME COLUMN processed TO is_processed;
        ELSE
            RAISE NOTICE 'Column already named is_processed, skipping rename';
        END IF;

        -- Step 3: Drop old index if it exists
        DROP INDEX IF EXISTS idx_events_unprocessed;

        -- Step 4: Create new index
        CREATE INDEX IF NOT EXISTS idx_events_unprocessed
            ON events(is_processed)
            WHERE is_processed = FALSE;

        RAISE NOTICE 'Migration complete!';
    ELSE
        RAISE NOTICE 'Events table does not exist. Run events_schema_clean.sql instead.';
    END IF;
END $$;

-- Verify the migration
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'events'
  AND column_name IN ('is_processed', 'processed')
ORDER BY column_name;
