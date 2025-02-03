from app.models.user import User
from app.models.property import Property
from app.models.landlord import Landlord
from app.extensions import db
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint for landlord-related endpoints
landlords_bp = Blueprint("landlords", __name__)

def get_current_user():
    """Get the current user from the JWT token."""
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)
    return user

def error_response(message, status_code):
    """Generate a consistent error response."""
    return jsonify({"error": message}), status_code

# Create property
@landlords_bp.route("/properties", methods=["POST"])
@jwt_required()
def create_landlord_property():
    """
    Create a new property for the authenticated landlord.

    Returns:
        JSON: Details of the newly created property or an error message.
    """
    data = request.json

    # Validate input payload
    if not data or "address" not in data:
        return error_response("Missing property details", 400)

    # Get the current user
    user = get_current_user()
    if not user or user.role != "Landlord":
        return error_response("Unauthorized", 403)

    try:
        # Create the new property
        new_property = Property(
            address=data["address"],
            landlord_id=user.user_id  # Use the landlord_id from the authenticated user
        )
        db.session.add(new_property)

        # Commit the transaction
        db.session.commit()

        # Prepare the response
        #TODO: add location once get property api 
        # location = url_for("landlords.get_property", property_id=new_property.property_id, _external=True)
        response = jsonify(new_property.to_dict())
        response.status_code = 201
        # response.headers["Location"] = location
        return response

    except Exception as e:
        db.session.rollback()
        return error_response("An error occurred while creating the property.", 500)
