import transaction
import json

from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from pyramid import testing
from . import log_auditevent
from . import get_auditlog


@fixture()
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.changelog')


def _get_event_name(index):
    return 'event_{}'.format(index)


def _get_payload_value1(index):
    return 'value1_{}'.format(index)


@fixture
def context(context):
    mocked_conn = Mock()
    mocked_auditconn = Mock()
    mocked_auditconn.root.return_value = {}
    mocked_conn.get_connection.return_value = mocked_auditconn
    context._p_jar = mocked_conn
    return context


@mark.usefixtures('integration')
def test_add_changelog(registry):
    assert hasattr(registry, 'changelog')


@fixture()
def request_(registry):
    assert hasattr(registry, 'changelog')
    request = testing.DummyResource(registry=registry)
    return request


def test_add_events(context):
    nb_events = 10000

    for idx in range(nb_events):
        log_auditevent(context,
                       _get_event_name(idx),
                       key1=_get_payload_value1(idx))
    transaction.commit()

    all_entries = get_auditlog(context).itervalues()
    assert len(list(all_entries)) == nb_events

    for i, entry in zip(range(nb_events), all_entries):
        event = entry[2]
        assert event.name == _get_event_name(i)
        expected_payload \
            = json.dumps(['key1', _get_payload_value1(idx)])
        assert event.payload == expected_payload


def test_no_audit_connection_adding_entry(context):
    context._p_jar.get_connection \
        = Mock(name='method', side_effect=KeyError('audit'))

    log_auditevent(context, 'eventName')

    assert get_auditlog(context) is None


def test_auditlog_already_exits(context):
    from . import _set_auditlog

    _set_auditlog(context)
    auditlog1 = get_auditlog(context)

    _set_auditlog(context)
    auditlog2 = get_auditlog(context)

    assert auditlog1 == auditlog2


@mark.usefixtures('integration')
def test_audit_changes_callback_empty_changelog(context, registry, request_):
    from . import audit_changes_callback
    request_.registry = registry
    request_.context = context

    response = Mock()
    audit_changes_callback(request_, response)

    all_entries = get_auditlog(context).values()
    assert len(all_entries) == 0
