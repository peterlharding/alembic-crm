
#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install iso_subdivision table
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op

revision: str      = '011__install_iso_subdivision'
down_revision: str = '010__install_iso_country'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(open("db/create/iso_subdivision.sql").read())


def downgrade() -> None:
    op.execute("DROP TABLE iso_subdivision")

