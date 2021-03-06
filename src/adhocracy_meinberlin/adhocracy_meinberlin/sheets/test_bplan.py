import colander
from pyramid import testing
from pytest import mark
from pytest import fixture
from pytest import raises


class TestProposalSheet:

    @fixture
    def meta(self):
        from .bplan import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import sheets
        assert meta.isheet == sheets.bplan.IProposal
        assert meta.schema_class == sheets.bplan.ProposalSchema

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        wanted = {'name': '',
                  'street_number': '',
                  'postal_code_city': '',
                  'email': '',
                  'statement': '',
                  }
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, registry, meta):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestProposalSchema:

    @fixture
    def inst(self):
        from .bplan import ProposalSchema
        return ProposalSchema()

    @fixture
    def cstruct_required(self):
        cstruct = {'name': 'name',
                   'street_number': 'y',
                   'postal_code': '12',
                   'statement': 'statement'
                   }
        return cstruct

    def test_create(self, inst):
        import colander
        assert inst['name'].required
        assert inst['street_number'].required
        assert inst['postal_code_city'].required
        assert isinstance(inst['email'].validator, colander.Email)
        assert inst['statement'].required

    def test_deserialize_raise_if_wrong_email(self, inst, cstruct_required):
        cstruct_required['email'] = 'wrong'
        with raises(colander.Invalid):
            inst.deserialize()


class TestProcessSettingsSheet:

    @fixture
    def meta(self):
        from .bplan import process_settings_meta
        return process_settings_meta

    def test_meta(self, meta):
        from . import bplan
        assert meta.isheet == bplan.IProcessSettings
        assert meta.schema_class == bplan.ProcessSettingsSchema
        assert meta.create_mandatory is True

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context, registry):
        inst = meta.sheet_class(meta, context, None)
        wanted = {'plan_number': '',
                  'participation_kind': ''}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestProcessPrivateSettingsSheet:

    @fixture
    def meta(self):
        from .bplan import process_private_settings_meta
        return process_private_settings_meta

    def test_meta(self, meta):
        from . import bplan
        assert meta.isheet == bplan.IProcessPrivateSettings
        assert meta.schema_class == bplan.ProcessPrivateSettingsSchema
        assert meta.permission_view == 'view_bplan_private_settings'

    def test_create(self, meta, context):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IResourceSheet
        inst = meta.sheet_class(meta, context, None)
        assert IResourceSheet.providedBy(inst)
        assert verifyObject(IResourceSheet, inst)

    @mark.usefixtures('integration')
    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        wanted = {'office_worker_email': ''}
        assert inst.get() == wanted

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)
