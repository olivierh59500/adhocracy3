import unittest
import transaction
from unittest.mock import Mock
from pyramid import testing
from substanced.util import get_auditlog

from adhocracy_core.auditing import set_auditlog


class AuditlogTest(unittest.TestCase):

    def _make_mocked_connection(self):
        mocked_connection = Mock()
        mocked_auditconn = Mock()
        mocked_auditconn.root.return_value = {}
        mocked_connection.get_connection.return_value = mocked_auditconn
        return mocked_connection

    def _get_event_name(self, index):
        return 'event_{}'.format(index)

    def setUp(self):
        self.context = testing.DummyResource()
        self.context._p_jar = self._make_mocked_connection()

    def test_add_events(self):
        set_auditlog(self.context)
        auditlog = get_auditlog(self.context)
        nb_events = 100000
        events_name = [self._get_event_name(i) for i in range(nb_events)]

        for name in events_name:
            auditlog.add(name, None)
        transaction.commit()

        all_entries = auditlog.get_all_entries()
        assert len(list(all_entries)) == nb_events

        for i, entry in zip(range(nb_events), all_entries):
            event = entry[2]
            assert event.name == self._get_event_name(i)

    def test_no_audit_connection(self):
        self.context._p_jar.get_connection \
            = Mock(name='method', side_effect=KeyError('audit'))
        set_auditlog(self.context)

        assert get_auditlog(self.context) is None

    def test_auditlog_already_exits(self):
        set_auditlog(self.context)
        auditlog1 = get_auditlog(self.context)

        set_auditlog(self.context)
        auditlog2 = get_auditlog(self.context)

        assert auditlog1 == auditlog2
