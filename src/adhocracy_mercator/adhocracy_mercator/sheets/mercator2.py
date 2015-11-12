"""Sheets for Mercator 2 proposals."""
import colander

from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import SingleLine
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import ISOCountryCode
from adhocracy_core.schema import AdhocracySchemaNode
from adhocracy_core.schema import Text
from adhocracy_core.schema import URL
from adhocracy_core.schema import DateTime
from adhocracy_core.schema import Email
from adhocracy_core.schema import Boolean
from adhocracy_core.schema import Integer


class IUserInfo(ISheet):
    """Marker interface for information about the proposal submitter."""


class UserInfoSchema(colander.MappingSchema):
    """Information about the proposal submitter."""

    first_name = SingleLine(missing=colander.required)
    last_name = SingleLine(missing=colander.required)

userinfo_meta = sheet_meta._replace(isheet=IUserInfo,
                                    schema_class=UserInfoSchema)


class IOrganizationInfo(ISheet):
    """Marker interface for organizational information."""


class OrganizationStatusEnum(AdhocracySchemaNode):
    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['registered_nonprofit',
                                'planned_nonprofit',
                                'support_needed',
                                'other',
                                ])


class OrganizationInfoSchema(colander.MappingSchema):
    """Data structure for organizational information."""

    name = SingleLine(missing=colander.required)
    city = SingleLine(missing=colander.required)
    country = ISOCountryCode(missing=colander.required)
    help_request = Text(validator=colander.Length(max=300))
    registration_date = DateTime(missing=colander.required, default=None)
    website = URL(missing=colander.drop)
    contact_email = Email(missing=colander.required)
    status = OrganizationStatusEnum(missing=colander.required)
    status_other = Text(validator=colander.Length(max=300))

    def validator(self, node, value):
        """Extra validation depending of the status of the organisation.

        Make `status_other` required if `status` == `other` and
        `help_request` required if `status` == `support_needed`.
        """
        status = value.get('status', None)
        if status == 'support_needed':
            if not value.get('help_request', None):
                help_request = node['help_request']
                raise colander.Invalid(
                    help_request,
                    msg='Required iff status == support_needed')
        elif status == 'other':
            if not value.get('status_other', None):
                status_other = node['status_other']
                raise colander.Invalid(status_other,
                                       msg='Required iff status == other')


organizationinfo_meta = sheet_meta._replace(
    isheet=IOrganizationInfo,
    schema_class=OrganizationInfoSchema)


class IPartners(ISheet):
    """Marker interface for the partner description."""


class PartnersSchema(colander.MappingSchema):
    has_partners = Boolean()
    partner1_name = SingleLine()
    partner1_website = URL()
    partner1_country = ISOCountryCode()
    partner2_name = SingleLine()
    partner2_website = URL()
    partner2_country = ISOCountryCode()
    partner3_name = SingleLine()
    partner3_website = URL()
    partner3_country = ISOCountryCode()
    other_partners = Text()


partners_meta = sheet_meta._replace(
    isheet=IPartners, schema_class=PartnersSchema)


class TopicEnum(AdhocracySchemaNode):
    """Enum of topic domains."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['democracy_and_participation',
                                'arts_and_cultural_activities',
                                'environment',
                                'social_inclusion',
                                'migration',
                                'communities',
                                'urban_development',
                                'education',
                                'other',
                                ])


class ITopic(ISheet):
    """Marker interface for the topic (ex: democracy, art, environment etc)."""


class TopicSchema(colander.MappingSchema):
    topic = TopicEnum(missing=colander.required)
    # TODO check other text is specified if topic is 'other'
    other = Text()


topic_meta = sheet_meta._replace(
    isheet=ITopic,
    schema_class=TopicSchema)


class IDuration(ISheet):
    """Marker interface for the duration."""


class DurationSchema(colander.MappingSchema):
    duration = Integer(missing=colander.required)


duration_meta = sheet_meta._replace(
    isheet=IDuration,
    schema_class=DurationSchema)


class ILocation(ISheet):
    """Marker interface for the location."""


class LocationSchema(colander.MappingSchema):
    city = Text(missing=colander.required)
    country = ISOCountryCode(missing=colander.required)
    has_link_to_ruhr = Boolean(missing=colander.required, default=False)
    # TODO makes next field obligatory if there is a link
    link_to_ruhr = Text()


location_meta = sheet_meta._replace(
    isheet=ILocation,
    schema_class=LocationSchema,
)


class IStatus(ISheet):
    """Marker interface for the project status."""


class ProjectStatusEnum(AdhocracySchemaNode):
    """Enum of organizational statuses."""

    schema_type = colander.String
    default = 'other'
    missing = colander.required
    validator = colander.OneOf(['starting',
                                'developping',
                                'scaling',
                                'other',
                                ])


class StatusSchema(colander.MappingSchema):
    status = ProjectStatusEnum(missing=colander.required)


class IRoadToImpact(ISheet):
    """Marker interface for the road to impact."""


class RoadToImpactSchema(colander.MappingSchema):
    challenge = Text(missing=colander.required)
    aim = Text(missing=colander.required)
    plan = Text(missing=colander.required)
    doing = Text(missing=colander.required)
    team = Text(missing=colander.required)
    other = Text(missing=colander.required)

roadtoimpact_meta = sheet_meta._replace(
    isheet=IRoadToImpact,
    schema_class=RoadToImpactSchema,
)

status_meta = sheet_meta._replace(
    isheet=IStatus,
    schema_class=StatusSchema,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(userinfo_meta, config.registry)
    add_sheet_to_registry(organizationinfo_meta, config.registry)
    add_sheet_to_registry(partners_meta, config.registry)
    add_sheet_to_registry(topic_meta, config.registry)
    add_sheet_to_registry(duration_meta, config.registry)
    add_sheet_to_registry(location_meta, config.registry)
    add_sheet_to_registry(status_meta, config.registry)
    add_sheet_to_registry(roadtoimpact_meta, config.registry)
