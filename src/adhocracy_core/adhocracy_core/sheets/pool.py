"""List, search and filter child resources."""
from copy import deepcopy

from colander import drop

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.schema import Integer
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import MappingType
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.interfaces import search_query
from adhocracy_core.interfaces import search_result
from adhocracy_core.interfaces import SearchQuery
from adhocracy_core.utils import remove_keys_from_dict


class PoolSheet(AnnotationRessourceSheet):
    """Pool resource sheet that allows filtering and aggregating elements."""

    _additional_params = ('serialization_form', 'show_frequency', 'show_count')

    def get(self, params: dict={},
            add_back_references=True,
            omit_readonly=False) -> dict:
        """Return child references or arbitrary search for descendants.

        :param params: Parameters to update the search query to find `elements`
            references (possible items are described in
            :class:`adhocracy_core.interfaces.SearchQuery`).
            The default search query is set in the `_references_query`
            property.
            If empty only direct child resources are returned and filtered by
            the target_isheet of the elements field.

        :returns: dictionary with key/values according to
                  :class:`adhocracy_core.interfaces.SearchResult`
        """
        return super().get(params,
                           add_back_references=add_back_references,
                           omit_defaults=omit_readonly)

    def _get_references_query(self, params: dict) -> SearchQuery:
        reftype = self._fields['reference']['elements'].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        default_params = {'interfaces': target_isheet,
                          'root': self.context,
                          'depth': 1,
                          'only_visible': False,
                          'resolve': True,
                          'allows': (),
                          }
        query = search_query._replace(**default_params)
        if params:
            query = query._replace(**params)
        return query

    def _get_reference_appstruct(self, query: SearchQuery) -> dict:
        if not self._catalogs:
            return {}  # ease testing
        default_query = self._get_references_query({})
        if query == default_query:  # performance tweak
            target_isheet = query.interfaces
            children = self.context.values()
            elements = [x for x in children if target_isheet.providedBy(x)]
            result = search_result._replace(elements=elements,
                                            count=len(elements))
        else:
            result = self._catalogs.search(query)
        appstruct = {'elements': result.elements,
                     'count': result.count,
                     'frequency_of': result.frequency_of,
                     'group_by': result.group_by,
                     }
        return appstruct

    def serialize(self, params: dict=None) -> dict:
        """Get sheet appstruct data and serialize.

        Extends :func:`adhocracy_core.interfaces.IResourceSheet.serialize`
        with the following parameters:

            serialization_form (str):
                serialization for references resources: `omit` returns an empty
                list, `url` the resource urls, `content` all resource data.
                Defaults to `path`.

            show_count (bool):
                add 'count` field, defaults to True.

            show_frequency (bool):
                add 'aggregateby` field. defaults to False.
        """
        params = params or {}
        has_custom_filters = params != {}
        settings = self.registry['config']
        if settings.adhocracy.filter_by_view_permission:
            params['allows'] = (self.request.effective_principals, 'view')
        if settings.adhocracy.filter_by_visible:
            params['only_visible'] = True
        params_query = remove_keys_from_dict(params, self._additional_params)
        appstruct = self.get(params=params_query, omit_readonly=True)
        if not has_custom_filters and self.meta.isheet is IPool:
            # workaround to reduce needless but expensive listing of elements
            params['serialization_form'] = 'omit'
            params['show_count'] = True
        if params.get('serialization_form', False) == 'omit':
            appstruct['elements'] = []
        if params.get('show_frequency', False):
            index_name = params.get('frequency_of', '')
            frequency = appstruct['frequency_of']
            appstruct['aggregateby'] = {index_name: frequency}
        # TODO: rename aggregateby in frequency_of
        schema = self.get_schema_with_bindings()
        schema = self._add_additional_nodes(schema, params)
        cstruct = schema.serialize(appstruct)
        return cstruct

    def _add_additional_nodes(self, schema: MappingSchema,
                              params: dict):
        if params.get('serialization_form', False) == 'content':
            elements = schema['elements']
            typ_copy = deepcopy(elements.children[0].typ)
            typ_copy.serialization_form = 'content'
            elements.children[0].typ = typ_copy
        if params.get('show_count', True):  # pragma: no branch
            child = Integer(default=0,
                            missing=drop,
                            name='count')
            schema.add(child)
        if params.get('show_frequency', False):
            child = SchemaNode(MappingType(unknown='preserve'),
                               default={},
                               missing=drop,
                               name='aggregateby')
            schema.add(child)
        return schema


class IPool(ISheet):
    """Marker interface for the pool sheet."""


class PoolElementsReference(SheetToSheet):
    """Pool sheet elements reference."""

    source_isheet = IPool
    source_isheet_field = 'elements'
    target_isheet = ISheet


class PoolSchema(MappingSchema):
    """Pool sheet data structure.

    `elements`: children of this resource (object hierarchy).
    """

    elements = UniqueReferences(reftype=PoolElementsReference,
                                readonly=True,
                                )


pool_meta = sheet_meta._replace(
    isheet=IPool,
    schema_class=PoolSchema,
    sheet_class=PoolSheet,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register adapter."""
    add_sheet_to_registry(pool_meta, config.registry)
