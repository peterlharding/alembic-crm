# AGENTS.md

This file provides guidance to Codex (chatgpt.com/codex) when working with code in this repository.

## What This Repo Is

A teaching demo for managing a Postgres schema with Alembic, grown from `alembic-demo` into a CRM schema.
The README is a step-by-step walkthrough with real transcripts; keep them in step when changing revisions or recipes.
The deliverable is the migration chain plus the tooling that stands up the database around it.

`app/models/` holds SQLAlchemy models for a FastAPI API that does not exist yet; model variants from another repo are due to be merged in, so expect them to change.
There are no unit tests: `make test-migrations` is the test suite, and GitHub Actions runs it (`.github/workflows/test-migrations.yml`) on pushes to `main` and on PRs touching migrations or their tooling.
`uv.lock` is deliberately gitignored (machines run different uv versions, which rewrite it), so CI runs plain `uv sync` from `pyproject.toml`; do not un-ignore it or reintroduce `--locked`.

`doc/NOTES.md` is setup history describing an older `001`/`002` chain and a flat `db/create/` layout; do not treat it as current.
`CLAUDE.md` at the repo root is the Claude Code copy of this file; update it alongside.

## Setup and Common Commands

`.env` is required by almost everything and is gitignored.
The template is `setup/env.example`, not the repo root: `cp setup/env.example .env`.
Change `PG_PORT`, `ADMINER_PORT`, `DATABASE_CONTAINER_NAME` and `ADMINER_CONTAINER_NAME` if another copy of the project is running.

```bash
uv sync                  # create/refresh .venv (Python >= 3.12)
make up                  # start postgres only; adminer is behind a compose profile
make setup-api-role      # create DEMO_ROLE, its personal database and DEMO_DB
alembic upgrade head     # apply all migrations; run from the repo root
```

| Command | Effect |
| --- | --- |
| `make chk-env` | echo the values the Makefile parsed out of `.env`, first stop when something is misconfigured |
| `make upgrade` / `make verify` / `make downgrade` | `alembic upgrade head` / `alembic current` / `alembic downgrade -1` |
| `make test-migrations` | run `scripts/test_migrations.sh` against a throwaway container |
| `make connect-api` / `make connect-su` | psql as `DEMO_ROLE` into `DEMO_DB` / as `postgres` |
| `make drop-api-role` | undo `setup-api-role`: drop `DEMO_DB`, the role's database and the role; a no-op if the role is absent |
| `make reset` | `down -v`, restart, wait for `pg_isready`, re-run `setup-api-role`; migrations still need re-applying |
| `make destroy` / `make down` / `make clean` | remove volume / stop containers / delete `.venv` |

`docker compose --profile adminer up -d` starts Adminer on `ADMINER_PORT`; the teardown recipes pass `--profile adminer` so they stop it too.
The psql recipes connect over TCP to `127.0.0.1:PG_PORT` and prompt for the password unless `~/.pgpass` or `PGPASSWORD` supplies it.

Working with a single revision: `alembic upgrade +1`, `alembic downgrade CRM_003`, `alembic history`, or `alembic upgrade CRM_002:CRM_003 --sql` for offline SQL (env.py still needs the `.env` variables).

### test_migrations.sh

It starts `postgres:$PG_VERSION` on a random port and runs `db/sql/create_api_user.sql` in it, then:
upgrades one revision at a time snapshotting `pg_dump --schema-only` plus per-table row counts, runs `db/test/check_modified_at.sql` and `scripts/check_models.py` at head, downgrades one step at a time diffing against each snapshot, and finally upgrades base to head in one go and diffs against the stepwise result.
The database from `make up` is not touched, and without `.env` it reads `setup/env.example`.
Overrides: `TEST_PG_IMAGE` (image), `ALEMBIC` (default `uv run --quiet alembic`) and `PYTHON` (default `uv run --quiet python`).

`check_modified_at.sql` exercises every table with a `modified_at` column and at least one row, so a seeded table without a `set_modified_at` trigger fails it.

## Architecture

### Migrations are thin wrappers around SQL files

Most revisions in `alembic/versions/` `op.execute(open("db/.../x.sql").read())` one or more DDL files, with a hand-written `downgrade()` that drops the objects by name in reverse order.

* **Run `alembic` from the repository root.** The `open()` paths are relative to the working directory.
* **The SQL owns the schema, not the models.** `alembic/env.py` keeps `target_metadata = None`, so `--autogenerate` is not used; a new table means writing DDL under `db/`, a revision that loads it, and a matching model in `app/models/`.
* **Downgrades are not true inverses.** Everything the SQL creates (views, functions, triggers, seed rows) must be undone explicitly; `API_003` drops `login_session_active` before `login_session` for this reason. Run `make test-migrations` after adding or editing a revision.
* **Treat applied SQL as history.** Existing databases are already at head, so fix a shipped object in a new revision (as `CRM_006` does) rather than editing the SQL an earlier revision loads.
* **Many create scripts start with `DROP TABLE IF EXISTS ... [CASCADE]`** and two include seed `INSERT`s (`api_credentials.sql`, `instance_metadata.sql`), so those rows live and die with the table; all other sample data comes from `CRM_008`.

The chain is strictly linear, and the revision id equals the filename stem, so `down_revision` names the previous file:

| Revision | Effect |
| --- | --- |
| `API_001__DDL` | `db/api/ddl/`: `set_modified_at()` and legacy `set_when_modified()` |
| `API_002__Credentials` | `api_credentials` (with a seed row), `token_blacklist` |
| `API_003__Utility_Tables` | `instance_metadata` (singleton, seeded), `audit_log`, `login_session` + `login_session_active` view |
| `CRM_001` | `db/crm/create/`: `application_user`, `access`, `user_role` |
| `CRM_002` - `CRM_005` | `task`, `event`; `document`, `note`, `attachment`; `contact`, `account`; `lead`, `opportunity`, `quote` |
| `CRM_006` | swaps `instance_metadata`'s trigger to `set_modified_at()` and drops `set_when_modified()`, which assigned to a nonexistent `when_modified` column |
| `CRM_007` | `set_modified_at` triggers on the nine CRM tables with a `modified_at` column |
| `CRM_008` | sample data: `db/crm/data/*.sql` plus `db/api/data/{audit_log,login_session,token_blacklist}.sql`; downgrade is one `TRUNCATE ... RESTART IDENTITY` |

New revisions continue the `CRM_00N` naming with `down_revision` set to the current head; `alembic heads` must report exactly one head or the test script fails.
Keep the docstring accurate, since `alembic upgrade` and `alembic history` print it.

### Two SQL styles

* **`db/api/`** follows the modern conventions: identity PKs, `uuid` business key, `text` + named `CHECK` constraints, `timestamptz`, and a `BEFORE UPDATE ... WHEN (OLD.* IS DISTINCT FROM NEW.*)` trigger calling `public.set_modified_at()`.
  New tables should use this style and that function.
* **`db/crm/`** is a port of a Salesforce-like schema: `varchar(n)` everywhere, no FKs, no constraints, and a mix of `modified_at`/`modified_by_id` and `updated_at`/`updated_by_id` audit columns.
  Only the `modified_at` tables get a trigger (`CRM_007`); `account`, `application_user`, `contact` and `api_credentials` use `updated_at`, which nothing maintains.
  Figures such as `opportunity.amount` are `varchar`, and `event` keeps Salesforce-style `varchar(18)` references (`guid`, `who_ref`, `account_id`, `owner_id`).

There are two `application_user` definitions: `db/api/create/application_user.sql` (modern, with trigger and admin seed) is loaded by no revision; `CRM_001` installs the CRM version.

### Sample data

One or two rows per table, forming one story (two accounts, their contacts, an open and a converted lead, opportunities, quotes and activities).
With no FKs declared, `*_id` columns hard-code ids 1 and 2 and assume each table is empty when `CRM_008` loads it; each file's header says what its ids point at.
Adding a row or a seeded table means keeping those references consistent and adding the file to `CRM_008`'s `SEEDS` (or a new revision).
A database that already has rows in a seeded table (for example `application_user` loaded by hand) will fail `CRM_008` on a unique constraint and roll back.

### SQLAlchemy models

`app/models/` has one SQLAlchemy 2.0 declarative model per table (`Mapped[...]`/`mapped_column`), re-exported from `app/models/__init__.py`, sharing `Base` from `base.py`.
They mirror the DDL exactly, including `Identity(always=True)`, `server_default`s, varchar lengths, named constraints and indexes; the `login_session_active` view is not mapped.
`instance_metadata` has no primary key in the database, so its model sets `__mapper_args__ = {"primary_key": [release]}` instead of declaring one.

`scripts/check_models.py` runs Alembic's `compare_metadata` (types, nullability, server defaults, indexes, unique constraints and table comments, but not CHECK constraints) against a database at head, then loads every row through each model.
It drops `DEFAULT NULL::<type>` versus no-default differences in a post-filter, because Alembic 1.19 crashes when a `compare_server_default` callable meets an identity column.
Run it with `uv run python scripts/check_models.py` against any database at head; a SQL change without the matching model change fails `make test-migrations`.

### Files no migration loads

* `db/api/data/api_credentials.sql` and `db/api/data/application_user.sql` (the api-style user, which does not fit the CRM table) are unused seeds.
* `setup/examples/008`-`010` are revisions from the old chain kept as examples, with old ids and paths; `009` shows an FK-safe seed downgrade.
* `scripts/versioning/versions/` holds generated geo revisions (`iso_country`, `iso_subdivision`, `locality`) with old-chain ids; the `gen.py` that produced them is not in this repo.
* `db/sql/create_demo_db.sql`, run by `scripts/create_demo_db.sh` via `docker exec`, is an idempotent alternative to `create_api_user.sql`.
* `db/sql/grant_all.sql` references roles unrelated to this project; `db/Makefile` hardcodes `crm_demo`.

### Configuration flows from .env three ways

* **Alembic:** `alembic/env.py` calls `load_dotenv()` and copies `DEMO_ROLE`, `DEMO_PASSWORD`, `PG_HOST`, `PG_PORT` and `DEMO_DB` via `os.environ[key]` into the section so `sqlalchemy.url` in `alembic.ini` can interpolate them; a missing key is a `KeyError` before anything runs.
* **psql:** `db/sql/create_api_user.sql` and `drop_api_user.sql` read `DEMO_*` with `\getenv`, hence `set -a; . ./.env` in those Makefile recipes.
* **Makefile:** greps `.env` at parse time, so keep it to plain `KEY=value` lines with no quotes or spaces around `=`; command-line overrides such as `make PG_PORT=5499 setup-api-role` win.

### Two privilege levels

Role and database creation runs outside Alembic as the postgres superuser (`setup-api-role`, `scripts/create_demo_db.sh`, or `scripts/create_api_user.py` as a psycopg2 equivalent).
Alembic connects as `DEMO_ROLE`, which owns `DEMO_DB`, so migrations cannot create roles or databases and a fresh container needs the role setup before `alembic upgrade` can connect.

`scripts/gen_credentials.py` and `scripts/chk_passwd.py` generate and check the unsalted sha256 password hashes used in the seed data.
