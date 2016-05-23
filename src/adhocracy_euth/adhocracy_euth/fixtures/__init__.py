"""Extend adhocracy core fixtures."""
from adhocracy_core.scripts.fixtures import fixtures_main as fixtures_main_core


def fixtures_main():
    """Load fixtures for adhocracy_core and adhocracy_euth."""
    fixtures_main_core('adhocracy_euth:fixture')
