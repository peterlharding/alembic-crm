#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  token_blacklist - db/api/create/token_blacklist.sql
"""
# -----------------------------------------------------------------------------

import uuid

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Text, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# -----------------------------------------------------------------------------

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    jti:            Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    user_id:        Mapped[int]       = mapped_column(BigInteger)
    reason:         Mapped[str]       = mapped_column(Text, server_default=text("''"))
    expiry:         Mapped[datetime]  = mapped_column(DateTime(timezone=True))
    blacklisted_on: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("token_blacklist_expiry_idx", "expiry"),
        Index("token_blacklist_user_id_idx", "user_id"),
        # Mirrors COMMENT ON TABLE, including its U+2014 dash
        {"comment": "Revoked token IDs. Rows are deletable once expiry passes \u2014 the token fails validation anyway."},
    )


# -----------------------------------------------------------------------------
