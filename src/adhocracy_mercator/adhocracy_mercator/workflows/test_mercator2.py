from pyramid import testing
from pytest import mark
from pytest import fixture
from webtest import TestResponse

from adhocracy_core.utils.testing import add_resources
from adhocracy_core.utils.testing import do_transition_to

@fixture
def integration(config):
    config.include('adhocracy_core.events')
    config.include('adhocracy_core.content')
    config.include('adhocracy_mercator.workflows')


@mark.usefixtures('integration')
def test_initiate_and_transition_to_announce(registry, context):
    workflow = registry.content.workflows['mercator']
    request = testing.DummyRequest()
    assert workflow.state_of(context) is None
    workflow.initialize(context)
    assert workflow.state_of(context) is 'draft'
    workflow.transition_to_state(context, request, 'announce')
    assert workflow.state_of(context) is 'announce'
    workflow.transition_to_state(context, request, 'participate')
    assert workflow.state_of(context) is 'participate'
    workflow.transition_to_state(context, request, 'evaluate')
    assert workflow.state_of(context) is 'evaluate'
    workflow.transition_to_state(context, request, 'result')
    assert workflow.state_of(context) is 'result'


@fixture(scope='class')
def app_anonymous(app_anonymous):
    app_anonymous.base_path = '/'
    return app_anonymous

@fixture(scope='class')
def app_participant(app_participant):
    app_participant.base_path = '/'
    return app_participant


@fixture(scope='class')
def app_god(app_god):
    app_god.base_path = '/'
    return app_god

@fixture(scope='class')
def app_initiator(app_initiator):
    app_initiator.base_path = '/'
    return app_initiator

def _post_proposal(app_user, path='/') -> TestResponse:
    from adhocracy_mercator.resources.mercator2 import IMercatorProposal
    resp = app_user.post_resource(path, IMercatorProposal,   {})
    return resp

# todo refactor
def _post_comment_item(app_user, path='') -> TestResponse:
    from adhocracy_core.resources.comment import IComment
    resp = app_user.post_resource(path, IComment, {})
    return resp

def _post_document_item(app_user, path='/') -> TestResponse:
    from adhocracy_core.resources.document import IDocument
    resp = app_user.post_resource(path, IDocument, {})
    return resp


def _post_document_version(app_user, path='/') -> TestResponse:
    from adhocracy_core.resources.document import IDocumentVersion
    resp = app_user.post_resource(path, IDocumentVersion, {})
    return resp


def _batch_post_full_sample_proposal(app_user) -> TestResponse:
    subrequests = _create_proposal()
    resp = app_user.batch(subrequests)
    return resp


@mark.functional
class TestMercator2:

    @fixture
    def process_url(self):
        return '/organisation/advocate-europe2'

    @fixture
    def proposal0_url(self):
        return '/organisation/advocate-europe2/proposal_0000000'


    def test_create_resources(self,
                              registry,
                              datadir,
                              process_url,
                              app,
                              app_admin):
        json_file = str(datadir.join('resources.json'))
        add_resources(app, json_file)
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

    def test_set_participate_state(self, registry, app, process_url, app_admin):
        resp = app_admin.get(process_url)
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'announce')
        assert resp.status_code == 200

        resp = do_transition_to(app_admin,
                                process_url,
                                'participate')
        assert resp.status_code == 200

    def test_participate_participant_creates_proposal(self,
                                                      registry,
                                                      app,
                                                      process_url,
                                                      app_participant):
        resp = _post_proposal(app_participant, path=process_url)
        assert resp.status_code == 200

    def test_participate_participant_can_read_extrafunding(self,
                                                           registry,
                                                           app,
                                                           process_url,
                                                           app_participant,
                                                           proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IExtraFunding
        resp = app_participant.get(proposal0_url)
        data = resp.json_body['data']
        assert IExtraFunding.__identifier__ in data

    def test_participate_participant2_cannot_read_extrafunding(self,
                                                               registry,
                                                               app,
                                                               process_url,
                                                               app_participant2,
                                                               proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IExtraFunding
        resp = app_participant2.get(proposal0_url)
        data = resp.json_body['data']
        assert IExtraFunding.__identifier__ not in data

    def test_participate_participant_can_edit_topic(self,
                                                       registry,
                                                       app,
                                                       process_url,
                                                       app_participant,
                                                       proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert ITopic.__identifier__ in data

    def test_participate_participant_creates_comment(self,
                                                     registry,
                                                     app,
                                                     app_participant,
                                                     proposal0_url):
        path = proposal0_url +  '/comments'
        resp = _post_comment_item(app_participant, path=path)
        assert resp.status_code == 200

    def test_participate_participant_cannot_update_winnerinfo(self,
                                                              registry,
                                                              app,
                                                              process_url,
                                                              app_participant,
                                                              proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert IWinnerInfo not in data


    def test_set_evaluate_state(self, registry, app, process_url, app_admin):
        resp = do_transition_to(app_admin,
                                process_url,
                                'evaluate')
        assert resp.status_code == 200

    def test_evaluate_participant_cannot_creates_proposal(self,
                                                          registry,
                                                          app,
                                                          process_url,
                                                          app_participant):
        from adhocracy_mercator.resources.mercator2 import IMercatorProposal
        postable_types = app_participant.get_postable_types(process_url)
        assert IMercatorProposal not in postable_types

    def test_evaluate_participant_cannot_comment(self,
                                                 registry,
                                                 app,
                                                 process_url,
                                                 app_participant,
                                                 proposal0_url):
        from adhocracy_core.resources.comment import ICommentVersion
        url = proposal0_url + '/comments'
        postable_types = app_participant.get_postable_types(url)
        assert ICommentVersion not in postable_types

    def test_evaluate_participant_cannot_edit_topic(self,
                                                    registry,
                                                    app,
                                                    process_url,
                                                    app_participant,
                                                    proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import ITopic
        resp = app_participant.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert ITopic.__identifier__ not in data


    def test_evaluate_moderator_can_update_winnerinfo(self,
                                                      registry,
                                                      app,
                                                      process_url,
                                                      app_moderator,
                                                      proposal0_url):
        from adhocracy_mercator.sheets.mercator2 import IWinnerInfo
        resp = app_moderator.options(proposal0_url)
        data = resp.json_body['PUT']['request_body']['data']
        assert IWinnerInfo.__identifier__ in data
