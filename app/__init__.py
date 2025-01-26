from app.routes.landlords import landlords_bp
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from flask import Flask
from app.extensions import cors, db, migrate, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

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
    app.register_blueprint(landlords_bp, url_prefix='/api/landlords')

    return app