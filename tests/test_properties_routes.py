from datetime import date
from app.models.groupChat import GroupChat
from app.models.property import Property
from app.models.tenancy import Tenancy

class TestCreateProperty:
    """Tests for POST /api/properties endpoint."""
    
    def test_success(self, client, session, landlord_token):
        """Test successful property creation by a landlord."""
        payload = {
            "address": "123 Test Street"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}
        
        response = client.post(
            "/api/properties",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 201
        assert response.json["address"] == "123 Test Street"
        
        # Verify database entries
        property = session.query(Property).first()
        assert property is not None
        assert property.address == "123 Test Street"

    def test_unauthorized_role(self, client, auth_token):
        """Test property creation by an unauthorized user (tenant)."""
        payload = {
            "address": "123 Test Street"
        }
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.post(
            "/api/properties",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_missing_address(self, client, landlord_token):
        """Test property creation with missing address."""
        payload = {}
        headers = {"Authorization": f"Bearer {landlord_token}"}
        
        response = client.post(
            "/api/properties",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 400
        assert response.json["error"] == "Missing property details"

    def test_no_token(self, client):
        """Test property creation without authentication token."""
        payload = {
            "address": "123 Test Street"
        }
        
        response = client.post(
            "/api/properties",
            json=payload
        )
        
        assert response.status_code == 401

    def test_database_error(self, client, session, landlord_token, mocker):
        """Test property creation with database error."""
        payload = {
            "address": "123 Test Street"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}
        
        mocker.patch.object(session, 'commit', side_effect=Exception("Database error"))
        
        response = client.post(
            "/api/properties",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 500
        assert response.json["error"] == "An error occurred while creating the property."


class TestGetProperties:
    """Tests for GET /api/properties endpoint."""

    def test_success(self, client, session, landlord_token, test_landlord_1):
        """Test successful retrieval of all properties for a landlord."""
        properties = [
            Property(address="123 Main Street", landlord_id=test_landlord_1.user_id),
            Property(address="456 Elm Street", landlord_id=test_landlord_1.user_id)
        ]
        session.add_all(properties)
        session.commit()

        headers = {"Authorization": f"Bearer {landlord_token}"}
        response = client.get("/api/properties", headers=headers)

        assert response.status_code == 200
        assert response.json["total"] == 2
        assert len(response.json["properties"]) == 2
        assert response.json["properties"][0]["address"] == "123 Main Street"
        assert response.json["properties"][1]["address"] == "456 Elm Street"

    def test_pagination(self, client, session, landlord_token, test_landlord_1):
        """Test pagination when retrieving properties."""
        for i in range(15):
            property = Property(address=f"Property {i}", landlord_id=test_landlord_1.user_id)
            session.add(property)
        session.commit()

        headers = {"Authorization": f"Bearer {landlord_token}"}
        
        # Test first page
        response = client.get("/api/properties?page=1&per_page=10", headers=headers)
        assert response.status_code == 200
        assert response.json["total"] == 15
        assert response.json["page"] == 1
        assert response.json["per_page"] == 10
        assert len(response.json["properties"]) == 10

        # Test second page
        response = client.get("/api/properties?page=2&per_page=10", headers=headers)
        assert response.status_code == 200
        assert response.json["page"] == 2
        assert len(response.json["properties"]) == 5

    def test_filter_by_status(self, client, session, landlord_token, test_landlord_1):
        """Test filtering properties by status."""
        properties = [
            Property(address="123 Main Street", landlord_id=test_landlord_1.user_id, status="rented"),
            Property(address="456 Elm Street", landlord_id=test_landlord_1.user_id, status="vacant")
        ]
        session.add_all(properties)
        session.commit()

        headers = {"Authorization": f"Bearer {landlord_token}"}

        # Test rented properties
        response = client.get("/api/properties?status=rented", headers=headers)
        assert response.status_code == 200
        assert response.json["total"] == 1
        assert response.json["properties"][0]["address"] == "123 Main Street"
        assert response.json["properties"][0]["status"] == "rented"

        # Test vacant properties
        response = client.get("/api/properties?status=vacant", headers=headers)
        assert response.status_code == 200
        assert response.json["total"] == 1
        assert response.json["properties"][0]["address"] == "456 Elm Street"
        assert response.json["properties"][0]["status"] == "vacant"

    def test_unauthorized(self, client, auth_token):
        """Test that unauthorized users cannot access landlord properties."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/properties", headers=headers)

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_no_token(self, client):
        """Test accessing properties without authentication."""
        response = client.get("/api/properties")

        assert response.status_code == 401

class TestGetProperty:
    """Tests for GET /api/properties/<property_id> endpoint."""

    def test_success(self, client, session, landlord_token, test_landlord_1):
        """Test successful retrieval of a specific property."""
        property = Property(address="789 Pine Street", landlord_id=test_landlord_1.user_id)
        session.add(property)
        session.commit()

        headers = {"Authorization": f"Bearer {landlord_token}"}
        response = client.get(f"/api/properties/{property.property_id}", headers=headers)

        assert response.status_code == 200
        assert response.json["address"] == "789 Pine Street"

    def test_property_not_found(self, client, landlord_token):
        """Test retrieval of a non-existing property."""
        headers = {"Authorization": f"Bearer {landlord_token}"}
        response = client.get("/api/properties/999", headers=headers)  # Assuming ID 999 does not exist

        assert response.status_code == 404
        assert response.json["error"] == "Property not found"

    def test_unauthorized_access(self, client, auth_token, session, test_landlord_1):
        """Test unauthorized access to a property by another user."""
        property = Property(address="101 Main Street", landlord_id=test_landlord_1.user_id)
        session.add(property)
        session.commit()

        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get(f"/api/properties/{property.property_id}", headers=headers)

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_no_token(self, client, session, test_landlord_1):
        """Test accessing property details without an authentication token."""
        property = Property(address="202 Main Street", landlord_id=test_landlord_1.user_id)
        session.add(property)
        session.commit()

        response = client.get(f"/api/properties/{property.property_id}")

        assert response.status_code == 401
        assert response.json.get("msg") == "Missing Authorization Header"

    def test_database_error(self, client, landlord_token, mocker, session, test_landlord_1):
        """Test server error due to database issues during property retrieval."""
        # Add a property to the session for context
        property = Property(address="303 Elm Street", landlord_id=test_landlord_1.user_id)
        session.add(property)
        session.commit()

        headers = {"Authorization": f"Bearer {landlord_token}"}

        # Patch the query filter_by method and the first method
        mock_query = mocker.MagicMock()
        mock_query.filter_by.return_value.first.side_effect = Exception("Database error")
        mocker.patch("app.models.property.Property.query", new=mock_query)

        response = client.get(f"/api/properties/{property.property_id}", headers=headers)

        # Verify the response for server error
        assert response.status_code == 500
        assert response.json["error"] == "An error occurred while retrieving the property."


class TestUpdateProperty:
    """Tests for PUT /api/properties/<property_id> endpoint."""

    def test_update_property_success(self, client, session, landlord_token, test_property_1):
        """Test successful update of a property's address."""
        payload = {"address": "456 Updated Street"}
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            f"/api/properties/{test_property_1.property_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 200
        assert response.json["address"] == "456 Updated Street"

        updated_property = session.get(Property, test_property_1.property_id)
        assert updated_property.address == "456 Updated Street"

    def test_update_property_unauthorized(self, client, auth_token, session, test_property_1):
        """Test unauthorized update of a property's address."""
        payload = {"address": "456 Unauthorized Street"}
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.put(
            f"/api/properties/{test_property_1.property_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

        # Verify the property remains unchanged
        unchanged_property = session.get(Property, test_property_1.property_id)
        assert unchanged_property.address == "123 Test Street"

    def test_update_property_not_found(self, client, landlord_token):
        """Test update of a non-existent property."""
        payload = {"address": "456 Nonexistent Street"}
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.put(
            "/api/properties/999",  # Assuming ID 999 does not exist
            json=payload,
            headers=headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Property not found"

    def test_update_property_no_token(self, client, test_property_1):
        """Test update without authentication token."""
        payload = {"address": "456 No Token Street"}

        response = client.put(
            f"/api/properties/{test_property_1.property_id}",
            json=payload
        )

        assert response.status_code == 401
        assert response.json["msg"] == "Missing Authorization Header"

    def test_update_property_database_error(self, client, session, landlord_token, mocker, test_property_1):
        """Test server error during property update."""
        payload = {"address": "456 DB Error Street"}
        headers = {"Authorization": f"Bearer {landlord_token}"}

        mocker.patch.object(session, "commit", side_effect=Exception("Database error"))

        response = client.put(
            f"/api/properties/{test_property_1.property_id}",
            json=payload,
            headers=headers
        )

        assert response.status_code == 500
        assert response.json["error"] == "An error occurred while updating the property."

class TestCreatePropertyTenancy:
    """Tests for POST /api/properties/<property_id>/tenancies endpoint."""

    def test_create_tenancy_success(self, client, session, landlord_token, test_property_1):
        """Test successful creation of a tenancy with all required fields."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01",
            "lease_end_date": "2024-12-31"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        
        # Verify response data
        assert response.json["property_id"] == test_property_1.property_id
        assert float(response.json["rent_due"]) == 1000.00
        assert response.json["lease_start_date"] == "2024-01-01"
        assert response.json["lease_end_date"] == "2024-12-31"
        assert "group_chat" in response.json
        assert "group_chat_id" in response.json["group_chat"]
        assert "group_name" in response.json["group_chat"]
        assert response.json["group_chat"]["group_name"] == f"Property Chat - {test_property_1.address}"

        # Verify database entries
        tenancy = session.query(Tenancy).first()
        assert tenancy is not None
        assert tenancy.property_id == test_property_1.property_id
        assert float(tenancy.rent_due) == 1000.00
        assert tenancy.lease_start_date == date(2024, 1, 1)
        assert tenancy.lease_end_date == date(2024, 12, 31)

        # Verify group chat creation
        group_chat = session.query(GroupChat).first()
        assert group_chat is not None
        assert group_chat.group_name == f"Property Chat - {test_property_1.address}"

    def test_create_tenancy_without_end_date(self, client, session, landlord_token, test_property_1):
        """Test successful creation of a tenancy without an end date."""
        # Clear any existing tenancies to ensure clean state
        session.query(Tenancy).delete()
        session.commit()
        
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        assert response.json["lease_end_date"] is None

        # Refresh session to ensure we get the latest data
        session.expire_all()
        tenancy = session.query(Tenancy).first()
        assert tenancy.lease_end_date is None

    def test_create_tenancy_unauthorized(self, client, auth_token, test_property_1):
        """Test tenancy creation by an unauthorized user (tenant)."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload,
            headers=headers
        )

        assert response.status_code == 403
        assert response.json["error"] == "Unauthorized"

    def test_create_tenancy_property_not_found(self, client, landlord_token):
        """Test tenancy creation for a non-existent property."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.post(
            "/api/properties/999/tenancies",  # Assuming ID 999 does not exist
            json=payload,
            headers=headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Property not found"

    def test_create_tenancy_missing_required_fields(self, client, landlord_token, test_property_1):
        """Test tenancy creation with missing required fields."""
        # Test missing rent_due
        payload1 = {
            "lease_start_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload1,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Missing required fields"

        # Test missing lease_start_date
        payload2 = {
            "rent_due": 1000.00
        }

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload2,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Missing required fields"

    def test_create_tenancy_invalid_date_format(self, client, landlord_token, test_property_1):
        """Test tenancy creation with invalid date formats."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "01-01-2024",  # Wrong format
            "lease_end_date": "12-31-2024"     # Wrong format
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload,
            headers=headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid date format. Use YYYY-MM-DD"

    def test_create_tenancy_database_error(self, client, session, landlord_token, test_property_1, mocker):
        """Test tenancy creation with database error."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01"
        }
        headers = {"Authorization": f"Bearer {landlord_token}"}

        # Mock database error
        mocker.patch.object(session, 'commit', side_effect=Exception("Database error"))

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload,
            headers=headers
        )

        assert response.status_code == 500
        assert response.json["error"] == "An error occurred while creating the tenancy."

    def test_create_tenancy_no_token(self, client, test_property_1):
        """Test tenancy creation without authentication token."""
        payload = {
            "rent_due": 1000.00,
            "lease_start_date": "2024-01-01"
        }

        response = client.post(
            f"/api/properties/{test_property_1.property_id}/tenancies",
            json=payload
        )

        assert response.status_code == 401
        assert response.json["msg"] == "Missing Authorization Header"