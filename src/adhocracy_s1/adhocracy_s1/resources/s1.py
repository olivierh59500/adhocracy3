"""Resource types for s1 process."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.resources.logbook import add_logbook_service
from adhocracy_core.sheets.logbook import IHasLogbookPool


class IProcess(process.IProcess):
    """S1 participation process."""


process_meta = process.process_meta._replace(
    content_name='S1Process',
    iresource=IProcess,
    workflow_name='s1',
)


class IPrivateProcess(process.IProcess):
    """Private S1 participation process."""


private_process_meta = process.process_meta._replace(
    content_name='S1PrivateProcess',
    iresource=IProcess,
    workflow_name='s1_private',
)


class IProposalVersion(proposal.IProposalVersion):
    """S1 participation process content version."""


proposal_version_meta = proposal.proposal_version_meta\
    ._replace(iresource=IProposalVersion,
              )\
    ._add(extended_sheets=(IHasLogbookPool,
                           ))


class IProposal(proposal.IProposal):
    """S1 participation process content."""


proposal_meta = proposal.proposal_meta\
    ._replace(iresource=IProposal,
              element_types=(IProposalVersion,),
              item_type=IProposalVersion,
              autonaming_prefix = 'proposal_',
              workflow_name = 's1_content',
              )\
    ._add(after_creation=(add_logbook_service,))


class IPrivateProposal(proposal.IProposal):
    """Private S1 participation process content."""


private_proposal_meta = proposal.proposal_meta \
    ._replace(iresource=IPrivateProposal,
              element_types=(IProposalVersion,),
              item_type=IProposalVersion,
              autonaming_prefix = 'proposal_',
              workflow_name = 's1_content_private',
              ) \
    ._add(after_creation=(add_logbook_service,))


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(private_process_meta, config)
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(private_proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
