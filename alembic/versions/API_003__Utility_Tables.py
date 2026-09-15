#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install instance_metadata, audit_log and session_log tables
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'API_003__Utility_Tables'
down_revision: str = 'API_002__Credentials'

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/api/create/instance_metadata.sql").read())
    op.execute(open("db/api/create/audit_log.sql").read())
    op.execute(open("db/api/create/login_session.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS login_session")
    op.execute("DROP TABLE IF EXISTS audit_log")
    op.execute("DROP TABLE IF EXISTS instance_metadata")


# -----------------------------------------------------------------------------

