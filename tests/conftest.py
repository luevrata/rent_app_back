import pytest
from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
import os
from dotenv import load_dotenv

load_dotenv() 

@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory SQLite DB for testing
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    with app.app_context():
        db.create_all()  # Create tables before tests
        yield app
        db.session.remove()
        db.drop_all()  # Drop tables after tests

@pytest.fixture(scope="function")
def client(app):
    """Set up a test client for sending requests."""
    return app.test_client()

@pytest.fixture(scope="function")
def session(app):
    """
    Provide a session for tests with transactional isolation.
    This ensures changes are rolled back after each test.
    """
    with app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to the connection
        db.session.bind = connection

        # Clear the database before each test
        db.session.query(User).delete()

        yield db.session  # Provide the session to the test

        # Roll back the transaction and close the connection
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def create_test_user(session):
    """Create a test user."""
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
