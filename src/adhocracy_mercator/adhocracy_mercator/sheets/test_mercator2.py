from pyramid import testing
from pytest import fixture
from pytest import mark


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

@mark.usefixtures('integration')
class TestIncludeme:

    def test_includeme_register_organizationinfo_sheet(self, config):
        from adhocracy_mercator.sheets.mercator import IOrganizationInfo
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=IOrganizationInfo)
        assert get_sheet(context, IOrganizationInfo)
