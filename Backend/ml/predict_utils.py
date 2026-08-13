import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
_model = None  # cached in memory after first load


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "model.pkl not found. Run ml/train_model.py first to train and save a model."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_price(data: dict) -> float:
    model = load_model()

    features = pd.DataFrame([{
        "area": data["area"],
        "bedrooms": data["bedrooms"],
        "bathrooms": data["bathrooms"],
        "location": data["location"],
    }])

    prediction = model.predict(features)[0]
    return round(float(prediction), 2)
