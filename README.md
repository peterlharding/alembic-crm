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
cp setup/env.example .env
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

```bash
make up
```

You should see something like this:

```bash
% make up
docker compose up -d
 Network alembic-crm_crm-demo-net Created
 Volume alembic-crm_crm_db Created
 Container alembic-postgres Started
docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED                  STATUS                  PORTS                      NAMES
044fea8fdb0e   postgres:18   "docker-entrypoint.s…"   Less than a second ago   Up Less than a second   127.0.0.1:5433->5432/tcp   alembic-postgres
```

Adminer, a web UI for browsing the database, sits behind a compose profile and is not started by `make up`.
Start it with `docker compose --profile adminer up -d` and open `http://127.0.0.1:8433` (the `ADMINER_PORT` from `.env`).
`make down`, `make destroy` and `make reset` stop it along with postgres.

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
make setup-api-role
```

You should see this:

```
% make setup-api-role

Setup api role and demo database...
set -a; . ./.env && \
	psql -h 127.0.0.1  -p 5433 -U postgres -f db/sql/create_api_user.sql
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

```bash
alembic upgrade head
```

You should see:

```bash
% alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> API_001__DDL, Install trigger functions
INFO  [alembic.runtime.migration] Running upgrade API_001__DDL -> API_002__Credentials, Install api_credentials and token_blacklist tables
INFO  [alembic.runtime.migration] Running upgrade API_002__Credentials -> API_003__Utility_Tables, Install instance_metadata, audit_log and login_session tables
INFO  [alembic.runtime.migration] Running upgrade API_003__Utility_Tables -> CRM_001, Install application_user, access and user_role tables
INFO  [alembic.runtime.migration] Running upgrade CRM_001 -> CRM_002, Install task and event tables
INFO  [alembic.runtime.migration] Running upgrade CRM_002 -> CRM_003, Install document, note and attachment tables
INFO  [alembic.runtime.migration] Running upgrade CRM_003 -> CRM_004, Install contact and account tables
INFO  [alembic.runtime.migration] Running upgrade CRM_004 -> CRM_005, Install lead, opportunity and quote tables
INFO  [alembic.runtime.migration] Running upgrade CRM_005 -> CRM_006, Replace set_when_modified() with set_modified_at()
INFO  [alembic.runtime.migration] Running upgrade CRM_006 -> CRM_007, Install set_modified_at triggers on CRM tables
INFO  [alembic.runtime.migration] Running upgrade CRM_007 -> CRM_008, Load sample data
```

The revision scripts alembic runs live in `alembic/versions`.
Each one loads SQL scripts from `db/api` (trigger functions, credentials and utility tables) or `db/crm` (the CRM tables).
Run `alembic` from the repository root, because the revisions open those SQL files by relative path.

The last revision, `CRM_008`, loads one or two sample rows into every table from the `data` directories.
They tell one small story: two customer accounts with a contact each, an open lead and a converted one, and the opportunities, quotes, tasks, events, notes and documents that go with them.
The schema declares no foreign keys, so the `*_id` columns in the sample data rely on each table being empty when it is loaded and handing out ids 1 and 2.

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
 public | access                  | table    | api
 public | access_id_seq           | sequence | api
 public | account                 | table    | api
 public | account_id_seq          | sequence | api
 public | alembic_version         | table    | api
 public | api_credentials         | table    | api
 public | api_credentials_id_seq  | sequence | api
 public | application_user        | table    | api
 public | application_user_id_seq | sequence | api
 public | attachment              | table    | api
 public | attachment_id_seq       | sequence | api
 public | audit_log               | table    | api
 public | audit_log_id_seq        | sequence | api
 public | contact                 | table    | api
 public | contact_id_seq          | sequence | api
 public | document                | table    | api
 public | document_id_seq         | sequence | api
 public | event                   | table    | api
 public | event_id_seq            | sequence | api
 public | instance_metadata       | table    | api
 public | lead                    | table    | api
 public | lead_id_seq             | sequence | api
 public | login_session           | table    | api
 public | login_session_active    | view     | api
 public | login_session_id_seq    | sequence | api
 public | note                    | table    | api
 public | note_id_seq             | sequence | api
 public | opportunity             | table    | api
 public | opportunity_id_seq      | sequence | api
 public | quote                   | table    | api
 public | quote_id_seq            | sequence | api
 public | task                    | table    | api
 public | task_id_seq             | sequence | api
 public | token_blacklist         | table    | api
 public | user_role               | table    | api
 public | user_role_id_seq        | sequence | api
(36 rows)

alembic_demo=> select * from api_credentials;
 id |                 guid                 |      email      |                         hashed_password                          |          created_at           |          updated_at           
----+--------------------------------------+-----------------+------------------------------------------------------------------+-------------------------------+-------------------------------
  1 | d2edb783-8349-4df2-a51e-aac1948ab147 | api@example.com | 6a078acf8050a3b1c19b5ddf78d76d09fd934dd6c4ac331be8a00784f202db00 | 2026-09-15 10:35:11.335556+00 | 2026-09-15 10:35:11.335556+00
(1 row)

alembic_demo=> select * from instance_metadata;
 release | app_version | db_version |        notes         |          modified_at          
---------+-------------+------------+----------------------+-------------------------------
 dev     | v0.1.0      | v0.1.0     | Schema modernisation | 2026-09-15 10:35:11.335556+00
(1 row)

alembic_demo=> \q
```


# Reinitializing the Database

If you want to start again or run into errors a couple of approaches are provided.

To do this you can either run 'make destroy':

```bash
% make destroy
docker compose --profile adminer down -v
 Container alembic-postgres Removed
 Volume alembic-crm_crm_db Removed
 Network alembic-crm_crm-demo-net Removed
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
docker compose --profile adminer down -v --remove-orphans
 Container alembic-postgres Removed
 Volume alembic-crm_crm_db Removed
 Network alembic-crm_crm-demo-net Removed
sleep 1
docker compose up -d
 Network alembic-crm_crm-demo-net Created
 Volume alembic-crm_crm_db Created
 Container alembic-postgres Started
Waiting for postgres.... now setup api role...
make setup-api-role
Setup api role and demo database...
set -a; . ./.env && \
	psql -h 127.0.0.1  -p 5433 -U postgres -f db/sql/create_api_user.sql
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
At head it also checks that an UPDATE stamps `modified_at` on every table that has that column and at least one row.
It then checks that the SQLAlchemy models in `app/models` match the schema and can load every row (see below).

```bash
% make test-migrations
scripts/test_migrations.sh
Starting postgres:18 as alembic-demo-test-4255
Upgrading one revision at a time
  ok  up to   API_001__DDL
  ...
  ok  up to   CRM_008
Checking modified_at at head
    NOTICE:  ok attachment: modified_at stamped on 2 rows
    ...
    NOTICE:  ok user_role: modified_at stamped on 2 rows
Checking models against the schema at head
    ok  18 models match the database
    ok  Access: loaded 2 row(s)
    ...
    ok  UserRole: loaded 2 row(s)
Downgrading one revision at a time
  ok  down to CRM_007
  ...
  ok  down to base
Upgrading base to head in one step
  ok  up to   CRM_008
    NOTICE:  ok attachment: modified_at stamped on 2 rows
    ...
    NOTICE:  ok user_role: modified_at stamped on 2 rows
PASS: 12 states, every upgrade and downgrade verified
```

Without a `.env` (as in CI) the script reads `setup/env.example` instead.

Run it after adding or editing a revision.
GitHub Actions also runs it, via `.github/workflows/test-migrations.yml`, on pushes to `main` and on pull requests that touch the migrations or their tooling.
A downgrade error only shows up when someone downgrades, and this is the cheapest way to find it first.


# SQLAlchemy Models

`app/models` holds one SQLAlchemy 2.0 model per table, for use by an API.
The SQL files and the Alembic revisions still own the schema: the models mirror it and are never used to create or migrate it, which is why `alembic/env.py` has no `target_metadata`.

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Opportunity

engine = create_engine("postgresql+psycopg2://api:Much-More-Secret@127.0.0.1:5433/alembic_demo")

with Session(engine) as session:
    open_deals = session.scalars(select(Opportunity).where(Opportunity.is_closed.is_(False))).all()
```

`scripts/check_models.py` compares the models with a migrated database using Alembic's autogenerate comparison (tables, columns, types, nullability, server defaults, indexes and unique constraints) and then loads every row through each model.
`make test-migrations` runs it at head; to run it against your own database once it is at head:

```bash
uv run python scripts/check_models.py
```

If you change a table's SQL, update its model in the same change, or the check fails.


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


