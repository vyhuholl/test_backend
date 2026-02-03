"""Tests for API routes."""

from app.models.activity import Activity
from app.models.building import Building
from app.models.organisation import Organisation


class TestOrganisationRoutes:
    """Test organisation API routes."""

    async def test_get_organisation_by_id(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test GET /organisations/{id}."""
        response = await authenticated_client.get(
            f"/organisations/{sample_organisation.id}",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_organisation.id
        assert data["name"] == sample_organisation.name

    async def test_get_organisation_not_found(self, authenticated_client):
        """Test GET /organisations/{id} with non-existent ID."""
        response = await authenticated_client.get("/organisations/999")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_get_organisations_by_building(
        self,
        authenticated_client,
        db_session,
        sample_building,
    ):
        """Test GET /organisations/by-building/{building_id}."""
        # Create organisations in the building
        org1 = Organisation(name="Org 1", building_id=sample_building.id)
        org2 = Organisation(name="Org 2", building_id=sample_building.id)
        db_session.add_all([org1, org2])
        await db_session.commit()

        response = await authenticated_client.get(
            f"/organisations/by-building/{sample_building.id}",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        org_names = [o["name"] for o in data]
        assert "Org 1" in org_names
        assert "Org 2" in org_names

    async def test_get_organisations_by_activity(
        self,
        authenticated_client,
        db_session,
        sample_activity,
    ):
        """Test GET /organisations/by-activity/{activity_id}."""
        # Create building
        building = Building(
            address="Test Address",
            latitude=55.0,
            longitude=37.0,
        )
        db_session.add(building)
        await db_session.commit()
        await db_session.refresh(building)

        # Create organisations with the activity
        org1 = Organisation(name="Org 1", building_id=building.id)
        org2 = Organisation(name="Org 2", building_id=building.id)
        org1.activities.append(sample_activity)
        org2.activities.append(sample_activity)
        db_session.add_all([org1, org2])
        await db_session.commit()

        response = await authenticated_client.get(
            f"/organisations/by-activity/{sample_activity.id}",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        org_names = [o["name"] for o in data]
        assert "Org 1" in org_names
        assert "Org 2" in org_names

    async def test_search_organisations_by_name(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test GET /organisations/search with name parameter."""
        response = await authenticated_client.get(
            f"/organisations/search?name={sample_organisation.name}",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_search_organisations_by_radius(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test GET /organisations/search with radius parameter."""
        lat = sample_organisation.building.latitude
        lon = sample_organisation.building.longitude
        response = await authenticated_client.get(
            f"/organisations/search?lat={lat}&lon={lon}&radius=10",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_search_organisations_by_area(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test GET /organisations/search with area parameters."""
        lat = sample_organisation.building.latitude
        lon = sample_organisation.building.longitude
        response = await authenticated_client.get(
            f"/organisations/search?min_lat={lat - 1}&max_lat={lat + 1}"
            f"&min_lon={lon - 1}&max_lon={lon + 1}",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_search_organisations_radius_without_lat_lon(
        self,
        authenticated_client,
    ):
        """Test GET /organisations/search with radius but no lat/lon."""
        response = await authenticated_client.get(
            "/organisations/search?radius=10",
        )

        assert response.status_code == 400
        data = response.json()
        # Custom HTTPException returns {"detail": "..."}
        detail = data.get("detail", "Unknown error")
        assert "lat" in detail.lower()

    async def test_search_organisations_partial_area_params(
        self,
        authenticated_client,
    ):
        """Test GET /organisations/search with partial area parameters."""
        response = await authenticated_client.get(
            "/organisations/search?min_lat=0&max_lat=1",
        )

        assert response.status_code == 400
        data = response.json()
        # Custom HTTPException returns {"detail": "..."}
        detail = data.get("detail", "Unknown error")
        assert "area" in detail.lower()

    async def test_get_organisations_without_auth(self, client):
        """Test GET /organisations/{id} without authentication."""
        response = await client.get("/organisations/1")

        assert response.status_code == 401

    async def test_get_organisations_invalid_auth(self, authenticated_client):
        """Test GET /organisations/{id} with invalid API key."""
        response = await authenticated_client.get(
            "/organisations/1",
            headers={"X-API-Key": "invalid-key"},
        )

        assert response.status_code == 401


class TestBuildingRoutes:
    """Test building API routes."""

    async def test_get_buildings(
        self,
        authenticated_client,
        sample_building,
    ):
        """Test GET /buildings."""
        response = await authenticated_client.get("/buildings")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert sample_building.address in [b["address"] for b in data]

    async def test_get_buildings_without_auth(self, client):
        """Test GET /buildings without authentication."""
        response = await client.get("/buildings")

        assert response.status_code == 401


class TestActivityRoutes:
    """Test activity API routes."""

    async def test_get_activities(
        self,
        authenticated_client,
        sample_activity,
    ):
        """Test GET /activities."""
        response = await authenticated_client.get("/activities")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert sample_activity.name in [a["name"] for a in data]

    async def test_get_activity_tree(
        self,
        authenticated_client,
        db_session,
    ):
        """Test GET /activities/tree."""
        # Create activity hierarchy
        parent = Activity(name="Parent")
        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)

        child = Activity(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()
        await db_session.refresh(child)

        response = await authenticated_client.get("/activities/tree")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Check that parent has children
        parent_node = next((n for n in data if n["name"] == "Parent"), None)
        assert parent_node is not None
        assert len(parent_node["children"]) >= 1

    async def test_get_activities_without_auth(self, client):
        """Test GET /activities without authentication."""
        response = await client.get("/activities")

        assert response.status_code == 401


class TestAPIResponseFormat:
    """Test API response format."""

    async def test_json_content_type(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test that responses have JSON content type."""
        response = await authenticated_client.get(
            f"/organisations/{sample_organisation.id}",
        )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    async def test_json_response_structure(
        self,
        authenticated_client,
        sample_organisation,
    ):
        """Test that responses have correct JSON structure."""
        response = await authenticated_client.get(
            f"/organisations/{sample_organisation.id}",
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data
