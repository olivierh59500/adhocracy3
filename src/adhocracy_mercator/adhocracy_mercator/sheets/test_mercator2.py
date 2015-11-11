from datetime import datetime
from datetime import timedelta

from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises


class TestUserInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import userinfo_meta
        return userinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator2 import IUserInfo
        from adhocracy_mercator.sheets.mercator2 import UserInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IUserInfo
        assert inst.meta.schema_class == UserInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'first_name': '',
                  'last_name': '',
                  }
        assert inst.get() == wanted


class TestOrganizationInfoSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import organizationinfo_meta
        return organizationinfo_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        from adhocracy_mercator.sheets.mercator2 import IOrganizationInfo
        from adhocracy_mercator.sheets.mercator2 import OrganizationInfoSchema
        inst = meta.sheet_class(meta, context)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)
        assert inst.meta.isheet == IOrganizationInfo
        assert inst.meta.schema_class == OrganizationInfoSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'name': '',
                  'city': '',
                  'country': 'DE',
                  'help_request': '',
                  'registration_date': None,
                  'website': '',
                  'contact_email': '',
                  'status': 'other',
                  'status_other': '',
                  }
        assert inst.get() == wanted


class TestOrganizationInfoSchema:

    @fixture
    def meta(self):
        from .mercator2 import organizationinfo_meta
        return organizationinfo_meta

    @fixture
    def inst(self):
        from adhocracy_mercator.sheets.mercator2 import OrganizationInfoSchema
        return OrganizationInfoSchema()

    @fixture
    def cstruct_required(self):
        return {'country': 'DE',
                'name': 'Name',
                'status': 'planned_nonprofit',
                'contact_email': 'anna@example.com',
                'registration_date': '2015-02-18T14:17:24+00:00',
                'city': 'Berlin',
                }

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'city': 'Required',
                                        'contact_email': 'Required',
                                        'country': 'Required',
                                        'name': 'Required',
                                        'registration_date': 'Required',
                                        'status': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        from pytz import UTC
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'country': 'DE',
             'name': 'Name',
             'status': 'planned_nonprofit',
             'contact_email': 'anna@example.com',
             'registration_date': datetime(2015, 2, 18,
                                           14, 17, 24, 0, tzinfo=UTC),
             'city': 'Berlin',
            }

    def test_deserialize_with_status_other_and_no_description(
            self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'other'
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status_other':
                                        'Required iff status == other'}

    def test_deserialize_with_status_support_needed_and_no_help_request(
            self, inst, cstruct_required):
        from colander import Invalid
        cstruct = cstruct_required
        cstruct['status'] = 'support_needed'
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'help_request':
                                        'Required iff status == support_needed'}

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


@mark.usefixtures('integration')
class TestIncludeme:

    def test_includeme_register_organizationinfo_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IOrganizationInfo
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IOrganizationInfo)
        assert get_sheet(context, IOrganizationInfo)

        # TODO other types
