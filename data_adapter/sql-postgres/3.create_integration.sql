-- Create Integration Table
CREATE TABLE IF NOT EXISTS integrations (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    is_deleted BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    platform_user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    token_type VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    scopes JSON,
    refresh_token VARCHAR(255),
    refresh_token_expires_at TIMESTAMPTZ NOT NULL
);
