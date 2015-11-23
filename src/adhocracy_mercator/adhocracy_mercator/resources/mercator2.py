"""Mercator 2 proposal."""

from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.interfaces import ISimple
from adhocracy_core.resources.logbook import add_logbook_service
from adhocracy_core.resources.proposal import IProposal
from adhocracy_core.resources.simple import simple_meta
import adhocracy_mercator.sheets.mercator2
import adhocracy_core.sheets


class IPitch(ISimple):
    """Proposal's pitch."""


pitch_meta = simple_meta._replace(
    content_name='Pitch',
    iresource=IPitch,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='pitch',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IPitch,
        adhocracy_core.sheets.description.IDescription,
        adhocracy_core.sheets.comment.ICommentable),
)


class IDuration(ISimple):
    """Duration."""

location_meta = simple_meta._replace(
    content_name='location',
    iresource=IDuration,
    permission_create='create_proposal',
    use_autonaming=True,
    autonaming_prefix='location',
    extended_sheets=(
        adhocracy_mercator.sheets.mercator2.IDuration,
        adhocracy_core.sheets.comment.ICommentable),
)


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
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(pitch_meta, config)
    add_resource_type_to_registry(location_meta, config)

# TODO specify workflow
#    workflow_name = 'mercator'
# TODO 'visualise your idea' / image
