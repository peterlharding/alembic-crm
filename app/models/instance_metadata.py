#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  instance_metadata - db/api/create/instance_metadata.sql
"""
# -----------------------------------------------------------------------------

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# -----------------------------------------------------------------------------

class InstanceMetadata(Base):
    __tablename__ = "instance_metadata"

    release:     Mapped[str]      = mapped_column(Text)
    app_version: Mapped[str]      = mapped_column(Text)
    db_version:  Mapped[str]      = mapped_column(Text)
    notes:       Mapped[str]      = mapped_column(Text, server_default=text("''"))
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("release IN ('dev', 'test', 'staging', 'prod')", name="instance_metadata_release_check"),
        CheckConstraint(r"app_version ~ '^v\d+\.\d+\.\d+$'", name="instance_metadata_app_version_check"),
        CheckConstraint(r"db_version ~ '^v\d+\.\d+\.\d+$'", name="instance_metadata_db_version_check"),
        # At most one row
        Index("instance_metadata_singleton", text("(true)"), unique=True),
    )

    # The table has no primary key; the singleton index makes any column
    # unique, and the ORM needs one to identify the row.
    __mapper_args__ = {"primary_key": [release]}


# -----------------------------------------------------------------------------
