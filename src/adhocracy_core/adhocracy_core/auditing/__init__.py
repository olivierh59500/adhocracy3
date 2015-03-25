"""Auditlog of events stored in a ZODB database."""
import substanced.audit


class AuditLog(substanced.audit.AuditLog):
    """An Auditlog composed of layered entries."""

    def __init__(self, max_layers=10000, layer_size=100, entries=None):
        super().__init__(max_layers, layer_size, entries)

    def get_all_entries(self):
        """Get all the entries in the Auditlog."""
        return self.newer(-1, -1)


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
