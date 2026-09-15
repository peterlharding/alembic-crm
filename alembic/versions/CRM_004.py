#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install contact and account tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_004'
down_revision: str = 'CRM_003'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/crm/create/contact.sql").read())
    op.execute(open("db/crm/create/account.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS account")
    op.execute("DROP TABLE IF EXISTS contact")


# -----------------------------------------------------------------------------

