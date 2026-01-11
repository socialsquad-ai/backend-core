-- Initial setup for SSQ database
-- Note: Database and user are created by Docker via POSTGRES_DB, POSTGRES_USER env vars
-- Extension uuid-ossp is created in 0.extensions.sql
--
-- For manual CLI setup (non-Docker), run:
--   psql postgres
--   CREATE DATABASE ssq;
--   CREATE USER ssq_user WITH PASSWORD 'ssq@143';
--   GRANT ALL PRIVILEGES ON DATABASE "ssq" to ssq_user;
--   \c ssq;
--   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant comprehensive permissions on public schema
-- These permissions are required for:
-- 1. Application to create/manage tables (e.g., taskiq_postgresql needs CREATE permission)
-- 2. Full CRUD operations on all tables and sequences
-- 3. Default privileges for future objects

GRANT ALL ON SCHEMA public TO PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO PUBLIC;
