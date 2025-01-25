import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disables unnecessary overhead
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

#TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
    # # Email server configuration
    # MAIL_SERVER = os.getenv("MAIL_SERVER") # Use your email provider's SMTP server
    # MAIL_PORT = os.getenv("MAIL_PORT")
    # MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    # MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    # MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # Your email address
    # MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")    # Your email password or app-specific password

