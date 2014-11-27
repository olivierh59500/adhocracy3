from webtest import TestApp
from pytest import fixture
from pytest import mark
import random
import time

from adhocracy_core.testing import god_login
from adhocracy_frontend.tests.acceptance.test_proposal import create_proposal
from adhocracy_frontend.tests.acceptance.test_comment import TestComment
from adhocracy_frontend.tests.acceptance.shared import wait
from adhocracy_frontend.tests.acceptance.shared import get_column_listing
from adhocracy_frontend.tests.acceptance.shared import get_list_element
from adhocracy_frontend.tests.acceptance.shared import get_listing_create_form
from adhocracy_frontend.tests.acceptance.shared import login_god
from adhocracy_frontend.tests.acceptance.shared import api_login_god
from mercator.tests.fixtures.fixturesMercatorProposals1 import create_proposals

@fixture(scope='module')
def proposals():
    return create_proposals(api_login_god(), n=1)


class TestComment(TestComment):

    @fixture(scope='class')
    def browser(self, browser, app):
        TestApp(app)
        login_god(browser)
        browser.visit(browser.app_url + 'r/mercator/')
        return browser

    @fixture(scope='class')
    def proposal_link(self, browser, proposals):
        """extract proposal link from proposal list"""
        column1 = browser.find_by_css(".moving-column-structure").first
        proposal_list = column1.find_by_css(".moving-column-body").first\
                               .find_by_tag("ol").first
        return proposal_list.find_by_css("h3 a").first

    @fixture(scope='class')
    def comment_view(self, browser, proposal_link):
        """shows a random proposal's comments"""
        proposal_link.click()

        def comment_link():
            return browser.find_link_by_href('/r/mercator/' +
                                             proposal_link.text +
                                             '/VERSION_0000001/@comments')

        wait(comment_link)
        comment_link().first.click()

        return browser.find_by_css(".moving-column-content2").first

