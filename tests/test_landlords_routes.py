from app.models.property import Property

def test_create_property_success(client, session, create_test_landlord_1, landlord_token):
    """Test successful property creation by a landlord."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    response = client.post(
        f"/api/landlords/{create_test_landlord_1.user_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 201
    assert response.json["address"] == "123 Test Street"
    
    # Verify database entries
    property = session.query(Property).first()
    assert property is not None
    assert property.address == "123 Test Street"
    assert property.landlord_id == create_test_landlord_1.user_id

def test_create_property_unauthorized_role(client, create_test_user, auth_token):
    """Test property creation by an unauthorized user (tenant)."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    response = client.post(
        f"/api/landlords/{create_test_user.user_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 403
    assert response.json["error"] == "Unauthorized"

def test_create_property_wrong_landlord(client, create_test_landlord_2, landlord_token):
    """Test property creation for a different landlord ID."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    wrong_landlord_id = create_test_landlord_2.user_id
    response = client.post(
        f"/api/landlords/{wrong_landlord_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 403
    assert response.json["error"] == "Unauthorized"

def test_create_property_missing_address(client, create_test_landlord_1, landlord_token):
    """Test property creation with missing address."""
    payload = {}  # Missing address
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    response = client.post(
        f"/api/landlords/{create_test_landlord_1.user_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 400
    assert response.json["error"] == "Missing property details"

def test_create_property_no_token(client, create_test_landlord_1):
    """Test property creation without authentication token."""
    payload = {
        "address": "123 Test Street"
    }
    
    response = client.post(
        f"/api/landlords/{create_test_landlord_1.user_id}/properties",
        json=payload
    )
    
    assert response.status_code == 401

def test_create_property_nonexistent_landlord(client, landlord_token):
    """Test property creation for non-existent landlord."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    non_existent_id = 99999
    response = client.post(
        f"/api/landlords/{non_existent_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 404
    assert response.json["error"] == "Landlord not found"

def test_create_property_database_error(client, session, create_test_landlord_1, landlord_token, mocker):
    """Test property creation with database error."""
    payload = {
        "address": "123 Test Street"
    }
    headers = {"Authorization": f"Bearer {landlord_token}"}
    
    # Mock the database session to raise an exception
    mocker.patch.object(session, 'commit', side_effect=Exception("Database error"))
    
    response = client.post(
        f"/api/landlords/{create_test_landlord_1.user_id}/properties",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 500
    assert response.json["error"] == "An error occurred while creating the property."