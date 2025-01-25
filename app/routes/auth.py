#TODO: UNCOMMENT WHEN START api DEVELOPMENT
# from flask import Blueprint, request, jsonify, redirect
# from app.models.tenant import Tenant
# from app.extensions import db

# auth = Blueprint("auth", __name__)

# # @auth.route('/api/auth/tenant_registration_page', methods=["GET"])
# # def tenant_registration_page():
# #     email = request.args.get('email')
# #     if email:
# #         # Check if the app is installed (use additional checks if needed)
# #         return redirect(f"rentapp://tenant_registration_page?email={email}")

# #     return jsonify({"error": "Email not provided"}), 400

# @auth.route('/register_tenant', methods=["POST"])
# def register_tenant():
#     data = request.json
#     if not data or "name" not in data or "email" not in data or "password" not in data:
#         return jsonify({"error": "Invalid registration data"}), 400

#     # Process the registration
#     tenant = Tenant.query.filter_by(contact=data["email"]).first()
#     if tenant:
#         tenant.name = data["name"]
#         tenant.password = data["password"]  # Make sure to hash the password in a real app
#         tenant.status = "registered"
#         db.session.commit()
#         return jsonify({"message": "Registration successful"}), 200
#     else:
#         return jsonify({"error": "Tenant not found"}), 404
