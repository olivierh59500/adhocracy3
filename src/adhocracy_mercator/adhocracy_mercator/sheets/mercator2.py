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


class StatusEnum(AdhocracySchemaNode):
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
    status = StatusEnum(missing=colander.required)
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
        if status == 'other':
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


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(userinfo_meta, config.registry)
    add_sheet_to_registry(organizationinfo_meta, config.registry)
    add_sheet_to_registry(partners_meta, config.registry)
