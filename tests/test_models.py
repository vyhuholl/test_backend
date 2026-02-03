"""Tests for database models."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.models.building import Building
from app.models.organisation import Organisation, OrganisationPhone


class TestActivity:
    """Test Activity model."""

    async def test_activity_creation(self, db_session):
        """Test creating an activity."""
        activity = Activity(name="Test Activity")
        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        assert activity.id is not None
        assert activity.name == "Test Activity"
        assert activity.parent_id is None

    async def test_activity_hierarchy(self, db_session):
        """Test activity hierarchy (parent-child relationships)."""
        # Create parent activity
        parent = Activity(name="Parent Activity")
        db_session.add(parent)
        await db_session.commit()

        # Create child activity
        child = Activity(name="Child Activity", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()

        # Refresh with eager loading to avoid MissingGreenlet error
        stmt = select(Activity).options(
            selectinload(Activity.children),
            selectinload(Activity.parent),
        )
        result = await db_session.execute(stmt)
        activities = result.scalars().all()
        parent = activities[0]
        child = activities[1]

        assert child.parent_id == parent.id
        assert child.parent == parent
        assert child in parent.children

    async def test_activity_get_descendants(self, db_session):
        """Test get_descendants method."""
        # Create hierarchy: parent -> child -> grandchild
        parent = Activity(name="Parent")
        db_session.add(parent)
        await db_session.commit()

        child = Activity(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()

        grandchild = Activity(name="Grandchild", parent_id=child.id)
        db_session.add(grandchild)
        await db_session.commit()

        # Get descendants from parent (async method)
        descendants = await parent.get_descendants(db_session)
        assert len(descendants) == 2
        assert child.id in [d.id for d in descendants]
        assert grandchild.id in [d.id for d in descendants]

    async def test_activity_get_level(self, db_session):
        """Test get_level method."""
        # Create 3-level hierarchy
        level0 = Activity(name="Level 0")
        db_session.add(level0)
        await db_session.commit()
        await db_session.refresh(level0)

        level1 = Activity(name="Level 1", parent_id=level0.id)
        db_session.add(level1)
        await db_session.commit()
        await db_session.refresh(level1)

        level2 = Activity(name="Level 2", parent_id=level1.id)
        db_session.add(level2)
        await db_session.commit()
        await db_session.refresh(level2)

        assert level0.get_level() == 0
        assert level1.get_level() == 1
        assert level2.get_level() == 2

    async def test_activity_repr(self, db_session):
        """Test Activity __repr__ method."""
        activity = Activity(name="Test Activity")
        db_session.add(activity)
        await db_session.commit()
        await db_session.refresh(activity)

        repr_str = repr(activity)
        assert "Activity" in repr_str
        assert str(activity.id) in repr_str
        assert "Test Activity" in repr_str


class TestBuilding:
    """Test Building model."""

    async def test_building_creation(self, db_session):
        """Test creating a building."""
        building = Building(
            address="123 Test Street",
            latitude=55.7558,
            longitude=37.6173,
        )
        db_session.add(building)
        await db_session.commit()
        await db_session.refresh(building)

        assert building.id is not None
        assert building.address == "123 Test Street"
        assert building.latitude == 55.7558
        assert building.longitude == 37.6173

    async def test_building_repr(self, db_session):
        """Test Building __repr__ method."""
        building = Building(
            address="123 Test Street",
            latitude=55.7558,
            longitude=37.6173,
        )
        db_session.add(building)
        await db_session.commit()
        await db_session.refresh(building)

        repr_str = repr(building)
        assert "Building" in repr_str
        assert str(building.id) in repr_str
        assert "123 Test Street" in repr_str


class TestOrganisation:
    """Test Organisation model."""

    async def test_organisation_creation(self, db_session, sample_building):
        """Test creating an organisation."""
        organisation = Organisation(
            name="Test Organisation",
            building_id=sample_building.id,
        )
        db_session.add(organisation)
        await db_session.commit()
        await db_session.refresh(organisation)

        assert organisation.id is not None
        assert organisation.name == "Test Organisation"
        assert organisation.building_id == sample_building.id
        assert organisation.building == sample_building

    async def test_organisation_with_phones(self, db_session, sample_building):
        """Test organisation with phone numbers."""
        organisation = Organisation(
            name="Test Organisation",
            building_id=sample_building.id,
        )
        phone1 = OrganisationPhone(phone_number="+7-123-456-7890")
        phone2 = OrganisationPhone(phone_number="+7-987-654-3210")
        organisation.phones.extend([phone1, phone2])

        db_session.add(organisation)
        await db_session.commit()

        # Refresh with eager loading to avoid MissingGreenlet error
        stmt = (
            select(Organisation)
            .options(
                selectinload(Organisation.phones),
            )
            .where(Organisation.id == organisation.id)
        )
        result = await db_session.execute(stmt)
        organisation = result.scalar_one_or_none()

        assert len(organisation.phones) == 2
        assert phone1.id in [p.id for p in organisation.phones]
        assert phone2.id in [p.id for p in organisation.phones]

    async def test_organisation_with_activities(
        self,
        db_session,
        sample_building,
        sample_activity,
    ):
        """Test organisation with activities."""
        organisation = Organisation(
            name="Test Organisation",
            building_id=sample_building.id,
        )
        organisation.activities.append(sample_activity)

        db_session.add(organisation)
        await db_session.commit()

        # Refresh with eager loading to avoid MissingGreenlet error
        stmt = (
            select(Organisation)
            .options(
                selectinload(Organisation.activities),
            )
            .where(Organisation.id == organisation.id)
        )
        result = await db_session.execute(stmt)
        organisation = result.scalar_one_or_none()

        assert sample_activity.id in [a.id for a in organisation.activities]

        # Also check the reverse relationship
        stmt2 = (
            select(Activity)
            .options(
                selectinload(Activity.organisations),
            )
            .where(Activity.id == sample_activity.id)
        )
        result2 = await db_session.execute(stmt2)
        activity = result2.scalar_one_or_none()
        assert organisation.id in [o.id for o in activity.organisations]

    async def test_organisation_building_relationship(
        self,
        db_session,
        sample_building,
    ):
        """Test organisation-building relationship."""
        organisation = Organisation(
            name="Test Organisation",
            building_id=sample_building.id,
        )
        db_session.add(organisation)
        await db_session.commit()

        # Refresh with eager loading to avoid MissingGreenlet error
        stmt = (
            select(Building)
            .options(
                selectinload(Building.organisations),
            )
            .where(Building.id == sample_building.id)
        )
        result = await db_session.execute(stmt)
        building = result.scalar_one_or_none()

        assert organisation.id in [o.id for o in building.organisations]


class TestOrganisationPhone:
    """Test OrganisationPhone model."""

    async def test_phone_creation(self, db_session, sample_organisation):
        """Test creating a phone number."""
        phone = OrganisationPhone(
            organisation_id=sample_organisation.id,
            phone_number="+7-123-456-7890",
        )
        db_session.add(phone)
        await db_session.commit()
        await db_session.refresh(phone)

        assert phone.id is not None
        assert phone.phone_number == "+7-123-456-7890"
        assert phone.organisation_id == sample_organisation.id
        assert phone.organisation == sample_organisation
