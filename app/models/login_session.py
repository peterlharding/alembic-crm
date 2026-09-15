#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  login_session - db/api/create/login_session.sql

  The login_session_active view (unrevoked, unexpired rows) is not mapped.
"""
# -----------------------------------------------------------------------------

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Identity,
    Index,
    LargeBinary,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# -----------------------------------------------------------------------------

class LoginSession(Base):
    __tablename__ = "login_session"

    id:                 Mapped[int]             = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    session_token_hash: Mapped[bytes]           = mapped_column(LargeBinary)
    user_id:            Mapped[int]             = mapped_column(BigInteger)
    workstation:        Mapped[str | None]      = mapped_column(Text)
    ip_address:         Mapped[str | None]      = mapped_column(INET)
    user_agent:         Mapped[str | None]      = mapped_column(Text)
    data:               Mapped[dict[str, Any]]  = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    started:            Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen:          Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at:         Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=text("now() + interval '12 hours'"))
    revoked_at:         Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("session_token_hash", name="login_session_token_key"),
        CheckConstraint("expires_at > started", name="login_session_expiry_check"),
        CheckConstraint("jsonb_typeof(data) = 'object'", name="login_session_data_object"),
        Index("login_session_user_id_idx", "user_id"),
        Index("login_session_expires_at_idx", "expires_at"),
    )


# -----------------------------------------------------------------------------
