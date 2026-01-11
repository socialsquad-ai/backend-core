-- This file runs first to enable required extensions
-- Docker entrypoint runs this against the POSTGRES_DB database

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
