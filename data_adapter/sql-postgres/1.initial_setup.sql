-- From CLI, run `psql postgres` and then execute below statements: 
create database ssq;
CREATE USER ssq_user WITH PASSWORD 'ssq@143';
GRANT ALL PRIVILEGES ON DATABASE "ssq" to ssq_user;
\c ssq;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant comprehensive permissions on public schema
-- These permissions are required for:
-- 1. Application to create/manage tables (e.g., taskiq_postgresql needs CREATE permission)
-- 2. Full CRUD operations on all tables and sequences
-- 3. Default privileges for future objects created by ssq_user
GRANT ALL ON SCHEMA public TO ssq_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ssq_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ssq_user;
-- Grant permissions on existing tables (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ssq_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ssq_user;
