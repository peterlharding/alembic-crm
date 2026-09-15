#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  Load sample data
"""
# -----------------------------------------------------------------------------

from typing import Sequence, Union
from alembic import op


# -----------------------------------------------------------------------------

revision: str      = 'CRM_008'
down_revision: str = 'CRM_007'

branch_labels: Union[str, Sequence[str], None] = None
depends_on:    Union[str, Sequence[str], None] = None


# -----------------------------------------------------------------------------
# One or two rows per table that has no seed yet. api_credentials and
# instance_metadata are seeded by their create scripts in API_002 and API_003.
#
# The *_id columns in the seeds assume each table is empty when loaded, so its
# rows get ids 1 and 2; see the header of each file.

SEEDS = (
    "db/crm/data/user_role.sql",
    "db/crm/data/application_user.sql",
    "db/crm/data/account.sql",
    "db/crm/data/contact.sql",
    "db/crm/data/lead.sql",
    "db/crm/data/opportunity.sql",
    "db/crm/data/quote.sql",
    "db/crm/data/task.sql",
    "db/crm/data/event.sql",
    "db/crm/data/note.sql",
    "db/crm/data/document.sql",
    "db/crm/data/attachment.sql",
    "db/crm/data/access.sql",
    "db/api/data/audit_log.sql",
    "db/api/data/login_session.sql",
    "db/api/data/token_blacklist.sql",
)


# -----------------------------------------------------------------------------

def upgrade() -> None:
    for path in SEEDS:
        op.execute(open(path).read())


# -----------------------------------------------------------------------------

def downgrade() -> None:
    # RESTART IDENTITY so a re-upgrade hands out ids 1 and 2 again.
    tables = ", ".join(path.rsplit("/", 1)[1].removesuffix(".sql") for path in reversed(SEEDS))
    op.execute(f"TRUNCATE {tables} RESTART IDENTITY")


# -----------------------------------------------------------------------------
