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
