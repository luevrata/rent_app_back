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

# Get all properties for a landlord
@landlords_bp.route("/properties", methods=["GET"])
@jwt_required()
def get_landlord_properties():
    """
    Get all properties for the authenticated landlord, with optional pagination and filtering.

    Query Parameters:
        page (int): The page number (default: 1).
        per_page (int): The number of items per page (default: 10).
        status (str): Filter properties by status.

    Returns:
        JSON: A list of properties with pagination metadata or an error message.
    """
    user = get_current_user()
    if not user or user.role != "Landlord":
        return error_response("Unauthorized", 403)

    # Pagination and filters
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    status = request.args.get("status", type=str)

    query = Property.query.filter_by(landlord_id=user.user_id)
    if status:
        query = query.filter(Property.status == status)

    properties = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "total": properties.total,
        "page": properties.page,
        "per_page": properties.per_page,
        "properties": [property.to_dict() for property in properties.items]
    })

# Get a single property
@landlords_bp.route("/properties/<int:property_id>", methods=["GET"])
@jwt_required()
def get_property(property_id):
    """
    Get details of a specific property based on property ID for the authenticated landlord.

    Path Parameters:
        property_id (int): The ID of the property to retrieve.

    Returns:
        JSON: Details of the specific property or an error message.
    """
    try:
        user = get_current_user()
        if not user or user.role != "Landlord":
            return error_response("Unauthorized", 403)

        property = Property.query.filter_by(property_id=property_id, landlord_id=user.user_id).first()
        if not property:
            return error_response("Property not found", 404)

        return jsonify(property.to_dict()), 200
    except Exception as e:
        return error_response("An error occurred while retrieving the property.", 500)