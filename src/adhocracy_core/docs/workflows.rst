Processes and Workflows
=======================

Preliminaries
-------------

For testing, we need to import some stuff and start the Adhocracy testapp::

    >>> from pprint import pprint
    >>> from adhocracy_core.testing import contributor_header
    >>> from webtest import TestApp
    >>> app = getfixture('app')
    >>> testapp = TestApp(app)
    >>> rest_url = 'http://localhost'


Introduction
------------

FIXME This is just a draft outline. It needs to be implemented and probably
revised.

This document explains and demonstrates processes and workflows, using the
Discussion Process as example.

FIXME Make this a pool instead, for simplicity:
Like all process types, discussions are versionable, so we first create an
an item:

    >>> disc = {'content_type': 'adhocracy_core.resources.discussion.IDiscussion',
    ...         'data': {}}
    >>> resp = testapp.post_json(rest_url + '/adhocracy', disc,
    ...                          headers=contributor_header)
    >>> disc_path = resp.json["path"]
    >>> first_discvers_path = resp.json['first_version_path']

Then we create a meaningful version that refers to the first (auto-created)
version as predecessor::

    >>> discvers = {'content_type': 'adhocracy_core.resources.discussion.IDiscussionVersion',
    ...             'data': {
    ...                 'adhocracy_core.sheets.discussion.IDiscussion': {
    ...                        'title': 'Was tun?',
    ...                        'teaser': 'Wer, wenn nicht wir? Wann, wenn nicht jetzt?'},
    ...                 'adhocracy_core.sheets.versions.IVersionable': {
    ...                     'follows': [first_discvers_path]}},
    ...             'root_versions': [first_discvers_path]}
    >>> resp = testapp.post_json(disc_path, discvers, headers=contributor_header)
    >>> snd_discvers_path = resp.json['path']

FIXME Convert into Pool.

The IDiscussion sheet also has a "phase" field. We didn't specify a value
for it, hence it's set to the default value, which (in this case) is "draft":::

    >>> resp_data = testapp.get(snd_discvers_path, headers=contributor_header).json
    >>> resp_data['data']['adhocracy_core.sheets.discussion.IDiscussion']['phase']
    'draft'

In the draft phase, the discussion is not yet visible to most people.
For example, it is not visible if you are not logged in:

    >>> resp_data = testapp.get(snd_discvers_path, status=403).json
