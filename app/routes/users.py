from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint("users", __name__)

@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    current_user = get_jwt_identity()  # Extract user identity from token
    return jsonify({"user": current_user}), 200