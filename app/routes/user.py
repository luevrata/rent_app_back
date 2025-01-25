from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

user = Blueprint("user", __name__)

@user.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    current_user = get_jwt_identity()  # Extract user identity from token
    return jsonify({"user": current_user}), 200