#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install document, note and attachment tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_003'
down_revision: str = 'CRM_002'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/crm/create/document.sql").read())
    op.execute(open("db/crm/create/note.sql").read())
    op.execute(open("db/crm/create/attachment.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS document")
    op.execute("DROP TABLE IF EXISTS note")
    op.execute("DROP TABLE IF EXISTS attachment")


# -----------------------------------------------------------------------------

