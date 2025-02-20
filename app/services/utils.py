from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models.user import User

def get_current_user():
    """Get the current user from the JWT token."""
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    return user

def error_response(message, status_code):
    """Generate a consistent error response."""
    return jsonify({"error": message}), status_code