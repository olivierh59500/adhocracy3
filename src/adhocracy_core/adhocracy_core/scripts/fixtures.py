"""Import fixtures."""
import argparse
import logging
import sys

from pyramid.paster import bootstrap

from . import import_fixture


def fixtures_main(additional_package=None):
    args = _argparse()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    _import_fixtures(env['root'], env['registry'], additional_package)
    env['closer']()


def _argparse():
    parser = argparse.ArgumentParser(description='Import adhocracy fixtures.')
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file',
                        default='etc/development.ini',
                        nargs='?')
    return parser.parse_args()


def _import_fixtures(root, registry, additional_package):
    import_fixture('adhocracy_core:fixture', root, registry)
    if additional_package:
        import_fixture(additional_package, root, registry)
