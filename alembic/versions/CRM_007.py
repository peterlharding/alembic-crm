#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  Install set_modified_at triggers on CRM tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_007'
down_revision: str = 'CRM_006'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------
# The CRM tables with a modified_at column had nothing maintaining it. The
# tables using updated_at (account, application_user, contact) are left alone.

TABLES = (
    "attachment",
    "document",
    "event",
    "lead",
    "note",
    "opportunity",
    "quote",
    "task",
    "user_role",
)


# -----------------------------------------------------------------------------

def upgrade() -> None:
    for table in TABLES:
        op.execute(f"""
            CREATE TRIGGER {table}_set_modified_at
                BEFORE UPDATE ON public.{table}
                FOR EACH ROW
                WHEN (OLD.* IS DISTINCT FROM NEW.*)
                EXECUTE FUNCTION public.set_modified_at()
        """)


# -----------------------------------------------------------------------------

def downgrade() -> None:
    for table in reversed(TABLES):
        op.execute(f"DROP TRIGGER {table}_set_modified_at ON public.{table}")


# -----------------------------------------------------------------------------
