#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install api_credentials table
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op

revision:      str = 'API_002__Credentials'
down_revision: str = 'API_001__DDL'

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/api/create/api_credentials.sql").read())
    op.execute(open("db/api/create/token_blacklist.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS token_blacklist")
    op.execute("DROP TABLE IF EXISTS api_credentials")


# -----------------------------------------------------------------------------


