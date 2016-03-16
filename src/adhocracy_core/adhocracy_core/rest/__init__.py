"""Configure rest api packages."""


def includeme(config):  # pragma: no cover
    """Include all rest views configuration."""
    api_prefix = config.registry.settings.get('substanced.api_prefix', '/api')
    api_pattern = api_prefix + '*traverse'
    config.add_route('substanced_api', api_pattern)
    config.include('.views')
    config.include('.batchview')
    config.add_request_method(lambda x: [], name='errors', reify=True)
    config.add_request_method(lambda x: {}, name='validated', reify=True)
    config.include('.exceptions')
    config.include('.subscriber')

