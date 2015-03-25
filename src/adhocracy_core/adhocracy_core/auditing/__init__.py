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
        # TODO: how big should the log size be?
        auditlog = AuditLog(max_layers=100000, layer_size=1000)
        root['auditlog'] = auditlog
