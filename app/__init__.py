from flask import Flask
from app.routes.landlords import landlords_bp
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.extensions import cors, db, migrate, jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Determine the environment and load the appropriate configuration
    env = os.getenv("FLASK_ENV", "development")  # Default to 'development' if not set
    configure_app(app, env)

    # Initialize extensions
    cors.init_app(app)  # Enable CORS
    db.init_app(app)
    migrate.init_app(app, db)

#TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
    # mail.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(landlords_bp, url_prefix="/api/landlords")

    return app


def configure_app(app, env):
    """Configure the Flask app based on the environment."""
    # Common configurations
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')

    # Environment-specific configurations
    if env == "testing":
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory database for tests
    elif env == "development":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DATABASE_URL")
    elif env == "production":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
        # app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    else:
        raise ValueError(f"Invalid FLASK_ENV: {env}")
