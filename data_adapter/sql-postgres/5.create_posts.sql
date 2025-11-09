-- Create posts table for storing social media posts and their engagement settings
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT gen_random_uuid(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    post_id VARCHAR(255) NOT NULL,
    integration_id INTEGER NOT NULL,
    ignore_instructions TEXT NOT NULL DEFAULT '',
    engagement_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    engagement_start_hours TIME NOT NULL DEFAULT '12:00:00',
    engagement_end_hours TIME NOT NULL DEFAULT '14:00:00',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraints
    CONSTRAINT uq_post_id UNIQUE (post_id),
    
    -- Add foreign key constraint
    CONSTRAINT fk_integration
        FOREIGN KEY (integration_id)
        REFERENCES integrations(id)
        ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_posts_post_id ON posts(post_id);
CREATE INDEX IF NOT EXISTS idx_posts_integration_id ON posts(integration_id);
CREATE INDEX IF NOT EXISTS idx_posts_engagement_enabled ON posts(engagement_enabled);