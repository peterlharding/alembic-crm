# alembic-crm

Intro to using alembic to setup and manage a Postgres database.

This walk through assumes you have a number of tools available:

* python (>= 3.12)
* uv (https://docs.astral.sh/uv/getting-started/installation/)
* git
* make
* docker

The project makes extensive use of a Makefile and make recipes
to setup and manage the project resources.

This project was originally developed on a macOS laptop and
has not been tested on Linux.  It has been successfully run on
Windows 11 under WSL.

# Using this Project

Work through the following steps to explore this proejct

## Step 1: Clone the Repo

Assume we add it under ~/src

```bash
cd ~/src
git clone https://github.com/peterlharding/alembic-crm.git
cd alembic-crm
```


## Step 2: Initialize the VENV

This assumes you have Python and uv installed.

Run:

```
activate
uv sync
```

Here is a representative transcript of the 'uv sync' operation:

```bash
% activate
(alembic-crm) % 
(alembic-crm) % uv sync
Using CPython 3.14.7 interpreter at: /opt/homebrew/opt/python@3.14/bin/python3.14
Creating virtual environment at: .venv
Resolved 35 packages in 3ms
Installed 24 packages in 23ms
 + alembic==1.19.1
 + annotated-doc==0.0.5
 + annotated-types==0.8.0
 + anyio==4.14.2
 + click==8.5.0
 + fastapi==0.141.1
 + h11==0.16.0
 + httptools==0.8.0
 + idna==3.19
 + mako==1.4.1
 + markupsafe==3.0.3
 + psycopg2-binary==2.9.12
 + pydantic==2.13.4
 + pydantic-core==2.46.4
 + python-dotenv==1.2.3
 + pyyaml==6.0.3
 + sqlalchemy==2.0.52
 + starlette==1.6.0
 + typing-extensions==4.16.0
 + typing-inspection==0.4.4
 + uvicorn==0.52.4
 + uvloop==0.22.1
 + watchfiles==1.2.0
 + websockets==17.1
```


## Step 3: Create and Customize a .env File

```bash
cp env.example .env
```

This sets up docker to run postgres on a local port 5433.  If you
are already using this port you will get a collision on startup.

Check the notes in .env for customization you may require.

If you attempt to run multiple versions of this project you
will need to customize the values of:

```
  PG_PORT
  ADMINER_PORT
  DATABASE_CONTAINER_NAME
  ADMINER_CONTAINER_NAME
```


## Step 4: Start the Docker Postgres Instance

Run:

``bash
make up
```
You should see something like this:

```bash
% make up
docker compose up -d
[+] up 4/4
 ✔ Network alembic-crm_local-alembic-net Created      0.0s
 ✔ Volume alembic-crm_pgdata             Created      0.0s
 ✔ Container alembic-postgres            Started      0.1s
 ✔ Container alembic-adminer             Started      0.2s
docker ps
CONTAINER ID   IMAGE               COMMAND                  CREATED                  STATUS                  PORTS                     NAMES
cde83ea1d490   adminer             "entrypoint.sh docke…"   Less than a second ago   Up Less than a second   127.0.0.1:8081->8080/tcp  alembic-adminer
170b08f4d38a   postgres:18-vector  "docker-entrypoint.s…"   Less than a second ago   Up Less than a second   127.0.0.1:5433->5432/tcp  alembic-postgres
```

Once the database is up you can connect as postgres, the DB superuser
role and inspect the instance as show in the transcript below using
'make connect-su':

```bash
% make connect-su
psql -h 127.0.0.1 -p 5433 -U postgres
psql (18.6, server 18.4 (Debian 18.4-1.pgdg13+1))
Type "help" for help.

postgres=# \l
                                                    List of databases
   Name    |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | Locale | ICU Rules |   Access privileges   
-----------+----------+----------+-----------------+------------+------------+--------+-----------+-----------------------
 postgres  | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | 
 template0 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
 template1 | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
           |          |          |                 |            |            |        |           | postgres=CTc/postgres
(3 rows)

postgres=# \du
                             List of roles
 Role name |                         Attributes                         
-----------+------------------------------------------------------------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
```


## Step 5: Initialize the Database

The intial 'docker compose up' will create a new postgres
instance which now needs to be configured.

The default postgres user password is contained in the .env
file.  You will need this for the setup.

```bash
make setup-user-role
```

You should see this:

```
% make setup-api-role

Setup api role and demo database...
set -a; . ./.env && \
	psql -h 127.0.0.1  -p 5433 -U postgres -f db/create/create_api_user.sql
CREATE ROLE
CREATE DATABASE
CREATE DATABASE
GRANT
GRANT
GRANT
GRANT
ALTER DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES
```

Now if you check the database you should see:

```bash
(alembic-crm) % make connect-su
psql -h 127.0.0.1 -p 5433 -U postgres
psql (18.6, server 18.4 (Debian 18.4-1.pgdg13+1))
Type "help" for help.

postgres=# \l
                                                      List of databases
     Name     |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | Locale | ICU Rules |   Access privileges   
--------------+----------+----------+-----------------+------------+------------+--------+-----------+-----------------------
 alembic_demo | api      | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =Tc/api              +
              |          |          |                 |            |            |        |           | api=CTc/api
 api          | api      | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | 
 postgres     | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | 
 template0    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
              |          |          |                 |            |            |        |           | postgres=CTc/postgres
 template1    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
              |          |          |                 |            |            |        |           | postgres=CTc/postgres
(5 rows)

postgres=# \du
                             List of roles
 Role name |                         Attributes                         
-----------+------------------------------------------------------------
 api       | 
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
```

The 'api' user/role now exists along with the 'api and 'alembic_demo'
databases.  You should now be able to connect as the 'api' user:

```bash
% make connect-api
psql -h 127.0.0.1 -p 5433 -U api -d alembic_demo
psql (18.6, server 18.4 (Debian 18.4-1.pgdg13+1))
Type "help" for help.

alembic_demo=> \d
Did not find any relations.
```

## Step 6: Now Use alembic to Initialize the Data

The alembic_demo database now exists - owned by 'api' but contains
no tables yet.  Let's use alembic to create the basic set of tables
and some starter data.


Run:

```base
alembic upgrade head
```

You should see:

```bash
% alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_set_when_modified, Install set_when_modified trigger function
INFO  [alembic.runtime.migration] Running upgrade 001_set_when_modified -> 002__install_api_credentials, Install api_credentials table
INFO  [alembic.runtime.migration] Running upgrade 002__install_api_credentials -> 003__install_instance_metadata, Install instance_metadata table
INFO  [alembic.runtime.migration] Running upgrade 003__install_instance_metadata -> 004__install_application_user, Install application_user table
INFO  [alembic.runtime.migration] Running upgrade 004__install_application_user -> 005__install_token_blacklist, Install token_blacklist table
INFO  [alembic.runtime.migration] Running upgrade 005__install_token_blacklist -> 006__install_login_session, Install login_session table
INFO  [alembic.runtime.migration] Running upgrade 006__install_login_session -> 007__install_audit_log, Install audit_log table
INFO  [alembic.runtime.migration] Running upgrade 007__install_audit_log -> 008__add_api_credentials_user, Add api credentials user
INFO  [alembic.runtime.migration] Running upgrade 008__add_api_credentials_user -> 009__add_admin_user, Add admin user
INFO  [alembic.runtime.migration] Running upgrade 009__add_admin_user -> 010__install_set_modified_at, Replace set_when_modified() with set_modified_at()
```

The various script files used by alembic to initilize the database
tables live in alembic/versions. These scripts reference SQL scripts
contained in db/create and db/data.

If you now check the database you should see:

```bash
% make connect-api
psql -h 127.0.0.1 -p 5433 -U api -d alembic_demo
psql (18.6, server 18.4 (Debian 18.4-1.pgdg13+1))
Type "help" for help.

alembic_demo=> \d
                  List of relations
 Schema |          Name           |   Type   | Owner 
--------+-------------------------+----------+-------
 public | alembic_version         | table    | api
 public | api_credentials         | table    | api
 public | api_credentials_id_seq  | sequence | api
 public | application_user        | table    | api
 public | application_user_id_seq | sequence | api
 public | audit_log               | table    | api
 public | audit_log_id_seq        | sequence | api
 public | instance_metadata       | table    | api
 public | login_session           | table    | api
 public | login_session_active    | view     | api
 public | login_session_id_seq    | sequence | api
 public | token_blacklist         | table    | api
(12 rows)

alembic_demo=> select * from api_credentials;
 id |              user_guid               |      email      |                         hashed_password                          |          created_at           
----+--------------------------------------+-----------------+------------------------------------------------------------------+-------------------------------
  1 | d2edb783-8349-4df2-a51e-aac1948ab147 | api@example.com | 6a078acf8050a3b1c19b5ddf78d76d09fd934dd6c4ac331be8a00784f202db00 | 2026-08-28 03:18:39.450095+00
(1 row)

alembic_demo=> select * from application_user;
 id |              user_guid               | username |                          password_hash                           |       email       | first_name | last_name | role  | is_active | notes | last_login |          created_at           |          modified_at          
----+--------------------------------------+----------+------------------------------------------------------------------+-------------------+------------+-----------+-------+-----------+-------+------------+-------------------------------+-------------------------------
  1 | 3b3fb7f6-1c39-452e-a5bb-262e58618ceb | admin    | a81b423e3b1afc6e915f934c7e364d4201c4ccb1df00e890e6eabc89b549a775 | admin@example.com | Admin      | User      | admin | t         |       |            | 2026-08-28 03:18:39.450095+00 | 2026-08-28 03:18:39.450095+00
(1 row)

alembic_demo=> \q
```


# Reinitializing the Database

If you want to start again or run into errors a couple of approaches are provided.

To do this you can either run 'make destroy':

```bash
% make destroy
docker compose down -v
[+] down 4/4
 ✔ Container alembic-adminer              Removed                                                                                                                                         0.1s
 ✔ Container alembic-postgres             Removed                                                                                                                                         0.2s
 ✔ Volume alembic-crm_pgdata             Removed                                                                                                                                         0.0s
 ✔ Network alembic-crm_local-alembic-net Removed        
```

and then re-apply the above steps.  The 'destroy' fires a 'docker
compose down -v' which stops the docker instance and removes all
its associated resources.

Alternatively, you can do a 'make reset'

This reset also removes the database but re-creates the 'api' role
and associated artefacts.  You would then need to re-run the 'alembic
upgrade head' to reinstall all the tables.

```bash
% make reset
Reset the docker environment
docker compose down -v --remove-orphans
[+] down 4/4
 ✔ Container alembic-adminer              Removed                                                                                                                                         0.1s
 ✔ Container alembic-postgres             Removed                                                                                                                                         0.1s
 ✔ Volume alembic-crm_pgdata             Removed                                                                                                                                         0.0s
 ✔ Network alembic-crm_local-alembic-net Removed                                                                                                                                         0.1s
sleep 1
docker compose up -d
[+] up 4/4
 ✔ Network alembic-crm_local-alembic-net Created                                                                                                                                         0.0s
 ✔ Volume alembic-crm_pgdata             Created                                                                                                                                         0.0s
 ✔ Container alembic-postgres             Started                                                                                                                                         0.1s
 ✔ Container alembic-adminer              Started                                                                                                                                         0.2s
Waiting for postgres.... now setup api role...

Setup api role and demo database...
set -a; . ./.env && \
	psql -h 127.0.0.1  -p 5433 -U postgres -f db/create/create_api_user.sql
CREATE ROLE
CREATE DATABASE
CREATE DATABASE
GRANT
GRANT
GRANT
GRANT
ALTER DEFAULT PRIVILEGES
ALTER DEFAULT PRIVILEGES
 ready...
```

There is also a drop-api-role make recipe which drops the 'api'
role/user after freeing or deleting attached database resources.


# Testing the Migrations

`make test-migrations` runs the whole migration chain against a throwaway Postgres container, so the database started by `make up` is left alone.
It upgrades one revision at a time and snapshots the schema and row counts after each step.
It then downgrades one revision at a time and checks that every step restores the snapshot taken on the way up.
Finally it upgrades from base to head in one go and compares the result with the stepwise upgrade.
At head it also checks that an UPDATE stamps `modified_at` on every table that has that column.

```bash
% make test-migrations
scripts/test_migrations.sh
Starting postgres:18 as alembic-crm-test-27203
Upgrading one revision at a time
  ok  up to   001_set_when_modified
  ...
  ok  up to   010__install_set_modified_at
Checking modified_at at head
    NOTICE:  ok application_user: modified_at stamped on 1 rows
    NOTICE:  ok instance_metadata: modified_at stamped on 1 rows
Downgrading one revision at a time
  ok  down to 009__add_admin_user
  ...
  ok  down to base
Upgrading base to head in one step
  ok  up to   010__install_set_modified_at
    NOTICE:  ok application_user: modified_at stamped on 1 rows
    NOTICE:  ok instance_metadata: modified_at stamped on 1 rows
PASS: 11 states, every upgrade and downgrade verified
```

Run it after adding or editing a revision.
GitHub Actions also runs it, via `.github/workflows/test-migrations.yml`, on pushes to `main` and on pull requests that touch the migrations or their tooling.
A downgrade error only shows up when someone downgrades, and this is the cheapest way to find it first.


# Notes

Check the doc/NOTES.md file for notes about the initial setup of this
project.

# Using Alembic

Use alembic downgrade with the target revision.

```bash
# See migration history
alembic history

# Revert one migration
alembic downgrade -1

# Revert to a specific revision
alembic downgrade <revision_id>

# Revert everything back to the initial base state
alembic downgrade base
```

Check the database’s current migration revision with:

```bash
alembic current
```

For example, if alembic history shows revision a1b2c3d4, run:

```bash
alembic downgrade a1b2c3d4
```


