
#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Install iso_country table
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op

revision: str      = '010__install_iso_country'
down_revision: str = '009__add_admin_user'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(open("db/create/iso_country.sql").read())


def downgrade() -> None:
    op.execute("DROP TABLE iso_country")

