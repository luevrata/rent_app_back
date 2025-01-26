from app.models.user import User


def test_register_user_success(client, session):
    """Test successful user registration."""
    payload = {
        "first_name": "New",
        "last_name": "User",
        "email": "new_user@example.com",
        "password": "password123",
        "role": "Tenant"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"

    # Verify the user was added to the database
    user = session.query(User).filter_by(email="new_user@example.com").first()
    assert user is not None
    assert user.first_name == "New"
    assert user.role == "Tenant"

def test_register_user_existing_email(client, create_test_user):
    """Test registration with an existing email."""
    payload = {
        "first_name": "Another",
        "last_name": "User",
        "email": "test@example.com",  # Same as `create_test_user`
        "password": "password123",
        "role": "Tenant"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Email already registered"


def test_register_user_missing_fields(client):
    """Test registration with missing fields."""
    payload = {
        "first_name": "Missing",
        "last_name": "Fields"
        # Missing email, password, and role
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid data"


def test_login_user_success(client, create_test_user):
    """Test successful user login."""
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    assert "token" in response.json
    assert response.json["user"]["email"] == "test@example.com"
    assert response.json["user"]["role"] == "Tenant"


def test_login_user_invalid_password(client, create_test_user):
    """Test login with an invalid password."""
    payload = {
        "email": "test@example.com",
        "password": "wrong_password"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid password"


def test_login_user_email_not_found(client, session):
    """Test login with an email not in the database."""
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 404
    assert response.json["error"] == "Email not found"


def test_login_user_missing_fields(client):
    """Test login with missing fields."""
    payload = {
        "email": "missing@example.com"
        # Missing password
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Missing email or password"
