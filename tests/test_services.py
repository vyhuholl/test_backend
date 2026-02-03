"""Tests for service layer."""

import pytest

from app.models.activity import Activity
from app.models.building import Building
from app.models.organisation import Organisation, OrganisationPhone
from app.services.activity_service import ActivityService
from app.services.building_service import BuildingService
from app.services.organisation_service import OrganisationService


class TestActivityService:
    """Test ActivityService."""

    async def test_get_all(self, db_session, sample_activity):
        """Test getting all activities."""
        service = ActivityService(db_session)
        activities = [a async for a in service.get_all()]

        assert len(activities) >= 1
        assert sample_activity in activities

    async def test_get_by_id(self, db_session, sample_activity):
        """Test getting activity by ID."""
        service = ActivityService(db_session)
        activity = await service.get_by_id(sample_activity.id)

        assert activity is not None
        assert activity.id == sample_activity.id
        assert activity.name == sample_activity.name

    async def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent activity."""
        service = ActivityService(db_session)
        activity = await service.get_by_id(999)

        assert activity is None

    async def test_get_descendants(self, db_session):
        """Test getting descendant activities."""
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

        service = ActivityService(db_session)
        descendants = await service.get_descendants(parent.id)

        assert len(descendants) == 2
        descendant_ids = [d.id for d in descendants]
        assert child.id in descendant_ids
        assert grandchild.id in descendant_ids

    async def test_get_descendants_not_found(self, db_session):
        """Test getting descendants of non-existent activity."""
        service = ActivityService(db_session)
        descendants = await service.get_descendants(999)

        assert descendants == []

    async def test_get_activity_tree(self, db_session):
        """Test getting activity tree."""
        # Create hierarchy
        parent = Activity(name="Parent")
        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)

        child = Activity(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)

        service = ActivityService(db_session)
        tree = await service.get_activity_tree()

        assert len(tree) == 1
        assert tree[0]["id"] == parent.id
        assert tree[0]["name"] == "Parent"
        assert len(tree[0]["children"]) == 1
        assert tree[0]["children"][0]["id"] == child.id


class TestBuildingService:
    """Test BuildingService."""

    async def test_get_all(self, db_session, sample_building):
        """Test getting all buildings."""
        service = BuildingService(db_session)
        buildings = [b async for b in service.get_all()]

        assert len(buildings) >= 1
        assert sample_building in buildings

    async def test_get_by_id(self, db_session, sample_building):
        """Test getting building by ID."""
        service = BuildingService(db_session)
        building = await service.get_by_id(sample_building.id)

        assert building is not None
        assert building.id == sample_building.id
        assert building.address == sample_building.address

    async def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent building."""
        service = BuildingService(db_session)
        building = await service.get_by_id(999)

        assert building is None


class TestOrganisationService:
    """Test OrganisationService."""

    async def test_get_by_id(self, db_session, sample_organisation):
        """Test getting organisation by ID."""
        service = OrganisationService(db_session)
        org = await service.get_by_id(sample_organisation.id)

        assert org is not None
        assert org.id == sample_organisation.id
        assert org.name == sample_organisation.name
        assert org.building is not None
        assert org.building.id == sample_organisation.building_id

    async def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent organisation."""
        service = OrganisationService(db_session)
        org = await service.get_by_id(999)

        assert org is None

    async def test_get_by_building(self, db_session, sample_building):
        """Test getting organisations by building."""
        # Create multiple organisations in the same building
        org1 = Organisation(name="Org 1", building_id=sample_building.id)
        org2 = Organisation(name="Org 2", building_id=sample_building.id)
        db_session.add_all([org1, org2])
        await db_session.commit()
        await db_session.refresh(org1)
        await db_session.refresh(org2)

        service = OrganisationService(db_session)
        organisations = [o async for o in service.get_by_building(sample_building.id)]

        assert len(organisations) == 2
        org_names = [o.name for o in organisations]
        assert "Org 1" in org_names
        assert "Org 2" in org_names

    async def test_get_by_activity(self, db_session, sample_activity):
        """Test getting organisations by activity."""
        # Create multiple organisations with the same activity
        building = Building(
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
        )
        db_session.add(building)
        await db_session.commit()
        await db_session.refresh(building)

        org1 = Organisation(name="Org 1", building_id=building.id)
        org2 = Organisation(name="Org 2", building_id=building.id)
        org1.activities.append(sample_activity)
        org2.activities.append(sample_activity)
        db_session.add_all([org1, org2])
        await db_session.commit()
        await db_session.refresh(org1)
        await db_session.refresh(org2)

        service = OrganisationService(db_session)
        organisations = [o async for o in service.get_by_activity(sample_activity.id)]

        assert len(organisations) == 2
        org_names = [o.name for o in organisations]
        assert "Org 1" in org_names
        assert "Org 2" in org_names

    async def test_get_by_activity_with_descendants(self, db_session):
        """Test getting organisations by activity including descendants."""
        # Create activity hierarchy
        parent = Activity(name="Parent")
        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)

        child = Activity(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)

        # Create building
        building = Building(
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
        )
        db_session.add(building)
        await db_session.commit()
        await db_session.refresh(building)

        # Create organisation with child activity
        org = Organisation(name="Test Org", building_id=building.id)
        org.activities.append(child)
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)

        service = OrganisationService(db_session)
        # Search by parent activity should find org with child activity
        organisations = [o async for o in service.get_by_activity(parent.id)]

        assert len(organisations) == 1
        assert organisations[0].name == "Test Org"

    async def test_search_by_name(self, db_session, sample_organisation):
        """Test searching organisations by name."""
        service = OrganisationService(db_session)
        organisations = [
            o async for o in service.search_by_name(sample_organisation.name)
        ]

        assert len(organisations) >= 1
        assert sample_organisation.name in [o.name for o in organisations]

    async def test_search_by_name_partial(self, db_session, sample_organisation):
        """Test searching organisations by partial name."""
        service = OrganisationService(db_session)
        organisations = [
            o async for o in service.search_by_name(sample_organisation.name[:4])
        ]

        assert len(organisations) >= 1

    async def test_search_by_radius(self, db_session, sample_organisation):
        """Test searching organisations by radius."""
        service = OrganisationService(db_session)
        organisations = [
            o
            async for o in service.search_by_radius(
                lat=sample_organisation.building.latitude,
                lon=sample_organisation.building.longitude,
                radius_km=10,
            )
        ]

        assert len(organisations) >= 1

    async def test_search_by_radius_no_results(self, db_session):
        """Test searching organisations by radius with no results."""
        service = OrganisationService(db_session)
        organisations = [
            o
            async for o in service.search_by_radius(
                lat=0.0,
                lon=0.0,
                radius_km=1,
            )
        ]

        assert len(organisations) == 0

    async def test_search_by_area(self, db_session, sample_organisation):
        """Test searching organisations by rectangular area."""
        service = OrganisationService(db_session)
        lat = sample_organisation.building.latitude
        lon = sample_organisation.building.longitude
        organisations = [
            o
            async for o in service.search_by_area(
                min_lat=lat - 1,
                max_lat=lat + 1,
                min_lon=lon - 1,
                max_lon=lon + 1,
            )
        ]

        assert len(organisations) >= 1

    async def test_search_by_area_no_results(self, db_session):
        """Test searching organisations by area with no results."""
        service = OrganisationService(db_session)
        organisations = [
            o
            async for o in service.search_by_area(
                min_lat=0.0,
                max_lat=1.0,
                min_lon=0.0,
                max_lon=1.0,
            )
        ]

        assert len(organisations) == 0

    async def test_search_combined_filters(self, db_session, sample_organisation):
        """Test searching with combined filters."""
        service = OrganisationService(db_session)
        lat = sample_organisation.building.latitude
        lon = sample_organisation.building.longitude
        organisations = [
            o
            async for o in service.search(
                name=sample_organisation.name[:4],
                lat=lat,
                lon=lon,
                radius_km=10,
            )
        ]

        assert len(organisations) >= 1

    async def test_haversine_distance(self, db_session):
        """Test Haversine distance calculation."""
        service = OrganisationService(db_session)
        # Distance between Moscow coordinates (should be ~0)
        distance = service._haversine_distance(55.7558, 37.6173, 55.7558, 37.6173)
        assert distance == 0.0

        # Distance between Moscow and St. Petersburg (approximately 630 km)
        distance = service._haversine_distance(
            55.7558, 37.6173,  # Moscow
            59.9343, 30.3351,  # St. Petersburg
        )
        assert 600 < distance < 700
