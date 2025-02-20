from datetime import date
from app.models.groupChat import GroupChat
from app.models.tenancy import Tenancy
import pytest
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.landlord import Landlord
from app.models.property import Property
from app.models.tenancyTenants import TenancyTenants
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""
    app = create_app()
    if os.getenv("FLASK_ENV") != "testing":
        raise RuntimeError("Tests should only be run in the testing environment")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Set up a test client for sending requests."""
    return app.test_client()

@pytest.fixture(scope="function")
def session(app):
    """
    Provide a session for tests with transactional isolation.
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        db.session.bind = connection

        # Clear all relevant tables before each test
        db.session.query(Property).delete()
        db.session.query(Landlord).delete()
        db.session.query(User).delete()
        db.session.query(TenancyTenants).delete()
        db.session.query(Tenancy).delete()

        yield db.session

        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def test_tenant_1(session):
    """Create a test user with Tenant role."""
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password=hashed_password,
        role="Tenant"
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture(scope="function")
def test_landlord_1(session):
    """Create a test landlord user 1 with associated Landlord record."""
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    user = User(
        first_name="Test1",
        last_name="Landlord",
        email="landlord1@example.com",
        password=hashed_password,
        role="Landlord"
    )
    session.add(user)
    session.flush()  # Get the user_id

    landlord = Landlord(landlord_id=user.user_id)
    session.add(landlord)
    session.commit()
    return user

@pytest.fixture
def test_landlord_2(session):
    """Create a test landlord user 2 with associated Landlord record."""
    hashed_password = bcrypt.generate_password_hash("password123").decode("utf-8")
    user = User(
        first_name="Test2",
        last_name="Landlord",
        email="landlord2@example.com",
        password=hashed_password,
        role="Landlord"
    )
    session.add(user)
    session.commit()

    landlord = Landlord(landlord_id=user.user_id)
    session.add(landlord)
    session.commit()
    return user
@pytest.fixture(scope="function")
def tenant_1_token(app, test_tenant_1):
    """Create a JWT token for the test tenant user."""
    with app.app_context():
        token = create_access_token(identity=str(test_tenant_1.user_id))
        return token

@pytest.fixture(scope="function")
def landlord_1_token(app, test_landlord_1):
    """Create a JWT token for the test landlord user."""
    with app.app_context():
        token = create_access_token(identity=str(test_landlord_1.user_id))
        return token
    
@pytest.fixture(scope="function")
def landlord_2_token(app, test_landlord_2):
    """Create a JWT token for the test landlord user."""
    with app.app_context():
        token = create_access_token(identity=str(test_landlord_2.user_id))
        return token


@pytest.fixture(scope="function")
def test_property_1(session, test_landlord_1):
    """
    Create a sample property associated with the test landlord.
    """
    property = Property(
        address="123 Test Street",
        landlord_id=test_landlord_1.user_id
    )
    session.add(property)
    session.commit()
    return property

@pytest.fixture(scope="function")
def test_groupChat_1(session):
    """Create a test group chat."""
    group_chat = GroupChat(group_name="Test Chat 1")
    session.add(group_chat)
    session.flush()  # Get the ID without committing
    return group_chat

@pytest.fixture(scope="function")
def test_groupChat_2(session):
    """Create a test group chat."""
    group_chat = GroupChat(group_name="Test Chat 2")
    session.add(group_chat)
    session.flush()  # Get the ID without committing
    return group_chat

@pytest.fixture(scope="function")
def test_tenancy_1(session, test_property_rented, test_groupChat_1):
    """Create a test tenancy."""
    tenancy = Tenancy(
        property_id=test_property_rented.property_id,
        rent_due=1000.00,
        lease_start_date=date(2024, 1, 1),
        lease_end_date=date(2024, 12, 31),
        group_chat_id=test_groupChat_1.group_chat_id
    )
    session.add(tenancy)
    session.commit()
    return tenancy

@pytest.fixture(scope="function")
def test_tenancy_2(session, test_property_rented, test_groupChat_2):
    """Create a test tenancy."""
    tenancy = Tenancy(
            property_id=test_property_rented.property_id,
            rent_due=1200.00,
            lease_start_date=date(2024, 2, 1),
            group_chat_id=test_groupChat_2.group_chat_id
        )
    session.add(tenancy)
    session.commit()
    return tenancy

@pytest.fixture(scope="function")
def test_tenancyTenants_1(session, test_tenancy_1, test_tenant_1):
    """Create a test tenancy-tenant association."""
    tenancy_tenant = TenancyTenants(
        tenancy_id=test_tenancy_1.tenancy_id,
        tenant_id=test_tenant_1.user_id
    )
    session.add(tenancy_tenant)
    session.commit()
    return tenancy_tenant

@pytest.fixture(scope="function")
def test_property_rented(session, test_landlord_1):
    """Create a test property with rented status."""
    property = Property(address="123 Test Street", landlord_id=test_landlord_1.user_id, status="rented")
    session.add(property)
    session.commit()
    return property

@pytest.fixture(scope="function")
def test_property_vacant(session, test_landlord_1):
    """Create a test property with vacant status."""
    property = Property(address="456 Elm Street", landlord_id=test_landlord_1.user_id, status="vacant")
    session.add(property)
    session.commit()
    return property