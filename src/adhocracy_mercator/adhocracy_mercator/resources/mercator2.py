"""Mercator 2 proposal."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.resources.logbook import add_logbook_service
from adhocracy_core.resources.proposal import IProposal
import adhocracy_mercator.sheets.mercator2


class IMercatorProposal(IProposal):
    """Mercator 2 proposal. Not versionable."""

proposal_meta = proposal.proposal_meta._replace(
    content_name='MercatorProposal2',
    iresource=IMercatorProposal,
    extended_sheets=(adhocracy_mercator.sheets.mercator2.IUserInfo,),
)._add(after_creation=(add_logbook_service,))


class IProcess(process.IProcess):
    """Mercator 2 participation process."""

process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=(IMercatorProposal,
                   ),
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)

# TODO specify workflow
#    workflow_name = 'mercator'
