#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install application_user, access and user_role tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_001'
down_revision: str = 'API_003__Utility_Tables'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/crm/create/application_user.sql").read())
    op.execute(open("db/crm/create/access.sql").read())
    op.execute(open("db/crm/create/user_role.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_role")
    op.execute("DROP TABLE IF EXISTS access")
    op.execute("DROP TABLE IF EXISTS application_user")


# -----------------------------------------------------------------------------

