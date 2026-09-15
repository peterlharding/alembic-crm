#!/usr/bin/env python
# 
# -----------------------------------------------------------------------------
"""
  Add admin user
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = '009__add_admin_user'
down_revision: str = '008__add_api_credentials_user'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------

def upgrade() -> None:
    op.execute(open("db/data/application_user.sql").read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    # TRUNCATE is refused because token_blacklist and login_session reference
    # application_user. Delete only the seeded row; their ON DELETE CASCADE
    # removes its dependents. Then rewind the identity so a re-upgrade reuses
    # the same id, which is what RESTART IDENTITY was meant to achieve.
    op.execute("DELETE FROM application_user WHERE user_guid = '3b3fb7f6-1c39-452e-a5bb-262e58618ceb'")
    op.execute(
        "SELECT setval(pg_get_serial_sequence('application_user', 'id'), "
        "COALESCE(MAX(id), 0) + 1, false) FROM application_user"
    )


# -----------------------------------------------------------------------------

