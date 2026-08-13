from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from extensions import db, bcrypt
from models import User
from config import Config

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or "@" not in email:
        return jsonify({"error": "Enter a valid email address."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created successfully.", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))  # maps to the "Remember me" checkbox

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password."}), 401

    expires = Config.JWT_REMEMBER_ME_EXPIRES if remember else Config.JWT_ACCESS_TOKEN_EXPIRES
    access_token = create_access_token(identity=str(user.id), expires_delta=expires)

    return jsonify({
        "message": "Logged in successfully.",
        "access_token": access_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({"user": user.to_dict()}), 200


# --- Google login placeholder ---
# For "Continue with Google" on the frontend, use Google Identity Services
# on the React side to get an ID token, then verify it here with
# google-auth's id_token.verify_oauth2_token(), create/find the user by
# email, and issue a JWT the same way as /login does above.
@auth_bp.route("/google", methods=["POST"])
def google_login():
    return jsonify({"error": "Google login not implemented yet."}), 501
