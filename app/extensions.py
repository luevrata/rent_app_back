from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

#TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
# mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
