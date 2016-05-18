"""Imprort fixtures in development environment
"""
import argparse
import os
import pkg_resources

from pyramid.paster import bootstrap
from pyramid.registry import Registry

from adhocracy_core.interfaces import IResource

from . import import_resources as main_import_resources
from . import import_local_roles as main_import_local_roles
from .import_users import _import_users as main_import_users
from .import_groups import _import_groups as main_import_groups
from .set_workflow_state import _set_workflow_state as main_set_workflow_state

def _import_fixtures(package: str, root: IResource, registry: Registry):
    types = [ 'groups', 'users', 'resources', 'local_roles' ]
    fixtures_exits = pkg_resources.resource_isdir(
        'adhocracy_core', 'fixtures')

    if not fixtures_exits:
        return

    for fixture_type in types:
        fixture_type_exists = pkg_resources.resource_isdir(
            package,
            'fixtures/' + fixture_type)

        if not fixture_type_exists:
            continue

        filenames = pkg_resources.resource_listdir(
            package,
            'fixtures/' + fixture_type)

        for filename in filenames:
            fixture = pkg_resources.resource_filename(
                package,
                '/fixtures/{}/{}'.format(fixture_type, filename))

            print('Importing {} from {}'.format(fixture_type, os.path.relpath(fixture)))

            if fixture_type == 'groups':
                main_import_groups(root, registry, fixture)
            elif fixture_type == 'users':
                main_import_users(root, registry, fixture)
            elif fixture_type == 'resources':
                main_import_resources(root, registry, fixture)
            elif fixture_type == 'local_roles':
                main_import_local_roles(root, registry, fixture)

def _set_workflow_phases(package: str, root: IResource, registry: Registry):
    try:
        statesfile = pkg_resources.resource_stream(package, '/fixtures/process_states')
    except FileNotFoundError:
        return

    lines = [ str(l, 'UTF-8').strip() for l in statesfile.readlines() ]

    process_states = { line.split(':')[0]: line.split(':')[1].split('->')
                       for line in  lines }

    for process_path, states in process_states.items():
        print('Set workflow state for {}'.format(process_path))
        main_set_workflow_state(root, registry, process_path, states, absolute=True, reset=True)


def _argparse():
    parser = argparse.ArgumentParser(description='Import adhocracy fixtures.')
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file',
                        default='etc/development.ini',
                        nargs='?')
    return parser.parse_args()


def fixtures_main(additional_package = None):
    args = _argparse()
    env = bootstrap(args.ini_file)
    root = env['root']
    registry = env['registry']


    _import_fixtures('adhocracy_core', root, registry)
    _set_workflow_phases('adhocracy_core', root, registry)

    if additional_package:
        _import_fixtures(additional_package, root, registry)
        _set_workflow_phases(additional_package, root, registry)


if __name__ == "__main__":
    fixtures_main()
