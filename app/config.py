import os

class Config:
    # Replace `username`, `password`, `localhost`, and `rent_app` with your database details
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disables unnecessary overhead
    SECRET_KEY = os.getenv("SECRET_KEY")

#TODO: UNCOMMENT WHEN START MAIL DEVELOPMENT
    # # Email server configuration
    # MAIL_SERVER = os.getenv("MAIL_SERVER") # Use your email provider's SMTP server
    # MAIL_PORT = os.getenv("MAIL_PORT")
    # MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    # MAIL_USE_SSL = os.getenv("MAIL_USE_SSL")
    # MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # Your email address
    # MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")    # Your email password or app-specific password

