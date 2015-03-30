"""Auditlog of events stored in a ZODB database."""
import transaction
import json

from substanced.util import get_auditlog
from BTrees.OOBTree import OOBTree
from datetime import datetime
from logging import getLogger
from collections import namedtuple

logger = getLogger(__name__)

AuditEntry = namedtuple('AuditEntry', ['name', 'oid', 'payload'])


class AuditLog(OOBTree):

    """An Auditlog composed of entries."""

    def add(self, name, oid, **kw):
        """ Add a record the audit log.

        ``_name`` should be the event name,
        ``_oid`` should be an object oid or ``None``, and ``kw`` should be a
        json-serializable dictionary.
        """
        payload = json.dumps(kw)
        self[datetime.utcnow()] = AuditEntry(name, oid, payload)


def _set_auditlog(context):
    """Set an auditlog for the context."""
    conn = context._p_jar
    try:
        auditconn = conn.get_connection('audit')
    except KeyError:
        return
    root = auditconn.root()
    if 'auditlog' not in root:
        auditlog = AuditLog()
        root['auditlog'] = auditlog


def _get_auditlog(context):
    auditlog = get_auditlog(context)
    if auditlog is None:
        _set_auditlog(context)
        transaction.commit()
        logger.info('Auditlog created')
        return get_auditlog(context)
    return auditlog


def log_auditevent(context, name, oid=None, **kw):
    """Add a an audit entry to the audit database.

    The audit database is created if missing. If the zodbconn.uri.audit
    value is not specified in the config, auditing does not happen.
    """
    auditlog = _get_auditlog(context)
    if auditlog is not None:
        auditlog.add(name, oid, **kw)
