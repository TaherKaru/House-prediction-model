import math
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd

from .config import DATASET_PATH, KMEANS_PATH, MODEL_PATH

HUBS = {"airport": (19.0896, 72.8656), "bkc": (19.0653, 72.8697), "csmt": (18.9402, 72.8356), "andheri_station": (19.1197, 72.8468), "thane_station": (19.1860, 72.9756)}


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return radius * 2 * math.asin(math.sqrt(a))


@dataclass
class Prediction:
    estimated_price: float
    confidence: str
    latitude: float
    longitude: float
    locality_resolved: str


class ModelService:
    def __init__(self):
        if not MODEL_PATH.exists() or not KMEANS_PATH.exists() or not DATASET_PATH.exists():
            raise FileNotFoundError("Model artefacts or cleaned dataset are missing. Restore them with `dvc pull`.")
        self.model = joblib.load(MODEL_PATH)
        self.kmeans = joblib.load(KMEANS_PATH)
        data = pd.read_csv(DATASET_PATH, usecols=["price", "locality", "new_latitude", "new_longitude", "new_pincode"])
        data = data.dropna(subset=["price", "locality", "new_latitude", "new_longitude"])
        data = data[data.price > 0].copy()
        data["log_price"] = np.log1p(data.price)
        data["pincode_key"] = data.new_pincode.fillna(0).astype(int).astype(str)
        self.pincode_mean = data.groupby("pincode_key").log_price.mean().to_dict()
        self.global_log_price = float(data.log_price.mean())
        self.locality_lookup = {str(name).casefold(): str(name) for name in data.locality.unique()}
        self.locality_coordinates = data.groupby("locality")[["new_latitude", "new_longitude"]].median().to_dict("index")

    def _resolve_location(self, location: str, latitude: float | None, longitude: float | None):
        canonical = self.locality_lookup.get(location.casefold(), location)
        if latitude is not None and longitude is not None:
            return canonical, latitude, longitude
        saved = self.locality_coordinates.get(canonical)
        if saved:
            return canonical, float(saved["new_latitude"]), float(saved["new_longitude"])
        return canonical, 19.0760, 72.8777  # Mumbai centroid for unknown localities

    def predict(self, request) -> Prediction:
        locality, latitude, longitude = self._resolve_location(request.location, request.latitude, request.longitude)
        coordinates = pd.DataFrame([[latitude, longitude]], columns=["new_latitude", "new_longitude"])
        feature_row = {"area": request.area, "locality": locality, "property_type": request.property_type, "bedroom_num": request.bhk, "bathroom_num": request.bathrooms, "furnished": request.furnished, "total_floors": request.total_floors, "new_latitude": latitude, "new_longitude": longitude, "pincode_target_encoded": self.pincode_mean.get(request.pincode, self.global_log_price), "micro_market_cluster": int(self.kmeans.predict(coordinates)[0])}
        for hub, (hub_lat, hub_lon) in HUBS.items():
            feature_row[f"distance_to_{hub}_km"] = haversine_km(latitude, longitude, hub_lat, hub_lon)
        frame = pd.DataFrame([feature_row])
        for category in ["locality", "property_type", "furnished", "micro_market_cluster"]:
            frame[category] = frame[category].astype("category")
        log_price = float(self.model.predict(frame)[0])
        known_location = locality in self.locality_coordinates
        return Prediction(max(0, float(np.expm1(log_price))), "high" if known_location else "medium", latitude, longitude, locality)


model_service: ModelService | None = None


def get_model_service() -> ModelService:
    global model_service
    if model_service is None:
        model_service = ModelService()
    return model_service
