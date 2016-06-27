from pytest import mark
from pytest import fixture


class TestProposal:

    @fixture
    def meta(self):
        from .bplan import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import resources
        assert meta.iresource == resources.bplan.IProposal
        assert meta.element_types == (resources.bplan.IProposalVersion,)
        assert meta.item_type == resources.bplan.IProposalVersion
        assert meta.permission_create == 'create_proposal'
        assert meta.use_autonaming
        assert meta.autonaming_prefix == 'proposal_'
        assert meta.default_workflow == 'bplan_private'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestProposalVersion:

    @fixture
    def meta(self):
        from .bplan import proposal_version_meta
        return proposal_version_meta

    def test_meta(self, meta):
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource == resources.bplan.IProposalVersion
        assert meta.extended_sheets == \
               (sheets.bplan.IProposal,
               )
        assert meta.permission_create == 'edit'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestProcess:

    @fixture
    def meta(self):
        from .bplan import process_meta
        return process_meta

    def test_meta(self, meta):
        from adhocracy_core.resources.process import IProcess
        from adhocracy_core.sheets.embed import IEmbed
        from adhocracy_core.sheets.image import IImageReference
        from adhocracy_meinberlin import sheets
        from adhocracy_meinberlin import resources
        assert meta.iresource is resources.bplan.IProcess
        assert resources.bplan.IProcess.isOrExtends(IProcess)
        assert meta.is_implicit_addable is True
        assert meta.permission_create == 'create_process'
        assert meta.extended_sheets == (sheets.bplan.IProcessSettings,
                                        sheets.bplan.IProcessPrivateSettings,
                                        IEmbed,
                                        IImageReference,
                                        )
        assert meta.permission_create == 'create_process'
        assert meta.default_workflow == 'bplan'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


