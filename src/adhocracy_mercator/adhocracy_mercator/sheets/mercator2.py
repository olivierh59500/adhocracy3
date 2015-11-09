"""Sheets for Mercator 2 proposals."""
import colander

from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import SingleLine
from adhocracy_core.interfaces import ISheet
from adhocracy_core.sheets import add_sheet_to_registry


class IUserInfo(ISheet):
    """Marker interface for information about the proposal submitter."""


class UserInfoSchema(colander.MappingSchema):
    """Information about the proposal submitter."""

    first_name = SingleLine(missing=colander.required)
    last_name = SingleLine()

userinfo_meta = sheet_meta._replace(isheet=IUserInfo,
                                    schema_class=UserInfoSchema)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(userinfo_meta, config.registry)
