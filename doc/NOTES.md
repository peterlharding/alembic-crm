
# Initial Prompt

I have created a guthub.com repo -

  git@github.com:peterlharding/alembic-demo.git

which I have cloned into /u/src/fastapi/alembic-demo.

The db/create sub-directory has a number of SQL scripts for creating
tables.

I want to setup a Python alembic configuration to for version 1
install the api_credentials.sql, token_blacklist.sql and
instance_metadata.sqltables and then for version 2 install the
application_user.sql, audit_log.sql and login_session.sql tables.

I have created a database, 'alembic_demo' in a local Postgres
instance (psql -h 127.0.0.1 -U api -d alembic_demo) - 'api'user
password is 'Projects-2026'.  Postgres password is 'Secret'.

---

# Now Add a pyproject.toml File

I want to create a pyproject.toml file for this repo.  Also I use
'uv' for package management and so will use 'uv sync' to create and
update a venv.

---

# Original Setup

This is an overview of the steps to use alembic to setup and manage
data in a Postgres database

## Step 1: Install Alembic

This is the process before adding a pyproject.toml file which will
allow 'uv sync' to manage packages

```bash
cd /u/src/fastapi/alembic-demo
uv pip install alembic
```

## Step 2: Initialize Alembic


```bash
alembic init alembic
```

This creates:

* alembic.ini — configuration file
* alembic/ directory with env.py, script.py.mako, and versions/

## Step 3: Configure alembic.ini

Edit alembic.ini and update the ini_section under [alembic]:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+psql://api:xxxx@127.0.0.1/alembic_demo
```

## Step 4: Create Migration Scripts

The following are examples from early in the development of this project.
Check the alembic/versions directory for the current mix.

### Version 1: alembic/versions/001_install_initial_tables.py

```python
"""install api_credentials, token_blacklist, and instance_metadata

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-01 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Install API credentials, token blacklist, and instance metadata tables."""
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/api_credentials.sql').read())
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/token_blacklist.sql').read())
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/instance_metadata.sql').read())


def downgrade() -> None:
    """Drop tables in reverse order."""
    op.execute("DROP TABLE IF EXISTS instance_metadata")
    op.execute("DROP TABLE IF EXISTS token_blacklist")
    op.execute("DROP TABLE IF EXISTS api_credentials")
```

### Version 2: alembic/versions/002_install_app_tables.py

``` python
"""install application_user, audit_log, and login_session tables

Revision ID: 002_app_tables
Revises: 001_initial
Create Date: 2026-01-01 00:00:00.000000
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers
revision: str = '002_app_tables'
down_revision: str = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Install application user, audit log, and login session tables."""
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/application_user.sql').read())
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/audit_log.sql').read())
    op.execute(open('/u/src/fastapi/alembic-demo/db/create/login_session.sql').read())


def downgrade() -> None:
    """Drop tables in reverse order."""
    op.execute("DROP TABLE IF EXISTS login_session")
    op.execute("DROP TABLE IF EXISTS audit_log")
    op.execute("DROP TABLE IF EXISTS application_user")
```

### Step 5: Run the Migrations

```bash
# Apply all migrations
alembic upgrade head

# Verify current version
alembic current

# To rollback one version
alembic downgrade -1
```

# Summary

| Alembic Version | Tables Created |
| --------------- | -------------- |
| v1 (001_initial) | api_credentials, token_blacklist, instance_metadata |
| v2 (002_app_tables) | application_user, audit_log, login_session |

If the SQL scripts use schema names or IF NOT EXISTS clauses, you
may need to adjust the downgrade() functions accordingly. Let me
know if you'd like help inspecting or modifying the actual SQL
files!


