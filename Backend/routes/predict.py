from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from ml.predict_utils import predict_price

predict_bp = Blueprint("predict", __name__, url_prefix="/api")


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()  # only logged-in users can get predictions
def predict():
    data = request.get_json(silent=True) or {}

    required_fields = ["area", "bedrooms", "bathrooms", "location"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        price = predict_price(data)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 500

    return jsonify({"predicted_price": price}), 200
