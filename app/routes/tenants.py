#TODO: UNCOMMENT WHEN START api DEVELOPMENT
# from flask import Blueprint, request, jsonify
# from app.models.tenant import Tenant
# from app.extensions import db, mail
# from flask_mail import Message

# # Create Blueprint for tenants
# tenants = Blueprint("tenants", __name__)

# # Get all tenants
# @tenants.route("/", methods=["GET"])
# def get_tenants():
#     tenants = Tenant.query.all()
#     return jsonify([tenant.to_dict() for tenant in tenants])

# # Add a new tenant
# @tenants.route("/", methods=["POST"])
# def add_tenant():
#     data = request.json
#     if not data or "name" not in data or "email" not in data or "rent_due" not in data:
#         return jsonify({"error": "Invalid tenant data"}), 400

#     new_tenant = Tenant(name=data["name"], email=data["email"], rent_due=data["rent_due"])
#     db.session.add(new_tenant)
#     db.session.commit()
#     return jsonify(new_tenant.to_dict()), 201

# # Function to send an invitation email
# @tenants.route("/<int:tenant_id>/send_invitation_email", methods=["POST"])
# def send_invitation_email(tenant_id):
#     tenant = Tenant.query.get(tenant_id)
#     if not tenant:
#         return jsonify({"error": "Tenant not found"}), 404
    
#     try:
#         msg = Message(
#             subject="You're Invited to Join [App Name]",
#             sender="elizaveta.firsovaaa@gmail.com",  # Replace with your email
#             recipients=[tenant.email]
#         )
#         msg.body = f"""
#         Hi {tenant.name},

#         You have been added as a tenant by your landlord to manage your rent and communication through [App Name].

#         Please click the link below to register and set up your account:
#         rentapp://api/auth/tenant_registration_page?email={tenant.email}

#         If you did not expect this email, please contact your landlord.

#         Best regards,
#         The [App Name] Team
#         """
#         mail.send(msg)

#         tenant.status = "invited"
#         db.session.commit()

#         return jsonify({"message": "Email sent and status updated"}), 200
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return jsonify({"error": "Failed to send email"}), 500



