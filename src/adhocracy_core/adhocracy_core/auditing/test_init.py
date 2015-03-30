import transaction
import json

from unittest.mock import Mock
from pytest import fixture
from substanced.util import get_auditlog
from . import log_auditevent


class TestAuditlog:

    def _get_event_name(self, index):
        return 'event_{}'.format(index)

    def _get_payload_value1(self, index):
        return 'value1_{}'.format(index)

    @fixture
    def context(self, context):
        mocked_conn = Mock()
        mocked_auditconn = Mock()
        mocked_auditconn.root.return_value = {}
        mocked_conn.get_connection.return_value = mocked_auditconn
        context._p_jar = mocked_conn
        return context

    def test_add_events(self, context):
        nb_events = 10000

        for idx in range(nb_events):
            log_auditevent(context,
                           self._get_event_name(idx),
                           None,
                           key1=self._get_payload_value1(idx))
        transaction.commit()

        all_entries = get_auditlog(context).itervalues()
        assert len(list(all_entries)) == nb_events

        for i, entry in zip(range(nb_events), all_entries):
            event = entry[2]
            assert event.name == self._get_event_name(i)
            expected_payload \
                = json.dumps(['key1', self._get_payload_value1(idx)])
            assert event.payload == expected_payload

    def test_no_audit_connection_adding_entry(self, context):
        context._p_jar.get_connection \
            = Mock(name='method', side_effect=KeyError('audit'))

        log_auditevent(context, 'eventName')

        assert get_auditlog(context) is None

    def test_auditlog_already_exits(self, context):
        from . import _set_auditlog

        _set_auditlog(context)
        auditlog1 = get_auditlog(context)

        _set_auditlog(context)
        auditlog2 = get_auditlog(context)

        assert auditlog1 == auditlog2
