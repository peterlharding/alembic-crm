
-- create_demo_db.sql
-- Creates an application role and database for Alembic migrations.
-- Run with psql, passing these variables (see create_demo_db.sh):
--   -v demo_db=...  -v demo_role=...  -v demo_password=...
-- Safe to re-run: existing role/database are left in place, password is reset.

\set ON_ERROR_STOP on

-- 1. Role: create if missing, otherwise just refresh the password
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'demo_role', :'demo_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'demo_role')
\gexec

SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'demo_role', :'demo_password')
\gexec

-- 2. Personal database named after the role (e.g. role 'api' -> database 'api'),
--    owned by the role. psql and many clients connect to this by default
--    when no database name is given. Skipped if DEMO_DB has the same name.
SELECT format('CREATE DATABASE %I OWNER %I', :'demo_role', :'demo_role')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'demo_role')
\gexec

SELECT format('ALTER DATABASE %I OWNER TO %I', :'demo_role', :'demo_role')
\gexec

-- 3. Application database: CREATE DATABASE can't run inside a DO block, hence \gexec.
--    Making the role the owner gives it full DDL rights inside the DB.
SELECT format('CREATE DATABASE %I OWNER %I', :'demo_db', :'demo_role')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'demo_db')
\gexec

SELECT format('ALTER DATABASE %I OWNER TO %I', :'demo_db', :'demo_role')
\gexec

-- Only the owner (and superusers) may connect
SELECT format('REVOKE ALL ON DATABASE %I FROM PUBLIC', :'demo_db')
\gexec

-- 4. Inside the application database: give the role the public schema so
--    Alembic can create tables, types, sequences, indexes, etc.
--    (PG15+ no longer lets ordinary users create objects in public.)
\connect :"demo_db"

SELECT format('ALTER SCHEMA public OWNER TO %I', :'demo_role')
\gexec

SELECT format('GRANT ALL ON SCHEMA public TO %I', :'demo_role')
\gexec

\echo 'Done: databases' :"demo_role" 'and' :"demo_db" 'owned by role' :"demo_role"



