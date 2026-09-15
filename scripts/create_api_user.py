#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
Setup api user
"""
# -----------------------------------------------------------------------------

import os
import sys
import psycopg2

from contextlib import closing
from dotenv import load_dotenv
from psycopg2 import sql, errors
from sqlalchemy import URL


# -----------------------------------------------------------------------------

load_dotenv()

PG_HOST            = os.environ.get("PG_HOST", "127.0.0.1")
PG_PORT            = int(os.environ["PG_PORT"])

PG_ADMIN_USER      = os.environ["PG_ADMIN_USER"]
PG_ADMIN_PASSWORD  = os.environ["PG_ADMIN_PASSWORD"]

DEMO_ROLE          = os.environ["DEMO_ROLE"]
DEMO_PASSWORD      = os.environ["DEMO_PASSWORD"]
DEMO_DB            = os.environ["DEMO_DB"]

url = URL.create(
    "postgresql+psycopg2",
    username=DEMO_ROLE,
    password=DEMO_PASSWORD,
    host=PG_HOST,
    port=PG_PORT,
    database=DEMO_DB,
)

DATABASE_URL = url.render_as_string(hide_password=False)

print(f"DATABASE_URL |{DATABASE_URL}|")

# sys.exit(1)

role = sql.Identifier(DEMO_ROLE)
pw   = sql.Literal(DEMO_PASSWORD)
db   = sql.Identifier(DEMO_DB)

"""
statements = [
        sql.SQL("CREATE ROLE {role} WITH LOGIN PASSWORD {pw}").format(role=role, pw=pw),
        sql.SQL("GRANT CONNECT ON DATABASE {db} TO {role}").format(db=db, role=role),
        sql.SQL("GRANT USAGE ON SCHEMA public TO {role}").format(role=role),
        sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role}").format(role=role),
        sql.SQL("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}").format(role=role),
]

with psycopg2.connect(DATABASE_URL, autocommit=True) as conn:
    for stmt in statements:
        conn.execute(stmt)
"""


GRANTS = [
    sql.SQL("GRANT CONNECT ON DATABASE {db} TO {role}").format(db=db, role=role),
    sql.SQL("GRANT USAGE ON SCHEMA public TO {role}").format(role=role),
    sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {role}").format(role=role),
    sql.SQL("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role}").format(role=role),
    sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {role}").format(role=role),
    sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {role}").format(role=role),
]


# -----------------------------------------------------------------------------

def main() -> int:
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_ADMIN_USER,
        password=PG_ADMIN_PASSWORD,
    )

    conn.autocommit = True

    with closing(conn), conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (DEMO_ROLE,))

        exists = cur.fetchone() is not None

        if exists:
            print(f"role {DEMO_ROLE!r} already exists; updating password")
            cur.execute(sql.SQL("ALTER ROLE {role} WITH LOGIN PASSWORD {pw}").format(role=role, pw=pw))
        else:
            print(f"creating role {DEMO_ROLE!r}")
            cur.execute(sql.SQL("CREATE ROLE {role} WITH LOGIN PASSWORD {pw}").format( role=role, pw=pw))

        try:
            cur.execute(sql.SQL("CREATE DATABASE {db} OWNER {role}").format(db=db, role=role))
            print(f"created database {DEMO_DB!r}")
        except errors.DuplicateDatabase:
            print(f"database {DEMO_DB!r} already exists")


        for stmt in GRANTS:
            cur.execute(stmt)

    print(f"granted {DEMO_ROLE!r} read/write on {DEMO_DB}.public")

    return 0


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())


# -----------------------------------------------------------------------------

