from app.routes.user import user
from flask import Flask
from app.extensions import cors, db, migrate, jwt
from app.routes.auth import auth

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
    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(user, url_prefix="/api/user")

    return app