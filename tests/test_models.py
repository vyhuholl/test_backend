"""Tests for database models."""

import pytest

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
        await db_session.refresh(parent)

        # Create child activity
        child = Activity(name="Child Activity", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)

        assert child.parent_id == parent.id
        assert child.parent == parent
        assert child in parent.children

    async def test_activity_get_descendants(self, db_session):
        """Test get_descendants method."""
        # Create hierarchy: parent -> child -> grandchild
        parent = Activity(name="Parent")
        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)

        child = Activity(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)

        grandchild = Activity(name="Grandchild", parent_id=child.id)
        db_session.add(grandchild)
        await db_session.commit()
        await db_session.refresh(grandchild)

        # Get descendants from parent
        descendants = parent.get_descendants()
        assert len(descendants) == 2
        assert child in descendants
        assert grandchild in descendants

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
        await db_session.refresh(organisation)

        assert len(organisation.phones) == 2
        assert phone1 in organisation.phones
        assert phone2 in organisation.phones

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
        await db_session.refresh(organisation)

        assert sample_activity in organisation.activities
        assert organisation in sample_activity.organisations

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
        await db_session.refresh(organisation)
        await db_session.refresh(sample_building)

        assert organisation in sample_building.organisations


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
