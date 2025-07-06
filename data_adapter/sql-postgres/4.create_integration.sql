-- Create Integration Table
CREATE TABLE IF NOT EXISTS integrations (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    platform VARCHAR(50) NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    token_type VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    scope VARCHAR(255),
    refresh_token VARCHAR(255)
);

GRANT ALL PRIVILEGES ON TABLE IF NOT EXISTS integrations TO ssq_user;
GRANT USAGE, SELECT ON SEQUENCE IF NOT EXISTS integrations_id_seq TO ssq_user;
