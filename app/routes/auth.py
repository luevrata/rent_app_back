from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import bcrypt, db

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login_user():
    """
    Handle user login and return a JWT access token upon successful authentication.
    """
    data = request.json

    # Validate request payload
    if not data or not all(key in data for key in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400
    
    # Normalize email to lowercase for case-insensitive comparison
    email = data["email"].lower()
    user = User.query.filter_by(email=email).first()

    if user:
        # Check password
        password = data["password"].encode('utf-8')
        if bcrypt.check_password_hash(user.password, password):
            # Generate JWT access token
            access_token = create_access_token(identity={"user_id": user.user_id, "role": user.role}, fresh=True)
            return jsonify({
                "token": access_token,
                "user": {
                    "id": user.user_id,
                    "email": user.email,
                    "role": user.role
                }
            }), 200
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({"error": "Email not found"}), 404



@auth.route('/register', methods=['POST'])
def register_user():
    """
    Handle user registration by validating input, hashing the password, 
    and saving the user to the database.
    """
    data = request.json
    if not data or not all(key in data for key in ('first_name', 'last_name', 'email', 'password', 'role')):
        return jsonify({"error": "Invalid data"}), 400
    
    email = data['email'].lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=email,
        password=hashed_password,
        role=data['role']
    )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201
