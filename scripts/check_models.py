#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  Compare the SQLAlchemy models in app.models with a migrated database.

  Connects with the same DEMO_ROLE, DEMO_PASSWORD, PG_HOST, PG_PORT and DEMO_DB
  settings as alembic/env.py and prints every difference Alembic's
  autogenerate comparison finds, exiting 1 if there are any. Run it from the
  repository root against a database at head; make test-migrations does.
"""
# -----------------------------------------------------------------------------

import os
import re
import sys

from pathlib import Path
from typing import Any

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from dotenv import load_dotenv
from sqlalchemy import URL, DefaultClause, create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import Base  # noqa: E402


# -----------------------------------------------------------------------------

def is_null_default(diff: tuple) -> bool:
    # A varchar column declared DEFAULT NULL reflects as NULL::character
    # varying, which means the same as the model declaring no default at all.
    # This is filtered afterwards rather than through a compare_server_default
    # callable, because Alembic 1.19 crashes calling one for identity columns.
    if diff[0] != "modify_default":
        return False
    _, _, _, _, _, database, model = diff
    return model is None and isinstance(database, DefaultClause) and bool(re.fullmatch(r"NULL(::[\w ]+)?", str(database.arg)))


# -----------------------------------------------------------------------------

def significant(diffs: list) -> list:
    kept = []
    for diff in diffs:
        if isinstance(diff, list):
            diff = [item for item in diff if not is_null_default(item)]
            if diff:
                kept.append(diff)
        else:
            kept.append(diff)
    return kept


# -----------------------------------------------------------------------------

def show(value: Any) -> str:
    if isinstance(value, DefaultClause):
        return f"DEFAULT {value.arg}"
    return repr(value)


# -----------------------------------------------------------------------------

def describe(diff: Any) -> str:
    # Column changes arrive as a list of tuples, everything else as one tuple:
    #   ("modify_type", schema, table, column, existing, database, model)
    #   ("add_table", Table), ("remove_index", Index), ...
    if isinstance(diff, list):
        return "\n".join(describe(item) for item in diff)

    op = diff[0]

    if op.startswith("modify_"):
        _, _, table, column, _, database, model = diff
        return f"  {op:<16} {table}.{column}: database {show(database)}, model {show(model)}"

    return f"  {op:<16} {', '.join(show(item) for item in diff[1:])}"


# -----------------------------------------------------------------------------

def main() -> int:
    load_dotenv()

    url = URL.create(
        "postgresql+psycopg2",
        username=os.environ["DEMO_ROLE"],
        password=os.environ["DEMO_PASSWORD"],
        host=os.environ["PG_HOST"],
        port=int(os.environ["PG_PORT"]),
        database=os.environ["DEMO_DB"],
    )

    engine = create_engine(url)

    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={"compare_type": True, "compare_server_default": True},
        )
        diffs = significant(compare_metadata(context, Base.metadata))

    tables = len(Base.metadata.tables)

    if diffs:
        engine.dispose()
        print(f"FAIL: {len(diffs)} difference(s) between {tables} models and the database")
        print("  (add_* means only the models have it, remove_* means only the database has it)")
        for diff in diffs:
            print(describe(diff))
        return 1

    print(f"ok  {tables} models match the database")

    # Load every row through the ORM, so type handling and mapper setup are
    # exercised as well as the table definitions.
    with Session(engine) as session:
        for mapper in sorted(Base.registry.mappers, key=lambda m: m.class_.__name__):
            rows = session.scalars(select(mapper.class_)).all()
            print(f"ok  {mapper.class_.__name__}: loaded {len(rows)} row(s)")

    engine.dispose()
    return 0


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())


# -----------------------------------------------------------------------------
