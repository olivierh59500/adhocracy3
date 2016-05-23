"""Import fixtures."""
import argparse
import logging
import sys

from pyramid.paster import bootstrap

from adhocracy_core.interfaces import IFixtureAsset
from . import import_fixture


logger = logging.getLogger(__name__)


def import_fixtures():
    args = _argparse()
    env = bootstrap(args.ini_file)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    _import_fixtures(env['root'],
                     env['registry'],
                     list_only=args.list_only,
                     custom=args.import_custom,
                     )
    env['closer']()


def _argparse():
    parser = argparse.ArgumentParser(description='Import adhocracy fixtures.')
    parser.add_argument('ini_file',
                        help='path to the adhocracy backend ini file',
                        default='etc/development.ini',
                        nargs='?')
    parser.add_argument('-l',
                        '--list_only',
                        help='List all registered fixture directories.',
                        action='store_true')
    parser.add_argument('-c',
                        '--import_custom',
                        help='Custom fixture name or file system path')
    return parser.parse_args()


def _import_fixtures(root,
                     registry,
                     import_all=True,
                     custom='',
                     list_only=False):
    assets = [x[0] for x in registry.getUtilitiesFor(IFixtureAsset)]
    if list_only:
        print('The following fixture directories are registered')
        for asset in assets:
            print(asset)
    elif custom:
        print('Importing fixture {}'.format(custom))
        import_fixture(custom, root, registry)
    elif import_all:
        for asset in assets:
            print('Importing fixture {}'.format(asset))
            import_fixture(asset, root, registry)

