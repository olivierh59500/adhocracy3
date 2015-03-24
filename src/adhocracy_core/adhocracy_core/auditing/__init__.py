"""Auditlog of events stored in a ZODB database."""
from substanced.audit import AuditLog


def set_auditlog(context):
    """Set an auditlog for the context."""
    conn = context._p_jar
    try:
        auditconn = conn.get_connection('audit')
    except KeyError:
        return
    root = auditconn.root()
    if 'auditlog' not in root:
        auditlog = AuditLog()  # TODO: increase log size
        root['auditlog'] = auditlog
