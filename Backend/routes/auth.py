from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from mysql.connector import Error

from config import Config
from database import DatabaseConnectionError, get_db_connection
from extensions import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def user_response(user):
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


def database_unavailable_response():
    return jsonify({
        "error": "MySQL is unavailable. Start MySQL and check Backend/.env credentials."
    }), 503


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name:
        return jsonify({"error": "Enter your full name."}), 400
    if not email or "@" not in email:
        return jsonify({"error": "Enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "An account with this email already exists."}), 409

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash),
        )
        connection.commit()
        return jsonify({
            "message": "Account created successfully.",
            "user": {"id": cursor.lastrowid, "name": name, "email": email},
        }), 201
    except DatabaseConnectionError:
        return database_unavailable_response()
    except Error:
        if connection:
            connection.rollback()
        return jsonify({"error": "Unable to create the account. Please try again."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()
        if not user or not bcrypt.check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password."}), 401

        expires = Config.JWT_REMEMBER_ME_EXPIRES if remember else Config.JWT_ACCESS_TOKEN_EXPIRES
        return jsonify({
            "message": "Logged in successfully.",
            "access_token": create_access_token(identity=str(user["id"]), expires_delta=expires),
            "user": user_response(user),
        }), 200
    except DatabaseConnectionError:
        return database_unavailable_response()
    except Error:
        return jsonify({"error": "Unable to log in. Please try again."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email FROM users WHERE id = %s", (get_jwt_identity(),)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found."}), 404
        return jsonify({"user": user_response(user)}), 200
    except DatabaseConnectionError:
        return database_unavailable_response()
    except Error:
        return jsonify({"error": "Unable to load the user."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
