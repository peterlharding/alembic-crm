#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install lead, opportunity and quote tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_005'
down_revision: str = 'CRM_004'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/crm/create/lead.sql").read())
    op.execute(open("db/crm/create/opportunity.sql").read())
    op.execute(open("db/crm/create/quote.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS quote")
    op.execute("DROP TABLE IF EXISTS opportunity")
    op.execute("DROP TABLE IF EXISTS lead")


# -----------------------------------------------------------------------------

