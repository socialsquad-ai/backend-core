CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    auth0_user_id VARCHAR(255) NOT NULL UNIQUE,  -- Auth0 user ID
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    signup_method VARCHAR(50) NOT NULL DEFAULT 'email-password',  -- email-password, google, facebook, etc.
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    auth0_created_at TIMESTAMP  -- When user was created in Auth0
);

GRANT ALL PRIVILEGES ON TABLE IF NOT EXISTS users TO ssq_user;
GRANT USAGE, SELECT ON SEQUENCE IF NOT EXISTS users_id_seq TO ssq_user;
