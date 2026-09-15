#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  api_credentials - db/api/create/api_credentials.sql
"""
# -----------------------------------------------------------------------------

import uuid

from datetime import datetime

from sqlalchemy import DateTime, Identity, Integer, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# -----------------------------------------------------------------------------

class ApiCredentials(Base):
    __tablename__ = "api_credentials"

    id:              Mapped[int]       = mapped_column(Integer, Identity(always=True), primary_key=True)
    guid:            Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, server_default=text("gen_random_uuid()"))
    email:           Mapped[str]       = mapped_column(String(128), unique=True)
    hashed_password: Mapped[str]       = mapped_column(String(128))
    created_at:      Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:      Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())


# -----------------------------------------------------------------------------
