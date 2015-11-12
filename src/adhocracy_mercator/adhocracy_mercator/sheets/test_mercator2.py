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

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


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


class TestPartnersSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import partners_meta
        return partners_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IPartners
        from adhocracy_mercator.sheets.mercator2 import PartnersSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IPartners
        assert inst.meta.schema_class == PartnersSchema

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        wanted = {'partner1_name': '',
                  'partner1_website': '',
                  'partner1_country': 'DE',
                  'partner2_name': '',
                  'partner2_website': '',
                  'partner2_country': 'DE',
                  'partner3_name': '',
                  'partner3_website': '',
                  'partner3_country': 'DE',
                  'other_partners': '',
                  'has_partners': False}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)

class TestTopicSchema:

    @fixture
    def meta(self):
        from .mercator2 import topic_meta
        return topic_meta

    @fixture
    def inst(self):
        from .mercator2 import TopicSchema
        return TopicSchema()

    @fixture
    def cstruct_required(self):
        return {'topic': 'urban_development'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'topic': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'topic': 'urban_development'}

class TestTopicSheet:

    @fixture
    def meta(self):
        from adhocracy_mercator.sheets.mercator2 import topic_meta
        return topic_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        from adhocracy_mercator.sheets.mercator2 import TopicSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ITopic
        assert inst.meta.schema_class == TopicSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestDurationSchema:

    @fixture
    def meta(self):
        from .mercator2 import duration_meta
        return duration_meta

    @fixture
    def inst(self):
        from .mercator2 import DurationSchema
        return DurationSchema()

    @fixture
    def cstruct_required(self):
        return {'duration': '6'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'duration': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
            {'duration': 6}


class TestDurationSheet:

    @fixture
    def meta(self):
        from .mercator2 import duration_meta
        return duration_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import IDuration
        from adhocracy_mercator.sheets.mercator2 import DurationSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == IDuration
        assert inst.meta.schema_class == DurationSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestLocationSchema:

    @fixture
    def meta(self):
        from .mercator2 import location_meta
        return location_meta

    @fixture
    def inst(self):
        from .mercator2 import LocationSchema
        return LocationSchema()

    @fixture
    def cstruct_required(self):
        return {'city': 'Berlin',
                'country': 'DE',
                'has_link_to_ruhr': 'false',
                'link_to_ruhr': ''
        }

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'city': 'Required',
                                        'country': 'Required',
                                        'has_link_to_ruhr': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == \
              {'city': 'Berlin',
               'country': 'DE',
               'has_link_to_ruhr': False}

class TestLocationSheet:

    @fixture
    def meta(self):
        from .mercator2 import location_meta
        return location_meta

    @fixture
    def context(self):
        from adhocracy_core.interfaces import IItem
        return testing.DummyResource(__provides__=IItem)

    def test_create_valid(self, meta, context):
        from adhocracy_mercator.sheets.mercator2 import ILocation
        from adhocracy_mercator.sheets.mercator2 import LocationSchema
        inst = meta.sheet_class(meta, context)
        assert inst.meta.isheet == ILocation
        assert inst.meta.schema_class == LocationSchema

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestLocationSchema:

    @fixture
    def meta(self):
        from .mercator2 import status_meta
        return status_meta

    @fixture
    def inst(self):
        from .mercator2 import StatusSchema
        return StatusSchema()

    @fixture
    def cstruct_required(self):
        return {'status': 'other'}

    def test_deserialize_empty(self, inst):
        from colander import Invalid
        cstruct = {}
        with raises(Invalid) as error:
            inst.deserialize(cstruct)
        assert error.value.asdict() == {'status': 'Required'}

    def test_deserialize_with_required(self, inst, cstruct_required):
        wanted = cstruct_required
        assert inst.deserialize(cstruct_required) == {'status': 'other'}
