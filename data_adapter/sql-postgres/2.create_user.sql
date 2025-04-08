CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    email VARCHAR(255) NOT NULL UNIQUE,
    timezone VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    password VARCHAR(255) NULL,
    status VARCHAR(255) NOT NULL DEFAULT 'pending'
);

GRANT ALL PRIVILEGES ON TABLE users TO ssq_user;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO ssq_user;