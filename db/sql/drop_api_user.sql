
SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'api') AS role_exists \gset

\if :role_exists

-- Default privileges are not covered by DROP OWNED BY in all cases;
-- must be run as whichever role originally granted them.

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM api;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE USAGE, SELECT ON SEQUENCES FROM api;

-- Drops objects the role owns and revokes its privileges in THIS database.

DROP OWNED BY api;
DROP DATABASE alembic_demo;
DROP DATABASE api;
DROP ROLE api;

\else
\echo 'role api does not exist, nothing to do'
\endif


