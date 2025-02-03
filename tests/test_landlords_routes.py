import pytest
from app.models.property import Property

def test_create_property_success(client, session, landlord_token):
    """Test successful property creation by a landlord."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    response = client.post(
        "/api/landlords/properties",  # Updated URL without landlord_id
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 201
    assert response.json["address"] == "123 Test Street"
    
    # Verify database entries
    property = session.query(Property).first()
    assert property is not None
    assert property.address == "123 Test Street"

def test_create_property_unauthorized_role(client, create_test_user, auth_token):
    """Test property creation by an unauthorized user (tenant)."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.post(
        "/api/landlords/properties",  # Updated URL without landlord_id
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 403
    assert response.json["error"] == "Unauthorized"

def test_create_property_missing_address(client, landlord_token):
    """Test property creation with missing address."""
    payload = {}  # Missing address
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    response = client.post(
        "/api/landlords/properties",  # Updated URL without landlord_id
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 400
    assert response.json["error"] == "Missing property details"

def test_create_property_no_token(client):
    """Test property creation without authentication token."""
    payload = {
        "address": "123 Test Street"
    }
    
    response = client.post(
        "/api/landlords/properties",  # Updated URL without landlord_id
        json=payload
    )
    
    assert response.status_code == 401

def test_create_property_database_error(client, session, landlord_token, mocker):
    """Test property creation with database error."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Mock the database session to raise an exception
    mocker.patch.object(session, 'commit', side_effect=Exception("Database error"))
    
    response = client.post(
        "/api/landlords/properties",  # Updated URL without landlord_id
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 500
    assert response.json["error"] == "An error occurred while creating the property."

def test_get_landlord_properties_success(client, session, landlord_token, create_test_landlord_1):
    """Test successful retrieval of all properties for a landlord."""
    # Create properties for the landlord
    properties = [
        Property(address="123 Main Street", landlord_id=create_test_landlord_1.user_id),
        Property(address="456 Elm Street", landlord_id=create_test_landlord_1.user_id)
    ]
    session.add_all(properties)
    session.commit()

    headers = {"Authorization": f"Bearer {landlord_token}"}
    response = client.get("/api/landlords/properties", headers=headers)

    assert response.status_code == 200
    assert response.json["total"] == 2
    assert len(response.json["properties"]) == 2
    assert response.json["properties"][0]["address"] == "123 Main Street"
    assert response.json["properties"][1]["address"] == "456 Elm Street"

def test_get_landlord_properties_pagination(client, session, landlord_token, create_test_landlord_1):
    """Test pagination when retrieving properties."""
    # Create multiple properties for pagination
    for i in range(15):
        property = Property(address=f"Property {i}", landlord_id=create_test_landlord_1.user_id)
        session.add(property)
    session.commit()

    headers = {"Authorization": f"Bearer {landlord_token}"}
    response = client.get("/api/landlords/properties?page=1&per_page=10", headers=headers)

    assert response.status_code == 200
    assert response.json["total"] == 15
    assert response.json["page"] == 1
    assert response.json["per_page"] == 10
    assert len(response.json["properties"]) == 10

    # Test second page
    response = client.get("/api/landlords/properties?page=2&per_page=10", headers=headers)
    assert response.status_code == 200
    assert response.json["page"] == 2
    assert len(response.json["properties"]) == 5

def test_get_landlord_properties_filter_by_status(client, session, landlord_token, create_test_landlord_1):
    """Test filtering properties by status."""
    # Create properties with different statuses
    properties = [
        Property(address="123 Main Street", landlord_id=create_test_landlord_1.user_id, status="rented"),
        Property(address="456 Elm Street", landlord_id=create_test_landlord_1.user_id, status="vacant")
    ]
    session.add_all(properties)
    session.commit()

    headers = {"Authorization": f"Bearer {landlord_token}"}

    # Filter by "rented" status
    response = client.get("/api/landlords/properties?status=rented", headers=headers)
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["properties"][0]["address"] == "123 Main Street"
    assert response.json["properties"][0]["status"] == "rented"

    # Filter by "vacant" status
    response = client.get("/api/landlords/properties?status=vacant", headers=headers)
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["properties"][0]["address"] == "456 Elm Street"
    assert response.json["properties"][0]["status"] == "vacant"

def test_get_landlord_properties_unauthorized(client, auth_token):
    """Test that unauthorized users cannot access landlord properties."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/landlords/properties", headers=headers)

    assert response.status_code == 403
    assert response.json["error"] == "Unauthorized"

def test_get_landlord_properties_no_token(client):
    """Test accessing properties without authentication."""
    response = client.get("/api/landlords/properties")

    assert response.status_code == 401

