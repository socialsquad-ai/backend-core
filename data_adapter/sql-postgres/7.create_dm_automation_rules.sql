-- Create dm_automation_rule table for managing DM automation rules
CREATE TABLE IF NOT EXISTS dm_automation_rules (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT gen_random_uuid(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    integration_id INTEGER NOT NULL,
    post_id VARCHAR(255),
    trigger_type VARCHAR(50) NOT NULL,
    match_type VARCHAR(50),
    trigger_text TEXT NOT NULL,
    dm_response TEXT NOT NULL,
    comment_reply TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Add constraints
    CONSTRAINT fk_integration
        FOREIGN KEY (integration_id)
        REFERENCES integrations(id)
        ON DELETE CASCADE,
    CONSTRAINT chk_trigger_type CHECK (trigger_type IN ('comment', 'dm')),
    CONSTRAINT chk_match_type CHECK (match_type IN ('EXACT_TEXT', 'AI_INTENT'))
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_dm_automation_rules_integration_id ON dm_automation_rules(integration_id);
CREATE INDEX IF NOT EXISTS idx_dm_automation_rules_post_id ON dm_automation_rules(post_id);
CREATE INDEX IF NOT EXISTS idx_dm_automation_rules_trigger_type ON dm_automation_rules(trigger_type);

-- Trigger to automatically update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON dm_automation_rules
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
