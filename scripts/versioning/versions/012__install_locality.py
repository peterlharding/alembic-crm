
#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install locality table
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op

revision: str      = '012__install_locality'
down_revision: str = '011__install_iso_subdivision'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(open("db/create/locality.sql").read())


def downgrade() -> None:
    op.execute("DROP TABLE locality")

