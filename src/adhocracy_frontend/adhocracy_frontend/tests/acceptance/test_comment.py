from webtest import TestApp
from pytest import fixture
from pytest import mark
import time

from adhocracy_core.testing import god_login
from adhocracy_frontend.tests.acceptance.test_proposal import create_proposal
from adhocracy_frontend.tests.acceptance.shared import wait
from adhocracy_frontend.tests.acceptance.shared import get_column_listing
from adhocracy_frontend.tests.acceptance.shared import get_list_element
from adhocracy_frontend.tests.acceptance.shared import get_listing_create_form
from adhocracy_frontend.tests.acceptance.shared import login_god


class TestComment:

    @fixture(scope='class')
    def browser(self, browser, app):
        TestApp(app)
        login_god(browser)
        browser.visit(browser.app_url +
                      'r/adhocracy/?movingColumns=is-show-show-hide')
        return browser

    @fixture(scope='class')
    def proposals(self, browser):
        content = get_column_listing(browser, 'content')
        proposal = create_proposal(content, 'test proposal with comments')
        show_proposal_comments(proposal)
        return proposal

    @fixture(scope='class')
    def proposal_link(self, browser, proposals):
        """extract proposal link from proposal list"""
        column1 = browser.find_by_css(".moving-column-structure").first
        proposal_list = column1.find_by_css(".moving-column-body").first\
                               .find_by_tag("ol").first
        return proposal_list.find_by_css("h3 a").first

    @fixture(scope='class')
    def comment_view(self, browser, proposal_link):
        """shows a roposal's comments"""
        proposal_link.click()

        def comment_link():
            return browser.find_link_by_href('/r/mercator/' +
                                             proposal_link.text +
                                             '/VERSION_0000001/@comments')

        wait(comment_link)
        comment_link().first.click()

        return browser.find_by_css(".moving-column-content2").first

    def test_create(self, browser, comment_view):
        text = "my comment"
        comment = create_comment(comment_view, text)
        assert comment is not None

    def test_create_long_comment(self, browser, comment_view):
        text = "A"*1000
        comment = create_comment(comment_view, text)
        assert comment is not None

    def test_empty_comment(self, browser, comment_view):
        text = ""
        comment = create_comment(comment_view, text)
        assert comment is None

    def test_show_amount_of_comments(self, browser, comment_view):
        amount_old = int(browser.find_by_css(".chapter-header").first\
                                .find_by_tag("a").first.text)
        assert create_comment(comment_view, text="my comment") is not None
        amount_new = int(browser.find_by_css(".chapter-header").first\
                                .find_by_tag("a").first.text)
        assert amount_new == amount_old + 1

    def test_simple_reply(self, browser, comment_view):
        comment = comment_view.find_by_css('.comment').first
        assert comment is not None

        reply = create_reply_comment(comment, 'somereply')
        assert reply is not None

    def test_nested_reply(self, browser, comment_view):
        level = 15

        to_reply_on = comment_view.find_by_css('.comment').first
        assert to_reply_on is not None

        for i in range(level):
            to_reply_on = create_reply_comment(to_reply_on, 'reply %d' % i)
            assert to_reply_on is not None
            browser.reload()

    def test_edit(self, browser, comment_view):
        comment = comment_view.find_by_css('.comment').first
        edit_comment(comment, 'edited')
        assert comment.find_by_css('.comment-content div').first.text == 'edited'

        browser.reload()

        assert wait(lambda: browser.find_by_css('.comment-content').\
                                                        first.text == 'edited')

    def test_edit_twice(self, browser, comment_view):
        comment = comment_view.find_by_css('.comment').first
        edit_comment(comment, 'edited 1')
        assert wait(lambda: browser.find_by_css('.comment-content').\
                                                      first.text == 'edited 1')
        edit_comment(comment, 'edited 2')
        assert wait(lambda: browser.find_by_css('.comment-content').\
                                                      first.text == 'edited 2')

    @mark.skipif(True, reason='FIXME Test needs to be updated since the '
                              'backend now throws a "No fork allowed" error')
    def test_multi_edits(self, browser):
        parent = get_column_listing(browser, 'content2').\
                                                 find_by_css('.comment').first
        reply = parent.find_by_css('.comment').first
        edit_comment(reply, 'somereply edited')
        edit_comment(parent, 'edited')
        assert parent.find_by_css('.comment-content').first.text == 'edited'

    def test_author(self, browser, comment_view):
        comment = comment_view.find_by_css('.comment').first
        actual = lambda element: element.find_by_css("adh-user-meta").first.text
        # the captialisation might be changed by CSS
        assert wait(lambda: actual(comment).lower() == god_login.lower())


def create_comment(comment_view, text):
    """Create a new comment in comment_view."""
    textarea = comment_view.find_by_tag('textarea').first
    textarea.fill(text)
    comment_view.find_by_css('input[type="submit"]').first.click()

    def comment():
        return get_list_element(comment_view,
                                text,
                                descendant='.comment-content')
    wait(comment)
    return comment()


def show_proposal_comments(proposal):
    proposal.find_by_css('a').first.click()
    proposal.find_by_css('button').last.click()


def create_top_level_comment(listing, content):
    """Create a new top level Comment."""
    form = get_listing_create_form(listing)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()
    wait(lambda: get_list_element(listing, content, descendant='.comment-content'))
    comment = get_list_element(listing, content, descendant='.comment-content')
    return comment


def create_reply_comment(parent, content):
    """Create a new reply to an existing comment."""
    form = get_comment_create_form(parent)
    form.find_by_css('textarea').first.fill(content)
    form.find_by_css('input[type="submit"]').first.click()
    reply = get_reply(parent, content)
    return reply


def edit_comment(comment, content):
    comment.find_by_css('.comment-meta a')[0].click()
    comment.find_by_css('textarea').first.fill(content)
    comment.find_by_css('.comment-meta a')[0].click()
    wait(lambda: comment.find_by_css('.comment-content').first.text == content)


def get_comment_create_form(comment):
    button = comment.find_by_css('.comment-meta a')[-1]
    button.click()
    return comment.find_by_css('.comment-create-form').first


def get_reply(parent, content):
    """Return reply to comment `parent` with content == `content`."""
    for element in parent.find_by_css('.comment'):
        wait(lambda: element.text, max_steps=100)
        if element.find_by_css('.comment-content').first.text == content:
            return element
