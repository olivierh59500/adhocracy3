from unittest.mock import Mock
from pytest import fixture
from pytest import mark
from pytest import raises


class TestBadge:

    @fixture
    def meta(self):
        from .badge import badge_meta
        return badge_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IBadge
        assert meta.use_autonaming is False
        assert meta.extended_sheets == (sheets.description.IDescription,
                                        sheets.badge.IBadge,
                                        sheets.name.IName,)
        assert meta.permission_create == 'create_badge'

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

class TestBadgeGroup:

    @fixture
    def meta(self):
        from .badge import badge_group_meta
        return badge_group_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IBadgeGroup
        assert meta.extended_sheets == (sheets.description.IDescription,
                                        )
        assert meta.permission_create == 'create_badge_group'
        assert meta.element_types == (resources.badge.IBadge,
                                      meta.iresource,
                                      )

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestParticipantsAssignableBadgeGroup:

    @fixture
    def meta(self):
        from .badge import participants_assignable_badge_group_meta
        return participants_assignable_badge_group_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IParticipantsAssignableBadgeGroup
        assert meta.iresource.isOrExtends(resources.badge.IBadgeGroup)
        assert meta.extended_sheets == (sheets.description.IDescription,
                                        )
        assert meta.permission_create == 'create_badge_group'
        assert meta.element_types == (resources.badge.IBadge,
                                      resources.badge.IBadgeGroup,
                                      meta.iresource,
                                      )
        assert meta.default_workflow == 'badge_assignment'

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

class TestBadgesService:

    @fixture
    def meta(self):
        from .badge import badges_service_meta
        return badges_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from adhocracy_core import resources
        assert meta.iresource is resources.badge.IBadgesService
        assert meta.iresource.extends(IServicePool)
        assert meta.element_types == (resources.badge.IBadge,
                                      resources.badge.IBadgeGroup,
                                      )
        assert meta.content_name == 'badges'
        assert meta.permission_create == 'create_service'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

    @mark.usefixtures('integration')
    def test_add_badge_assignments_service(self, pool, registry):
        from substanced.util import find_service
        from .badge import add_badges_service
        add_badges_service(pool, registry, {})
        assert find_service(pool, 'badges')


class TestBadgeAssignment:

    @fixture
    def meta(self):
        from .badge import badge_assignment_meta
        return badge_assignment_meta

    def test_meta(self, meta):
        from adhocracy_core import resources
        from adhocracy_core import sheets
        assert meta.iresource is resources.badge.IBadgeAssignment
        assert meta.basic_sheets == (sheets.metadata.IMetadata,
                                     sheets.badge.IBadgeAssignment,
                                     sheets.description.IDescription
                                    )
        assert meta.permission_create == 'create_badge_assignment'
        assert meta.use_autonaming
        assert meta.autonaming_prefix == ''

    @mark.usefixtures('integration')
    def test_create(self, context, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)


class TestBadgeAssignmentsService:

    @fixture
    def meta(self):
        from .badge import badge_assignments_service_meta
        return badge_assignments_service_meta

    def test_meta(self, meta):
        from adhocracy_core.interfaces import IServicePool
        from adhocracy_core import resources
        assert meta.iresource is resources.badge.IBadgeAssignmentsService
        assert meta.iresource.extends(IServicePool)
        assert meta.element_types == (resources.badge.IBadgeAssignment,)
        assert meta.content_name == 'badge_assignments'
        assert meta.permission_create == 'create_service'

    @mark.usefixtures('integration')
    def test_create(self, registry, meta):
        assert registry.content.create(meta.iresource.__identifier__)

    @mark.usefixtures('integration')
    def test_add_badge_assignments_service(self, pool, registry):
        from substanced.util import find_service
        from .badge import add_badge_assignments_service
        add_badge_assignments_service(pool, registry, {})
        assert find_service(pool, 'badge_assignments')
