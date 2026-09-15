# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A teaching demo for managing a Postgres schema with Alembic.
The README is a step-by-step walkthrough; `doc/NOTES.md` records the original setup history.

Despite the repo path and the `fastapi`/`uvicorn` dependencies in `pyproject.toml`, there is no application code, no ORM models and no unit tests.
`make test-migrations` is the test suite: it exercises every upgrade and downgrade against a throwaway container.
GitHub Actions runs it (`.github/workflows/test-migrations.yml`) on pushes to `main` and on pull requests that touch migrations or their tooling; without a `.env` the script falls back to `env.example`.
The deliverable is the migration chain plus the tooling that stands up the database around it.

### Branches

* `base-schema` carries the base schema, revisions 001 to 009.
* `main` adds revision 010, which replaces the broken `set_when_modified()` trigger function with `set_modified_at()`.
* `add-geo` branched before that and adds revisions 010 to 012 and the geographic reference tables, and is the branch to develop the geo work on.
  Its revision numbers collide with `main`: when it is rebased, the geo revisions become 011 to 013 and the first one's `down_revision` must point at `010__install_set_modified_at`.

The branches also differ in `docker-compose.yaml`: `add-geo` requests the `postgres:${PG_VERSION}-vector` image, `main` uses plain `postgres:${PG_VERSION}` because the vector image was not available when the project was tried on Windows.
Check which branch is out before diagnosing an image pull failure.

## Setup and Common Commands

`.env` is required by almost everything and is gitignored.
Create it first with `cp env.example .env`, then customize `PG_PORT`, `ADMINER_PORT`, `DATABASE_CONTAINER_NAME` and `ADMINER_CONTAINER_NAME` if another copy of this project is already running.

```bash
uv sync                  # create/refresh .venv (Python >= 3.12)
make up                  # start postgres + adminer containers
make setup-api-role      # create the api role and the alembic_demo database
alembic upgrade head     # apply all migrations
```

Other recipes:

| Command | Effect |
| --- | --- |
| `make chk-env` | echo the values parsed out of `.env`, first stop when something is misconfigured |
| `make verify` | `alembic current` |
| `make downgrade` | roll back one revision |
| `make test-migrations` | step every revision up and down in a throwaway container, checking each downgrade restores the previous schema and row counts |
| `make connect-api` | psql as the demo role into the demo database |
| `make connect-su` | psql as the postgres superuser |
| `make reset` | tear down volumes, restart, wait for readiness, re-run `setup-api-role`; migrations still need re-applying |
| `make destroy` | `docker compose down -v`, removes the volume |
| `make down` / `make clean` | stop containers / delete `.venv` |

Adminer is published on `ADMINER_PORT` (8433 in the example env).

## Architecture

### Migrations are thin wrappers around SQL files

Every revision in `alembic/versions/` is hand-written and does one thing:

```python
def upgrade() -> None:
    op.execute(open("db/create/api_credentials.sql").read())

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS api_credentials")
```

Consequences that matter when editing this repo:

* **Always run `alembic` from the repository root.**
  Those `open()` paths are relative to the process working directory, not to the migration file.
* **`--autogenerate` is useless here.**
  `alembic/env.py` sets `target_metadata = None` because there are no SQLAlchemy models.
  Adding a table means writing the DDL in `db/create/` and hand-writing the revision that reads it.
* **`downgrade()` is written by hand and is not a true inverse.**
  Schema revisions drop the object by name; data revisions `TRUNCATE`.
  Run `make test-migrations` when adding a revision, since an error here is invisible until someone downgrades.
  Revisions 010 to 012 on `add-geo` are currently wrong in exactly this way, see below.

The chain is strictly linear and the revision id equals the filename stem (`002__install_api_credentials`), so `down_revision` reads as the previous filename.
Revisions 001 to 007 install the base schema, 008 and 009 seed data from `db/data/`, and 010 replaces the `modified_at` trigger function.
On `add-geo`, 010 to 012 install the geographic tables instead.

### Generating new revisions

`scripts/versioning/gen.py` is the scaffolder.
Edit its `VERSION`, `last_revision_name`, `last_revision_command` and `TODO` list, run it from inside `scripts/versioning/`, and it writes one revision per table in `TODO` into `scripts/versioning/versions/`.
That output directory is deliberately gitignored by `scripts/versioning/.gitignore`; the generated files are reviewed and then copied into `alembic/versions/`.

**`gen.py` has an off-by-one in the generated `downgrade()`.**
It emits `last_revision_command`, which is the drop statement for the *previous* table rather than the one the revision just created.
The committed 010 to 012 carry the resulting bug: 010 truncates `application_user`, 011 drops `iso_country`, 012 drops `iso_subdivision`, and nothing drops `locality`.
Fix the generator and the three revisions together, otherwise regenerating reintroduces it.

### Configuration flows from .env in two different ways

* **Alembic:** `alembic/env.py` calls `load_dotenv()`, then pushes `DEMO_ROLE`, `DEMO_PASSWORD`, `PG_HOST`, `PG_PORT` and `DEMO_DB` into the alembic config section so the `sqlalchemy.url` template in `alembic.ini` can interpolate them.
  It reads them with `os.environ[key]`, so a missing variable is a `KeyError` before any migration runs.
* **psql scripts:** `db/create/create_api_user.sql` pulls the same values with `\getenv`, which is why the Makefile prefixes that recipe with `set -a; . ./.env`.

The Makefile itself parses `.env` a third way, by grepping it, so keep the file to plain `KEY=value` lines without quoting or spaces around `=`.

### Two privilege levels

Role and database creation happens outside Alembic, as the postgres superuser, via `make setup-api-role`.
Alembic then connects as `DEMO_ROLE` (`api`), which owns the demo database.
So a migration cannot create roles or databases, and a fresh container needs `setup-api-role` before `upgrade head` will connect at all.

## The SQL Layer

### db/create/ conventions

Application tables use `GENERATED ALWAYS AS IDENTITY` primary keys, a `uuid` business key defaulting to `gen_random_uuid()`, `timestamptz` audit columns, `text` plus `CHECK` rather than `varchar(n)`, named `CONSTRAINT` clauses, and a `BEFORE UPDATE ... WHEN (OLD.* IS DISTINCT FROM NEW.*)` trigger calling the shared `public.set_modified_at()` function installed by revision 010.
Audit columns are spelled `created_at` and `modified_at`.

Revision 001 originally installed `set_when_modified()`, which assigns to `NEW.when_modified`.
No table has that column, so every UPDATE on `application_user` and `instance_metadata` failed with `record "new" has no field "when_modified"`.
Revision 010 swaps both triggers over to `set_modified_at()` and drops the old function.
`set_when_modified.sql` and the old trigger definitions in `application_user.sql` and `instance_metadata.sql` stay as they are, because revisions 001, 003 and 004 still load them; new tables should call `set_modified_at()`.
`db/test/check_modified_at.sql`, run by `make test-migrations`, catches a trigger that does not stamp the column.

### Reference data naming

The `iso_` prefix marks tables whose content is externally standardised, leaving application-defined tables unprefixed.
This is why `state` became `iso_subdivision` (ISO 3166-2) while `city` became `locality`, which is not an ISO concept.
`db/create/refactored.sql` is the design document that argues these choices, including an OPEN QUESTIONS section.
It is a standalone reference and no migration executes it.

The geo tables are keyed for reference data rather than for an application: `iso_country` uses the two-letter code as a natural primary key, and `locality` reaches `iso_subdivision` through a composite `(country_code, subdivision_code)` foreign key so the pair is validated together.

### db/data/ seeds

`api_credentials.sql` and `application_user.sql` are loaded by revisions 008 and 009.

The geographic seeds are not wired into any migration yet.
`iso_country.sql`, `iso_subdivision.sql` and `locality.sql` match the current table names, while `state.sql` and `city.sql` are the pre-rename versions kept for reference.
Loading the geo data needs new revisions 013 onward.

## scripts/

Standalone helpers, not imported by anything: `gen_credentials.py` (generate and sha256-hash a password), `chk_passwd.py` (hash a given password to compare against a stored value), `create_api_user.py` (a psycopg2 equivalent of the `setup-api-role` recipe).
`versioning/gen.py` is covered above.
