from pyramid import testing
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


class TestAuditlog:

    @fixture
    def inst(self):
        from . import AuditLog
        return AuditLog()

    def test_create(self, inst):
        from BTrees.OOBTree import OOBTree
        assert isinstance(inst, OOBTree)

    def test_add(self, inst):
        import datetime
        import json
        from . import AuditEntry
        appstruct = {'data': 1}
        inst.add('created', **appstruct)
        key, value = inst.items()[0]
        assert isinstance(key, datetime.datetime)
        assert isinstance(value, AuditEntry)
        assert value.name == 'created'
        assert value.payload == json.dumps(appstruct)
        # TODO Do we really want an arbitrary payload build from keywords?
        # NOTE: to have a proper unit test for the add method we could
        # mock the AuditLog object, but in this case its quite complicated


class TestSetAuditlog:
    """ TODO public function called from root factory"""


class TestGetAuditlog:
    """ not really needed, we could use substanced.util.get_auditlog for now"""


class TestAddAuditEvent:

    @fixture
    def user(self):
        return testing.DummyResource(__name__='user',
                                     name='name')
    @fixture
    def mock_auditlog(self):
        from . import AuditLog
        mock = Mock(spec=AuditLog)
        return mock

    @fixture
    def mock_get_auditlog(self, monkeypatch):
        from adhocracy_core import auditing
        monkeypatch.setattr(auditing, 'get_auditlog', Mock())
        return monkeypatch

    def call_fut(self, resource, action, user):
        from . import add_auditevent
        return add_auditevent(resource, action, user)

    def test_ignore_if_no_auditlog(self, context, user, mock_get_auditlog,
                                   mock_auditlog):
        mock_get_auditlog.return_value = None
        self.call_fut(context, 'created', user)
        assert mock_auditlog.add.called is False

    def test_add_if_auditlog(self, context, user, mock_get_auditlog,
                             mock_auditlog):
        mock_get_auditlog.return_value = mock_auditlog
        self.call_fut(context, 'created', user)
        assert mock_auditlog.add.called_with('/', 'created', 'name', '/user')

