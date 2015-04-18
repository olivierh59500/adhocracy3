"""Scripts to migrate legacy objects in existing databases."""
import logging
from pyramid.threadlocal import get_current_registry
from substanced.evolution import add_evolution_step
from zope.interface.interfaces import IInterface
from adhocracy_core.utils import get_sheet
from adhocracy_core.interfaces import IPool
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.sheets.comment import IComment


logger = logging.getLogger(__name__)


def migrate_sheet_to_attribute_storage(context: IPool,
                                       isheet: IInterface):
    """Migrate `isheet` sheet to attribute storage."""
    registry = get_current_registry(context)
    pool = get_sheet(context, IPool, registry=registry)
    query = {'sheet': isheet,
             'depth': 'all',
             'only_visible': False,
             }
    resources = pool.get(query)['elements']
    count = len(resources)
    logger.info('Migrating {0} to attribute storage {1}'.format(count, isheet))
    for index, resource in enumerate(resources):
        logger.info('Migrating {0} of {1}: {2}'.format(index + 1, count,
                                                       resource))
        annotation_data = getattr(resource, '_sheets', {})
        sheet_data = annotation_data.get(isheet.__identifier__, {})
        if sheet_data:
            sheet = get_sheet(resource, isheet, registry=registry)
            appstruct = annotation_data[isheet.__identifier__]
            sheet.set(appstruct)
            del annotation_data[isheet.__identifier__]
        if annotation_data == {} and hasattr(resource, '_sheets'):
            delattr(resource, '_sheets')


def evolve2_use_attribute_storage_for_rate_sheet(root: IPool):
    """Migrate rate sheet to attribute storage."""
    migrate_sheet_to_attribute_storage(root, IRate)


def evolve3_use_attribute_storage_for_comment_sheet(root: IPool):
    """Migrate commet sheet to attribute storage."""
    migrate_sheet_to_attribute_storage(root, IComment)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_directive('add_evolution_step', add_evolution_step)
    config.scan('substanced.evolution.subscribers')
    config.add_evolution_step(evolve2_use_attribute_storage_for_rate_sheet)
    config.add_evolution_step(evolve3_use_attribute_storage_for_comment_sheet)
