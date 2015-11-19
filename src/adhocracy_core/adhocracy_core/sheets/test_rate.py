from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
import colander

from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.rate import ILikeable




@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.rate')


def _make_rateable():
    return testing.DummyResource(__provides__=IRateable)


class TestRateableSheet:

    @fixture
    def inst(self, pool, service):
        pool['rates'] = service
        from adhocracy_core.sheets.rate import rateable_meta
        return rateable_meta.sheet_class(rateable_meta, pool)

    def test_create(self, inst):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        from adhocracy_core.sheets.rate import IRateable
        from adhocracy_core.sheets.rate import RateableSchema
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IRateable
        assert inst.meta.schema_class == RateableSchema
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, inst):
        post_pool = inst.context['rates']
        assert inst.get() == {'post_pool': post_pool,
                              'rates': [],
                              }

class TestRateSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.rate import rate_meta
        return rate_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        inst = meta.sheet_class(meta, context)
        assert issubclass(meta.sheet_class, AttributeResourceSheet)
        assert inst.meta.isheet == IRate
        assert inst.meta.schema_class == RateSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': None,
                              'object': None,
                              'rate': 0,
                              }


class DummyQuery:

    def __init__(self, result=[]):
        self.result = result

    def __iand__(self, other):
        return self

    def execute(self, **kwargs):
        return self.result


class DummyIndex:

    def __init__(self, result=[]):
        self.result = result

    def eq(self, *args, **kwargs):
        return DummyQuery(self.result)

    def noteq(self, *args, **kwargs):
        return DummyQuery(self.result)


@mark.usefixtures('integration')
class TestRateSchema:

    @fixture
    def schema_with_mock_ensure_rate(self, monkeypatch, request_, context):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import RateSchema
        mock = Mock()
        monkeypatch.setattr(rate, '_ensure_rate_is_unique', mock)
        schema = RateSchema().bind(request=request_, context=context)
        return schema

    @fixture
    def subject(self, monkeypatch):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanRate
        subject = testing.DummyResource(__provides__=ICanRate)
        mock_get_user = Mock(return_value=subject)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        return subject

    def test_deserialize_valid(self, context, schema_with_mock_ensure_rate,
                               subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '1'}
        assert schema_with_mock_ensure_rate.deserialize(data) == {
            'subject': subject, 'object': object, 'rate': 1}

    def test_deserialize_valid_minus_one(self, context,
                                         schema_with_mock_ensure_rate,
                                         subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '-1'}
        assert schema_with_mock_ensure_rate.deserialize(data) == {
            'subject': subject, 'object': object, 'rate': -1}

    def test_deserialize_invalid_rate(self, context,
                                      schema_with_mock_ensure_rate, subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '77'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_subject(self, context,
                                         schema_with_mock_ensure_rate):
        subject = testing.DummyResource()
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_subject_missing(self, context,
                                                 schema_with_mock_ensure_rate):
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_subject_isnt_current_user(
            self, context, monkeypatch, schema_with_mock_ensure_rate):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanRate
        subject = testing.DummyResource(__provides__=ICanRate)
        user = testing.DummyResource(__provides__=ICanRate)
        mock_get_user = Mock(return_value=user)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_object(self, context,
                                        schema_with_mock_ensure_rate,
                                        subject):
        context['subject'] = subject
        object = testing.DummyResource()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_object_missing(self, context,
                                        schema_with_mock_ensure_rate, subject):
        context['subject'] = subject
        data = {'subject': '/subject', 'object': '', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_ensure_rate_is_unique_ok(self, monkeypatch, request_,
                                      context, subject):
        from adhocracy_core.sheets.rate import _ensure_rate_is_unique
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets import rate
        mock_find_catalog = Mock(return_value={'reference': DummyIndex(),
                                               'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = RateSchema().bind(request=request_, context=context)
        object = _make_rateable()
        node = Mock()
        value = {'subject': subject, 'object': object, 'rate': '1'}
        result = _ensure_rate_is_unique(node, value, request_)
        assert result is None

    def test_ensure_rate_is_unique_error(self, monkeypatch, request_,
                                         context, subject):
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets.rate import _ensure_resource_is_unique
        from adhocracy_core.sheets import rate
        from adhocracy_core.utils import named_object
        mock_find_catalog = Mock(
            return_value={'reference': DummyIndex(['dummy']),
                          'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = RateSchema().bind(request=request_, context=context)
        object = _make_rateable()
        node = Mock()
        node.children = [named_object('object')]
        value = {'subject': subject, 'object': object, 'rate': '1'}
        with raises(colander.Invalid):
            _ensure_resource_is_unique(node, value, request_, IRate, 'rate')


@mark.usefixtures('integration')
class TestRateValidators:

    def test_rateable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        rateable = _make_rateable()
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is True
        assert validator.validate(2) is False
        assert validator.validate(-2) is False


@mark.usefixtures('integration')
def test_includeme_register_rate_sheet(config, context):
    from adhocracy_core.sheets.rate import IRate
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IRate)
    inst = get_sheet(context, IRate)
    assert inst.meta.isheet is IRate


class TestLikeableSheet:

    @fixture
    def meta(self):
        from .rate import likeable_meta
        return likeable_meta

    @fixture
    def inst(self, pool, service):
        pool['likes'] = service
        from adhocracy_core.sheets.rate import likeable_meta
        return likeable_meta.sheet_class(likeable_meta, pool)

    def test_create(self, inst):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        from adhocracy_core.sheets.rate import ILikeable
        from adhocracy_core.sheets.rate import LikeableSchema
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == ILikeable
        assert inst.meta.schema_class == LikeableSchema
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, inst):
        post_pool = inst.context['likes']
        assert inst.get() == {'post_pool': post_pool,
                              'likes': [],
                              }

    @mark.usefixtures('integration')
    def test_includeme(self, meta):
        from adhocracy_core.utils import get_sheet
        context = testing.DummyResource(__provides__=meta.isheet)
        assert get_sheet(context, meta.isheet)


class TestLikeSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.rate import like_meta
        return like_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.rate import ILike
        from adhocracy_core.sheets.rate import LikeSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        inst = meta.sheet_class(meta, context)
        assert issubclass(meta.sheet_class, AttributeResourceSheet)
        assert inst.meta.isheet == ILike
        assert inst.meta.schema_class == LikeSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': None,
                              'object': None,
                              'like': 0,
                              }

def _make_likeable():
    return testing.DummyResource(__provides__=ILikeable)

@mark.usefixtures('integration')
class TestLikeSchema:

    @fixture
    def schema_with_mock_ensure_like(self, monkeypatch, request_, context):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import LikeSchema
        mock = Mock()
        monkeypatch.setattr(rate, '_ensure_like_is_unique', mock)
        schema = LikeSchema().bind(request=request_, context=context)
        return schema

    @fixture
    def subject(self, monkeypatch):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanLike
        subject = testing.DummyResource(__provides__=ICanLike)
        mock_get_user = Mock(return_value=subject)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        return subject

    def test_deserialize_valid(self, context, schema_with_mock_ensure_like,
                               subject):
        context['subject'] = subject
        object = _make_likeable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'like': '1'}
        assert schema_with_mock_ensure_like.deserialize(data) == {
            'subject': subject, 'object': object, 'like': 1}

    def test_deserialize_invalid_like(self, context,
                                      schema_with_mock_ensure_like, subject):
        context['subject'] = subject
        object = _make_likeable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'like': '77'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_deserialize_invalid_subject(self, context,
                                         schema_with_mock_ensure_like):
        subject = testing.DummyResource()
        context['subject'] = subject
        object = _make_likeable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'like': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_deserialize_invalid_subject_missing(self, context,
                                                 schema_with_mock_ensure_like):
        object = _make_likeable()
        context['object'] = object
        data = {'subject': '', 'object': '/object', 'like': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_deserialize_subject_isnt_current_user(
            self, context, monkeypatch, schema_with_mock_ensure_like):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanLike
        subject = testing.DummyResource(__provides__=ICanLike)
        user = testing.DummyResource(__provides__=ICanLike)
        mock_get_user = Mock(return_value=user)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        context['subject'] = subject
        object = _make_likeable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'like': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_deserialize_invalid_object(self, context,
                                        schema_with_mock_ensure_like,
                                        subject):
        context['subject'] = subject
        object = testing.DummyResource()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'like': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_deserialize_invalid_object_missing(self, context,
                                        schema_with_mock_ensure_like, subject):
        context['subject'] = subject
        data = {'subject': '/subject', 'object': '', 'like': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_like.deserialize(data)

    def test_ensure_like_is_unique_ok(self, monkeypatch, request_,
                                      context, subject):
        from adhocracy_core.sheets.rate import _ensure_like_is_unique
        from adhocracy_core.sheets.rate import LikeSchema
        from adhocracy_core.sheets.rate import ILike
        from adhocracy_core.sheets import rate
        mock_find_catalog = Mock(return_value={'reference': DummyIndex(),
                                               'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = LikeSchema().bind(request=request_, context=context)
        object = _make_likeable()
        node = Mock()
        value = {'subject': subject, 'object': object, 'like': '1'}
        result = _ensure_like_is_unique(node, value, request_)
        assert result is None

    def test_ensure_like_is_unique_error(self, monkeypatch, request_,
                                         context, subject):
        from adhocracy_core.sheets.rate import ILike
        from adhocracy_core.sheets.rate import LikeSchema
        from adhocracy_core.sheets.rate import _ensure_resource_is_unique
        from adhocracy_core.sheets import rate
        from adhocracy_core.utils import named_object
        mock_find_catalog = Mock(
            return_value={'reference': DummyIndex(['dummy']),
                          'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = LikeSchema().bind(request=request_, context=context)
        object = _make_likeable()
        node = Mock()
        node.children = [named_object('object')]
        value = {'subject': subject, 'object': object, 'like': '1'}
        with raises(colander.Invalid):
            _ensure_resource_is_unique(node, value, request_, ILike, 'like')
