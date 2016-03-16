"""Admin interface based on substanced, url prefix is 'sdi'."""



def includeme(config):
    """Register sdi admin interface."""
    from substanced.sdi import user
    from substanced.sdi import MANAGE_ROUTE_NAME
    from substanced.sdi import sdiapi
    config.include('pyramid_chameleon')
    settings = config.registry.settings
    year = 86400 * 365
    config.add_static_view('deformstatic', 'deform:static', cache_max_age=year)
    config.add_static_view('sdistatic', 'substanced.sdi:static',
                           cache_max_age=year)
    config.override_asset(to_override='substanced.sdi:templates/',
                          override_with='substanced.sdi.views:templates/')
    manage_prefix = settings.get('substanced.manage_prefix', '/manage')
    manage_pattern = manage_prefix + '*traverse'
    config.add_route(MANAGE_ROUTE_NAME, manage_pattern)
    config.add_request_method(user, reify=True)
    config.set_request_property(lambda r: r.user.locale, name="_LOCALE_")
    config.add_request_method(sdiapi, reify=True)
    config.add_permission('sdi.edit-properties')  # used by sheet machinery
    config.include('.views')
