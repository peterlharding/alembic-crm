#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  Install trigger functions
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str = 'API_001__DDL'
down_revision: Union[str, None] = None

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/api/ddl/set_modified_at.sql").read())
    op.execute(open("db/api/ddl/set_when_modified.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS set_when_modified")
    op.execute("DROP FUNCTION IF EXISTS set_modified_at")


# -----------------------------------------------------------------------------

