-- From CLI, run `psql postgres` and then execute below statements: 
create database ssq;
CREATE USER ssq_user WITH PASSWORD 'ssq@143';
GRANT ALL PRIVILEGES ON DATABASE "ssq" to ssq_user;
\c ssq;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
