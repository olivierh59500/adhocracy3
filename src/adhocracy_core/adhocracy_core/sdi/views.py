from colander import SchemaNode
from colander import String
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_defaults
from substanced.folder import views as sd_folder_views
from substanced import content as sd_content
from substanced.form import FormView
from substanced.util import _
from substanced.util import find_objectmap
from substanced.sdi import mgmt_view
from substanced.sdi.views import acl as sd_sdi_views_acl
from substanced.schema import Schema

from adhocracy_core.interfaces import IPool
from adhocracy_core.sheets.name import IName


class SheetsFormView(FormView):

    def _build_form(self):
        """Changed behavior:

            - expected self.schema to have all needed bindings

            - add CSRF protection to self.schema

            - fix bugs with deform and adhocracy permission sheet
        """
        use_ajax = getattr(self, 'use_ajax', False)
        ajax_options = getattr(self, 'ajax_options', '{}')
        action = getattr(self, 'action', '')
        method = getattr(self, 'method', 'POST')
        formid = getattr(self, 'formid', 'deform')
        autocomplete = getattr(self, 'autocomplete', None)
        request = self.request
        sheet_schema = self.schema
        schema_with_csrf = Schema()
        for child in sheet_schema:
            schema_with_csrf.add(child)
        schema_with_csrf.validator = sheet_schema.validator
        bindings = sheet_schema.bindings
        bindings['_csrf_token_'] = request.session.get_csrf_token()
        if not bindings['request']:
            bindings['request'] = request  # workaround Bug permission sheet
        self.schema = schema_with_csrf.bind(**bindings)
        form = self.form_class(self.schema, action=action, method=method,
                               buttons=self.buttons, formid=formid,
                               use_ajax=use_ajax, ajax_options=ajax_options,
                               autocomplete=autocomplete)
        self.before(form)
        reqts = form.get_widget_resources()
        for field in form.children:
            is_readonly = getattr(field.schema, 'readonly', False)
            if is_readonly:
                from colander import null
                field.widget.readonly = True
                if field.name in form.cstruct:
                    # workaround Bug with deform list widget
                    del form.cstruct[field.name]
                    field.widget.deserialize = lambda x, y: null
        return form, reqts


@sd_folder_views.folder_contents_views()
class AdhocracyFolderContents(sd_folder_views.FolderContents):
    """Default contents tab."""

    def sdi_addable_content(self):
        registry = self.request.registry
        introspector = registry.introspector
        cts = []
        meta_addable = self.request.registry.content\
            .get_resources_meta_addable(self.context, self.request)
        content_types_addable = [m.iresource.__identifier__ for m
                                 in meta_addable]
        for data in introspector.get_category('substance d content types'):
            intr = data['introspectable']
            if intr['content_type'] in content_types_addable:
                cts.append(data)
        return cts


def binder_columns(folder, subobject, request, default_columnspec):
    subobject_name = getattr(subobject, '__name__', str(subobject))
    objectmap = find_objectmap(folder)
    user_oid = getattr(subobject, '__creator__', None)
    created = getattr(subobject, '__created__', None)
    modified = getattr(subobject, '__modified__', None)
    state = [x for x in getattr(subobject, '__workflow_state__', {'':''}).values()][-1]
    if user_oid is not None:
        user = objectmap.object_for(user_oid)
        user_name = getattr(user, '__name__', 'anonymous')
    else:
        user_name = 'anonymous'
    if created is not None:
        created = created.isoformat()
    if modified is not None:
        modified = modified.isoformat()

    def make_sorter(index_name):
        def sorter(folder, resultset, limit=None, reverse=False):
            #index = find_index(folder, 'sdidemo', index_name)
            #if index is None:
            return resultset
            #return resultset.sort(index, limit=limit, reverse=reverse)
        return sorter

    return default_columnspec + \
           [
               {'name': 'Title',
                'value': getattr(subobject, 'title', subobject_name),
                'sorter': make_sorter('title'),
                },
               {'name': 'Modified Date',
                'value': modified,
                'sorter': make_sorter('modified'),
                'formatter': 'date',
                },
               {'name': 'Creator',
                'value': user_name,
                },
               {'name': 'Workflow state',
                'value': state,
                },
           ]


@sd_folder_views.folder_contents_views(
    name='services',
    tab_title=_('Services'),
    tab_near=sd_folder_views.RIGHT,
    view_permission='sdi.view-services',
    tab_condition=sd_folder_views.has_services,
    )
class AdhocracyFolderServices(sd_folder_views.FolderServices):
    """Services tab."""


@view_defaults(name='acl_edit',
               permission='sdi.change-acls',
               renderer='substanced.sdi.views:templates/acl.pt')
class AdhocracyACLEditViews(sd_sdi_views_acl.ACLEditViews):
    """Security tab."""

    @mgmt_view(tab_title=_('Security'))
    def acl_view(self):
        return super().acl_view()

    def get_principal_name(self, principal_id):
        return principal_id

    @mgmt_view(tab_condition=False,
               name='inherited_acl',
               renderer='substanced.sdi.views:templates/acl#inherited_acl.pt')
    def inherited_acl(self):
        return super().inherited_acl()

    @mgmt_view(tab_condition=False,
               name='local_acl',
               tab_title=_('Security'),
               renderer='substanced.sdi.views:templates/acl#local_acl.pt')
    def local_acl(self):
        return super().local_acl()

    @mgmt_view(request_param='form.move_up',
               tab_title=_('Security'))
    def move_up(self):
        return super().move_up()

    @mgmt_view(request_param='form.move_down',
               tab_title=_('Security'))
    def move_down(self):
        return super().move_down()

    @mgmt_view(request_param='form.remove',
               tab_title=_('Security'))
    def remove(self):
        return super().remove()

    @mgmt_view(request_param='form.add',
               tab_title=_('Security'))
    def add(self):
        return super().add()

    @mgmt_view(request_param='form.inherit',
               tab_title=_('Security'))
    def inherit(self):
        return super().inherit()


@mgmt_view(
    context=IPool,
    name='upload',
    tab_title=_('Upload'),
    #tab_condition=True,
    #addable_content='File',
    tab_after='contents',
    permission='sdi.add-content',
    renderer='substanced.folder:templates/multiupload.pt'
    )
def multi_upload(context, request):
    return {}


@mgmt_view(
    context=IPool,
    name='upload-submit',
    request_method='POST',
    renderer='json',
    permission='sdi.add-content',
    )
def multi_upload_submit(context, request):
    return sd_folder_views.multi_upload_submit(context, request)


@mgmt_view(
    name='properties',
    renderer='substanced.property:templates/propertysheets.pt',
    tab_title=_('Sheets'),
    permission='sdi.view',
    )
class AdhocracyPropertySheetsView(SheetsFormView):
    """Sheets tab"""

    buttons = (_('save'),)

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.registry = request.registry
        sheets_edit = self.get_editable_sheets()
        if not sheets_edit:
            raise HTTPNotFound('No viewable property sheets')
        subpath = request.subpath
        active_factory = None
        active_sheet_name = ''
        if subpath:
            active_sheet_name = subpath[0]
            active_factory = dict(sheets_edit)[active_sheet_name]
        if not active_factory:
            active_sheet_name, active_factory = sheets_edit[0]
        self.active_sheet_name = active_sheet_name
        self.active_sheet = dict(sheets_edit)[active_sheet_name]
        self.sheet_names = [x[0] for x in sheets_edit]
        self.schema = self.active_sheet.get_schema_with_bindings()

    def get_editable_sheets(self) -> []:
        sheets = self.registry.content.get_sheets_edit(self.context,
                                                       self.request)
        return [(s.meta.isheet.__identifier__, s) for s in sheets]

    def save_success(self, appstruct: dict):
        self.active_sheet.set(appstruct)
        self.request.sdiapi.flash_with_undo('Updated sheets', 'success')
        return HTTPFound(self.request.sdiapi.mgmt_path(
            self.context, '@@properties', self.active_sheet_name))

    def show(self, form):
        appstruct = self.active_sheet.get()
        return {'form': form.render(appstruct=appstruct,
                                    readonly=False)}


class AddResourceSchema(Schema):
    name = SchemaNode(String(),
                      validator=sd_folder_views.name_validator,
                      )


def register_add_view(parent_iresource, iresource, config, view_name):
    content_type = iresource.__identifier__

    class AddResourceView(FormView):
        title = 'Add {0}'.format(content_type)
        schema = AddResourceSchema()
        buttons = ('add',)

        def add_success(self, appstruct):
            registry = self.request.registry
            meta = registry.content.resources_meta[iresource]
            appstructs = {}
            if not meta.use_autonaming:
                name = appstruct['name']
                appstructs = {IName.__identifier__: {'name': name}}
            registry.content.create(content_type,
                                    parent=self.context,
                                    appstructs=appstructs,
                                    request=self.request,
                                    registry=self.request.registry,
                                    )
            return HTTPFound(location=self.request.sdiapi.mgmt_path(self.context))

    kwargs = {'context': parent_iresource,
              'name': view_name,
              'tab_condition': False,
              'permission': 'sdi.add-content',
              'renderer': 'substanced.sdi:templates/form.pt',
              'view': AddResourceView,
              }
    config.add_mgmt_view(**kwargs)



def includeme(config):
    config.add_view_predicate('content_type',
                              sd_content._ContentTypePredicate)
    config.include('substanced.property')
    config.include('substanced.folder')
    config.include('substanced.file')
    config.scan('substanced.file')
    config.scan('substanced.db.views')
    config.scan('substanced.sdi.views.manage')
    config.scan('substanced.sdi.views.login')
    config.scan('.views')
