
--  ---------------------------------------------------------------------------

\getenv demo_role DEMO_ROLE
-- \echo 'demo_role =' :demo_role

\getenv demo_password DEMO_PASSWORD
-- \echo 'demo_password =' :demo_password

\getenv demo_db DEMO_DB
-- \echo 'demo_db =' :demo_db

--  ---------------------------------------------------------------------------

CREATE ROLE :demo_role WITH LOGIN PASSWORD :'demo_password';

CREATE DATABASE :demo_role OWNER :demo_role;
CREATE DATABASE :demo_db   OWNER :demo_role;

GRANT CONNECT ON DATABASE :demo_db TO :demo_role;

GRANT USAGE ON SCHEMA public TO :demo_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO :demo_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO :demo_role;

--  ---------------------------------------------------------------------------
-- Setup privlieges

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO :demo_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO :demo_role;

