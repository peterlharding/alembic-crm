#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install task and event tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_002'
down_revision: str = 'CRM_001'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/crm/create/task.sql").read())
    op.execute(open("db/crm/create/event.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS task")
    op.execute("DROP TABLE IF EXISTS event")


# -----------------------------------------------------------------------------

