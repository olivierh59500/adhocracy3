from pytest import fixture


@fixture(scope='class')
def app_router(app_settings):
    from adhocracy_core.testing import make_configurator
    import adhocracy_core
    configurator = make_configurator(app_settings, adhocracy_core)
    configurator.include('adhocracy_core.sdi')
    import bpdb;bpdb.set_trace()
    return configurator.make_wsgi_app()


def test_add_sdi_interface(app_god):
    import bpdb;bpdb.set_trace()
