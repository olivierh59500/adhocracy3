"""Stadtforum process resources."""
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal


class IPoll(proposal.IProposal):
    """Poll."""


poll_meta = proposal.proposal_meta._replace(
    iresource=IPoll,
    default_workflow='stadtforum_poll',
    autonaming_prefix='poll_',
)


class IProcess(process.IProcess):
    """Stadtforum participation process."""


process_meta = process.process_meta._replace(
    content_name='StadtForumProcess',
    iresource=IProcess,
    element_types=(IPoll,
                   ),
    is_implicit_addable=True,
    default_workflow = 'stadtforum',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(process_meta, config)
    add_resource_type_to_registry(poll_meta, config)
