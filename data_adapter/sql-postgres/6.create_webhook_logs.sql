-- Create webhook_logs table for storing webhook events and their processing status
CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT gen_random_uuid(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    webhook_id VARCHAR(255) NOT NULL,
    integration_id INTEGER NOT NULL,
    post_id INTEGER,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Add foreign key constraints
    CONSTRAINT fk_integration
        FOREIGN KEY (integration_id)
        REFERENCES integrations(id)
        ON DELETE CASCADE,
        
    CONSTRAINT fk_post
        FOREIGN KEY (post_id)
        REFERENCES posts(id)
        ON DELETE SET NULL,
    
    -- Add unique constraint
    CONSTRAINT unique_webhook_event UNIQUE (webhook_id, event_type)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_webhook_logs_integration_id ON webhook_logs(integration_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_post_id ON webhook_logs(post_id) WHERE post_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_webhook_logs_status ON webhook_logs(status);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_created_at ON webhook_logs(created_at);
