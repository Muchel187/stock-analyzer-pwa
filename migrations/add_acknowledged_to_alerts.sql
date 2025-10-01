-- Add acknowledged column to alerts table
-- For Phase 3 Part 3: Notification Center

ALTER TABLE alerts ADD COLUMN IF NOT EXISTS acknowledged BOOLEAN DEFAULT FALSE;

-- Update existing triggered alerts to be acknowledged (so they don't all show up)
UPDATE alerts SET acknowledged = TRUE WHERE is_triggered = TRUE AND acknowledged IS NULL;
