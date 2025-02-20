from datetime import datetime
from app.models.groupChat import GroupChat
from app.models.tenancy import Tenancy
from app.models.user import User
from app.models.property import Property
from app.extensions import db
from app.services.utils import error_response, get_current_user
from flask import Blueprint, request, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity

# Blueprint for property-related endpoints
properties_bp = Blueprint("properties", __name__)

# Create property
@properties_bp.route("", methods=["POST"])
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
@properties_bp.route("", methods=["GET"])
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
@properties_bp.route("/<int:property_id>", methods=["GET"])
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
    
# Update property
@properties_bp.route("/<int:property_id>", methods=["PUT"])
@jwt_required()
def update_property_address(property_id):
    """
    Update the address of a specific property for the authenticated landlord.

    Path Parameters:
        property_id (int): The ID of the property to update.

    Returns:
        JSON: Updated property details or an error message.
    """
    try:
        # Authenticate user
        user = get_current_user()
        if not user or user.role != "Landlord":
            return error_response("Unauthorized", 403)

        # Check if property exists and belongs to the landlord
        property = Property.query.filter_by(property_id=property_id, landlord_id=user.user_id).first()
        if not property:
            return error_response("Property not found", 404)

        # Validate request payload
        data = request.json
        if not data or "address" not in data:
            return error_response("Missing or invalid 'address' in the request body.", 400)

        # Update the address
        property.address = data["address"]
        db.session.commit()

        return jsonify(property.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return error_response("An error occurred while updating the property.", 500)

# Create tenancy for a property
@properties_bp.route("/<int:property_id>/tenancies", methods=["POST"])
@jwt_required()
def create_property_tenancy(property_id):
    """
    Create a new tenancy for a specific property.

    Path Parameters:
        property_id (int): The ID of the property to create a tenancy for.

    Request Body:
        rent_due (float): The rent amount due
        lease_start_date (str): Start date of the lease (YYYY-MM-DD)
        lease_end_date (str): End date of the lease (YYYY-MM-DD) (optional)

    Returns:
        JSON: Details of the newly created tenancy or an error message.
    """
    try:
        # Authenticate user
        user = get_current_user()
        if not user or user.role != "Landlord":
            return error_response("Unauthorized", 403)

        # Check if property exists and belongs to the landlord
        property = Property.query.filter_by(property_id=property_id, landlord_id=user.user_id).first()
        if not property:
            return error_response("Property not found", 404)

        # Validate request payload
        data = request.json
        required_fields = ["rent_due", "lease_start_date"]
        if not data or not all(field in data for field in required_fields):
            return error_response("Missing required fields", 400)

        try:
            lease_start_date = datetime.strptime(data["lease_start_date"], "%Y-%m-%d").date()
            lease_end_date = None  # Initialize as None by default
            
            # Only try to parse lease_end_date if it's provided and not empty
            if data.get("lease_end_date"):
                lease_end_date = datetime.strptime(data["lease_end_date"], "%Y-%m-%d").date()
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD", 400)

        # Create group chat first
        group_chat = GroupChat(
            group_name=f"Property Chat - {property.address}"
        )
        db.session.add(group_chat)
        db.session.flush()  # Get the group_chat_id without committing

        # Create new tenancy with explicit None for lease_end_date if not provided
        new_tenancy = Tenancy(
            property_id=property_id,
            rent_due=float(data["rent_due"]),
            lease_start_date=lease_start_date,
            lease_end_date=lease_end_date,  # This will be None if not provided
            group_chat_id=group_chat.group_chat_id
        )

        db.session.add(new_tenancy)
        db.session.commit()

        response_data = {
            "tenancy_id": new_tenancy.tenancy_id,
            "property_id": new_tenancy.property_id,
            "rent_due": float(new_tenancy.rent_due),
            "lease_start_date": new_tenancy.lease_start_date.isoformat(),
            "lease_end_date": new_tenancy.lease_end_date.isoformat() if new_tenancy.lease_end_date else None,
            "group_chat": {
                "group_chat_id": group_chat.group_chat_id,
                "group_name": group_chat.group_name
            }
        }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        return error_response("An error occurred while creating the tenancy.", 500)
    

@properties_bp.route("/<int:property_id>/tenancies", methods=["GET"])
@jwt_required()
def get_property_tenancies(property_id):
    """
    Retrieve all tenancies associated with a specific property.

    Path Parameters:
        property_id (int): The ID of the property to get tenancies for.

    Returns:
        JSON: List of tenancies associated with the property or an error message.
    """
    try:
        # Authenticate user
        user = get_current_user()
        if not user:
            return error_response("Unauthorized", 403)

        # Check if property exists
        property = db.session.get(Property, property_id)
        if not property:
            return error_response("Property not found", 404)

        # Verify user has access to the property
        if property.landlord_id != user.user_id:
            return error_response("Unauthorized access to property", 403)

        # Get all tenancies for the property
        tenancies = Tenancy.query.filter_by(property_id=property_id).all()

        # Format response
        tenancies_data = []
        for tenancy in tenancies:
            tenancy_data = {
                "tenancy_id": tenancy.tenancy_id,
                "property_id": tenancy.property_id,
                "rent_due": float(tenancy.rent_due),
                "lease_start_date": tenancy.lease_start_date.isoformat(),
                "lease_end_date": tenancy.lease_end_date.isoformat() if tenancy.lease_end_date else None,
                "group_chat": {
                    "group_chat_id": tenancy.group_chat.group_chat_id,
                    "name": tenancy.group_chat.group_name
                }
            }
            tenancies_data.append(tenancy_data)

        return jsonify(tenancies_data), 200

    except Exception as e:
        print(f"Error retrieving tenancies: {str(e)}")
        return error_response("An error occurred while retrieving tenancies.", 500)