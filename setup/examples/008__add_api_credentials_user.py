#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Add api credentials user
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = '008__add_api_credentials_user'
down_revision: str = '007__install_audit_log'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/data/api_credentials.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("TRUNCATE api_credentials")


# -----------------------------------------------------------------------------

