from pytest import fixture
from pytest import mark


class TestDocumentProcess:

    @fixture
    def meta(self):
        from .engagement_landschaft import process_meta
        return process_meta

    def test_meta(self, meta):
        import adhocracy_core.resources
        from adhocracy_meinberlin import resources
        assert meta.iresource == resources.engagement_landschaft.IProcess
        assert meta.iresource.isOrExtends(
            adhocracy_core.resources.document_process.IDocumentProcess)
        assert meta.workflow_name == 'debate'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)
