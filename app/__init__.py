from flask import Flask, Blueprint
from app.extensions import cors, db, migrate

main = Blueprint('main', __name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Initialize extensions
    cors.init_app(app)  # Enable CORS
    db.init_app(app)
    migrate.init_app(app, db)
    #TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
    # mail.init_app(app)

    # Register blueprints
    # TODO: UNCOMMENT WHEN START api DEVELOPMENT
    # app.register_blueprint(tenants, url_prefix="/api/tenants")
    # app.register_blueprint(auth, url_prefix="/api/auth")

    return app