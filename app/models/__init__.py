#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
"""
  SQLAlchemy models, one module per table.

  The schema is owned by the SQL files under db/ and the Alembic revisions
  that load them; these models mirror it and never create it.
  scripts/check_models.py compares them with a migrated database.
"""
# -----------------------------------------------------------------------------

from app.models.base import Base

from app.models.api_credentials import ApiCredentials
from app.models.audit_log import AuditLog
from app.models.instance_metadata import InstanceMetadata
from app.models.login_session import LoginSession
from app.models.token_blacklist import TokenBlacklist

from app.models.access import Access
from app.models.account import Account
from app.models.application_user import ApplicationUser
from app.models.attachment import Attachment
from app.models.contact import Contact
from app.models.document import Document
from app.models.event import Event
from app.models.lead import Lead
from app.models.note import Note
from app.models.opportunity import Opportunity
from app.models.quote import Quote
from app.models.task import Task
from app.models.user_role import UserRole


# -----------------------------------------------------------------------------

__all__ = [
    "Base",
    "ApiCredentials",
    "AuditLog",
    "InstanceMetadata",
    "LoginSession",
    "TokenBlacklist",
    "Access",
    "Account",
    "ApplicationUser",
    "Attachment",
    "Contact",
    "Document",
    "Event",
    "Lead",
    "Note",
    "Opportunity",
    "Quote",
    "Task",
    "UserRole",
]


# -----------------------------------------------------------------------------
