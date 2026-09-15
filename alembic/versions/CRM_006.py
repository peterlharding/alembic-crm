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

revision: str      = 'CRM_006'
down_revision: str = 'CRM_005'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------
# set_when_modified() assigns NEW.when_modified, a column no table has, so
# every UPDATE on instance_metadata failed. Its column is modified_at, and
# API_001 already installs set_modified_at().

TABLES = ("instance_metadata",)


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
    for table in TABLES:
        op.execute(f"DROP TRIGGER {table}_set_when_modified ON public.{table}")
        create_trigger(table, "set_modified_at")
    op.execute("DROP FUNCTION public.set_when_modified()")


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute(open("db/api/ddl/set_when_modified.sql").read())
    for table in TABLES:
        op.execute(f"DROP TRIGGER {table}_set_modified_at ON public.{table}")
        create_trigger(table, "set_when_modified")


# -----------------------------------------------------------------------------
