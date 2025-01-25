from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

#TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
# mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
bcrypt = Bcrypt() 
jwt = JWTManager()


