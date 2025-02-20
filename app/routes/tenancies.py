from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.extensions import db
from app.models.tenancy import Tenancy
from app.models.property import Property
from app.services.utils import get_current_user, error_response

# Blueprint for tenancy-related endpoints
tenancies_bp = Blueprint("tenancies", __name__)

@tenancies_bp.route("/<int:tenancy_id>", methods=["PUT"])
@jwt_required()
def update_tenancy(tenancy_id):
    """
    Update tenancy details.

    Path Parameters:
        tenancy_id (int): The ID of the tenancy to update.

    Request Body:
        rent_due (float, optional): The new rent amount
        lease_start_date (str, optional): New start date of the lease (YYYY-MM-DD)
        lease_end_date (str, optional): New end date of the lease (YYYY-MM-DD)

    Returns:
        JSON: Updated tenancy details or an error message.
    """
    try:
        # Authenticate user
        user = get_current_user()
        if not user or user.role != "Landlord":
            return error_response("Unauthorized", 403)

        # Get tenancy
        tenancy = db.session.get(Tenancy, tenancy_id)
        if not tenancy:
            return error_response("Tenancy not found", 404)

        # Check if user owns the property associated with the tenancy
        property = db.session.get(Property, tenancy.property_id)
        if not property or property.landlord_id != user.user_id:
            return error_response("Unauthorized access to tenancy", 403)

        # Get request data
        data = request.json
        if not data:
            return error_response("No update data provided", 400)

        # Update rent_due if provided
        if "rent_due" in data:
            try:
                tenancy.rent_due = float(data["rent_due"])
            except (ValueError, TypeError):
                return error_response("Invalid rent_due value", 400)

        # Update lease dates if provided
        date_fields = {
            "lease_start_date": None,
            "lease_end_date": None
        }

        for field in date_fields:
            if field in data:
                try:
                    if data[field] is None:
                        setattr(tenancy, field, None)
                    else:
                        date_value = datetime.strptime(data[field], "%Y-%m-%d").date()
                        setattr(tenancy, field, date_value)
                except ValueError:
                    return error_response(f"Invalid {field} format. Use YYYY-MM-DD", 400)

        # Validate lease dates if both are present
        if tenancy.lease_start_date and tenancy.lease_end_date:
            if tenancy.lease_end_date < tenancy.lease_start_date:
                return error_response("Lease end date cannot be before start date", 400)

        # Save changes
        db.session.commit()

        # Prepare response
        response_data = {
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

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error updating tenancy: {str(e)}")
        return error_response("An error occurred while updating the tenancy.", 500)