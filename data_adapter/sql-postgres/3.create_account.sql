-- Create Account Table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4(),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    comment_approvals BOOLEAN DEFAULT FALSE,
    comment_approvals_delay_seconds INTEGER DEFAULT 0,
    comment_response_delay_seconds INTEGER DEFAULT 0,
    comment_reply_depth INTEGER DEFAULT 1
);

GRANT ALL PRIVILEGES ON TABLE accounts TO ssq_user;
GRANT USAGE, SELECT ON SEQUENCE accounts_id_seq TO ssq_user;
