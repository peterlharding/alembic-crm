
--  ---------------------------------------------------------------------------
-- Undo create_api_user.sql. Run as the superuser, connected to the database
-- create_api_user.sql was run from (postgres by default).

\set ON_ERROR_STOP on

\getenv demo_role DEMO_ROLE
\getenv demo_db DEMO_DB

SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'demo_role') AS role_exists \gset

\if :role_exists

-- Default privileges are not covered by DROP OWNED BY in all cases;
-- must be run as whichever role originally granted them.

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM :"demo_role";

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE USAGE, SELECT ON SEQUENCES FROM :"demo_role";

-- Drops objects the role owns and revokes its privileges in THIS database.

DROP OWNED BY :"demo_role";
DROP DATABASE IF EXISTS :"demo_db";
DROP DATABASE IF EXISTS :"demo_role";
DROP ROLE :"demo_role";

\else
\echo 'role' :demo_role 'does not exist, nothing to do'
\endif

