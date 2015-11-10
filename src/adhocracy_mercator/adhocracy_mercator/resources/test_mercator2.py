from pytest import fixture
from pytest import mark

class TestMercatorProposal:

    @fixture
    def meta(self):
        from .mercator2 import proposal_meta
        return proposal_meta

    def test_meta(self, meta):
        import adhocracy_mercator.sheets.mercator2
        from adhocracy_mercator.resources import mercator2
        from adhocracy_core.resources.comment import add_commentsservice
        from adhocracy_core.resources.rate import add_ratesservice
        from adhocracy_core.resources.logbook import add_logbook_service
        from adhocracy_core.sheets.badge import IBadgeable
        assert meta.iresource == mercator2.IMercatorProposal
        # assert meta.element_types == (mercator.IMercatorProposalVersion,
        #                               mercator.IOrganizationInfo,
        #                               mercator.IIntroduction,
        #                               mercator.IDescription,
        #                               mercator.ILocation,
        #                               mercator.IStory,
        #                               mercator.IOutcome,
        #                               mercator.ISteps,
        #                               mercator.IValue,
        #                               mercator.IPartners,
        #                               mercator.IFinance,
        #                               mercator.IExperience,
        #                               )
        assert meta.extended_sheets == \
            (adhocracy_mercator.sheets.mercator2.IUserInfo,)
        assert meta.is_implicit_addable
        assert add_ratesservice in meta.after_creation
        assert add_commentsservice in meta.after_creation
        assert add_logbook_service in meta.after_creation

    @mark.usefixtures('integration')
    def test_create(self, pool, meta, registry):
        res = registry.content.create(meta.iresource.__identifier__,
                                      parent=pool,
                                      )
        assert meta.iresource.providedBy(res)

class TestProcess:

    @fixture
    def meta(self):
        from .mercator2 import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources.process
        from adhocracy_core.resources.asset import add_assets_service
        from .mercator2 import IProcess
        from .mercator2 import IMercatorProposal
        assert meta.iresource is IProcess
        assert IProcess.isOrExtends(adhocracy_core.resources.process.IProcess)
        assert meta.element_types == (IMercatorProposal,)
        # TODO specify workflow
        # assert meta.workflow_name == 'mercator'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        res = registry.content.create(meta.iresource.__identifier__)
        assert meta.iresource.providedBy(res)
