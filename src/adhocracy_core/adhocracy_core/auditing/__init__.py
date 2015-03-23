"""Auditlog of events stored in a ZODB database."""
import transaction
import json

from pyramid.traversal import resource_path
from substanced.util import get_auditlog
from BTrees.OOBTree import OOBTree
from datetime import datetime
from logging import getLogger
from collections import namedtuple
from adhocracy_core.utils import get_user
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.utils import get_sheet_field
from pyramid_zodbconn import get_connection


logger = getLogger(__name__)

AuditEntry = namedtuple('AuditEntry', ['name', 'payload'])

RESOURCE_CREATED = 'resourceCreated'
RESOURCE_MODIFIED = 'resourceModified'


class AuditLog(OOBTree):

    """An Auditlog composed of entries."""

    def add(self, name, **kw):
        """ Add a record the audit log.

        ``_name`` should be the event name,
        ``_oid`` should be an object oid or ``None``, and ``kw`` should be a
        json-serializable dictionary.
        """
        payload = json.dumps(kw)
        self[datetime.utcnow()] = AuditEntry(name, payload)


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


def log_auditevent(context, name, **kw):
    """Add a an audit entry to the audit database.

    The audit database is created if missing. If the zodbconn.uri.audit
    value is not specified in the config, auditing does not happen.
    """
    auditlog = _get_auditlog(context)
    if auditlog is not None:
        auditlog.add(name, **kw)


def audit_changes_callback(request, response):
    """Add audit entries to the auditlog when the data is changed."""
    registry = request.registry
    changelog_metadata = registry.changelog.values()
    if len(changelog_metadata) == 0:
        return

    connection = get_connection(request)
    root = connection.root()
    user = get_user(request)
    user_name = get_sheet_field(user, IUserBasic, 'name')
    user_path = resource_path(user)

    for meta in changelog_metadata:
        path = resource_path(meta.resource)
        if meta.created:
            log_auditevent(root,
                           RESOURCE_CREATED,
                           resource_path=path,
                           user_name=user_name,
                           user_path=user_path)
        elif meta.modified:
            log_auditevent(root,
                           RESOURCE_MODIFIED,
                           resource_path=path,
                           user_name=user_name,
                           user_path=user_path)
        # else: log visibility changes?
        transaction.commit()
