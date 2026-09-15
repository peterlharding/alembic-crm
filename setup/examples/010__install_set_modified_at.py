#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  Replace set_when_modified() with set_modified_at()
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = '010__install_set_modified_at'
down_revision: str = '009__add_admin_user'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------
# set_when_modified() assigned NEW.when_modified, a column no table has, so
# every UPDATE on these tables failed. Their column is modified_at.

TABLES = ("application_user", "instance_metadata")


# -----------------------------------------------------------------------------

def create_trigger(table: str, function: str) -> None:
    op.execute(f"""
        CREATE TRIGGER {table}_{function}
            BEFORE UPDATE ON public.{table}
            FOR EACH ROW
            WHEN (OLD.* IS DISTINCT FROM NEW.*)
            EXECUTE FUNCTION public.{function}()
    """)


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/create/set_modified_at.sql").read())
    for table in TABLES:
        op.execute(f"DROP TRIGGER {table}_set_when_modified ON public.{table}")
        create_trigger(table, "set_modified_at")
    op.execute("DROP FUNCTION public.set_when_modified()")


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute(open("db/create/set_when_modified.sql").read())
    for table in TABLES:
        op.execute(f"DROP TRIGGER {table}_set_modified_at ON public.{table}")
        create_trigger(table, "set_when_modified")
    op.execute("DROP FUNCTION public.set_modified_at()")


# -----------------------------------------------------------------------------
