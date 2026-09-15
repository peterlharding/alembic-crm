#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  application_user - db/crm/create/application_user.sql

  This is the CRM table installed by CRM_001, not the unused
  db/api/create/application_user.sql.
"""
# -----------------------------------------------------------------------------

import uuid

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Identity, Integer, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


# -----------------------------------------------------------------------------

class ApplicationUser(Base):
    __tablename__ = "application_user"

    id:                         Mapped[int]              = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    guid:                       Mapped[uuid.UUID | None] = mapped_column(Uuid)

    username:                   Mapped[str | None]       = mapped_column(String(32))
    hashed_password:            Mapped[str | None]       = mapped_column(String(255))
    alias:                      Mapped[str | None]       = mapped_column(String(32))

    first_name:                 Mapped[str | None]       = mapped_column(String(32))
    last_name:                  Mapped[str | None]       = mapped_column(String(32))

    company_name:               Mapped[str | None]       = mapped_column(String(100))
    division:                   Mapped[str | None]       = mapped_column(String(32))
    department:                 Mapped[str | None]       = mapped_column(String(100))
    title:                      Mapped[str | None]       = mapped_column(String(100))

    street:                     Mapped[str | None]       = mapped_column(String(100))
    city:                       Mapped[str | None]       = mapped_column(String(50))
    state:                      Mapped[str | None]       = mapped_column(String(32))
    postal_code:                Mapped[str | None]       = mapped_column(String(20))
    country:                    Mapped[str | None]       = mapped_column(String(100))

    email:                      Mapped[str | None]       = mapped_column(String(255), unique=True)
    phone:                      Mapped[str | None]       = mapped_column(String(20))
    phone_extension:            Mapped[str | None]       = mapped_column(String(10))
    fax:                        Mapped[str | None]       = mapped_column(String(20))
    mobile_phone:               Mapped[str | None]       = mapped_column(String(20))

    is_active:                  Mapped[bool | None]      = mapped_column(Boolean, server_default=text("true"))

    user_role_id:               Mapped[int | None]       = mapped_column(BigInteger)
    user_type:                  Mapped[str | None]       = mapped_column(String(20), server_default=text("'Standard'"))
    profile_id:                 Mapped[int | None]       = mapped_column(BigInteger)

    timezone_sid_key:           Mapped[str | None]       = mapped_column(String(32), server_default=text("'Australia/Melbourne'"))

    locale_sid_key:             Mapped[str | None]       = mapped_column(String(32), server_default=text("'en_AU'"))
    language_locale_key:        Mapped[str | None]       = mapped_column(String(32), server_default=text("'en_US'"))

    receives_info_emails:       Mapped[bool | None]      = mapped_column(Boolean, server_default=text("false"))
    receives_admin_info_emails: Mapped[bool | None]      = mapped_column(Boolean, server_default=text("false"))
    email_encoding_key:         Mapped[str | None]       = mapped_column(String(32), server_default=text("'ISO-8859-1'"))

    employee_number:            Mapped[str | None]       = mapped_column(String(50))
    delegated_approver_id:      Mapped[int | None]       = mapped_column(BigInteger)

    start_day:                  Mapped[int | None]       = mapped_column(Integer, server_default=text("6"))
    end_day:                    Mapped[int | None]       = mapped_column(Integer, server_default=text("23"))

    last_login_date:            Mapped[datetime | None]  = mapped_column(DateTime(timezone=True))

    created_at:                 Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by_id:              Mapped[int | None]       = mapped_column(BigInteger)
    updated_at:                 Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_by_id:              Mapped[int | None]       = mapped_column(BigInteger)


# -----------------------------------------------------------------------------
