from app.models.user import User
from flask import Blueprint, request, jsonify, url_for
from app.models.property import Property
from app.models.landlord import Landlord
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint for landlord-related endpoints
landlords_bp = Blueprint("landlords", __name__)

@landlords_bp.route("/<int:landlord_id>/properties", methods=["POST"])
@jwt_required()
def create_landlord_property(landlord_id):
    """
    Create a new property for a specific landlord.

    Args:
        landlord_id (int): The ID of the landlord.

    Returns:
        JSON: Details of the newly created property or an error message.
    """
    data = request.json

    # Validate input payload
    if not data or "address" not in data:
        return jsonify({"error": "Missing property details"}), 400

    # Get the current user's identity and convert it to int
    current_user_id = int(get_jwt_identity())

    # Get the user to check their role
    user = User.query.get(current_user_id)
    if not user or user.role != "Landlord" or current_user_id != landlord_id:
        return jsonify({"error": "Unauthorized"}), 403

    # Check if the landlord exists in the database
    landlord = Landlord.query.get(landlord_id)
    if not landlord:
        return jsonify({"error": "Landlord not found"}), 404

    # Create the new property
    new_property = Property(
        address=data["address"],
        landlord_id=landlord_id
    )
    db.session.add(new_property)
    db.session.commit()

    # Add 'Location' header pointing to the new resource
    # location = url_for("landlords.get_property", property_id=new_property.property_id, _external=True)
    response = jsonify(new_property.to_dict())
    response.status_code = 201
    # response.headers["Location"] = location
    return response
