"""Build a candidate model after the feedback queue reaches the configured threshold."""
import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from housevalue.database import PriceFeedback, RetrainingJob, SessionLocal  # noqa: E402
from housevalue.model_service import HUBS, get_model_service, haversine_km  # noqa: E402


def feature_row(payload, price, service):
    locality, latitude, longitude = service._resolve_location(payload["location"], payload.get("latitude"), payload.get("longitude"))
    row = {"price": price, "area": payload["area"], "locality": locality, "property_type": payload["property_type"], "bedroom_num": payload["bhk"], "bathroom_num": payload["bathrooms"], "furnished": payload.get("furnished", "Unfurnished"), "total_floors": payload.get("total_floors", 1), "new_latitude": latitude, "new_longitude": longitude, "new_pincode": payload["pincode"]}
    return row


def prepare_features(data, service):
    data = data.dropna(subset=["price", "area", "locality", "new_latitude", "new_longitude"]).copy()
    data = data[data.price > 0]
    data["pincode_target_encoded"] = data.new_pincode.astype(str).map(service.pincode_mean).fillna(service.global_log_price)
    data["micro_market_cluster"] = service.kmeans.predict(data[["new_latitude", "new_longitude"]])
    for hub, (lat, lon) in HUBS.items():
        data[f"distance_to_{hub}_km"] = [haversine_km(row.new_latitude, row.new_longitude, lat, lon) for row in data.itertuples()]
    features = ["area", "locality", "property_type", "bedroom_num", "bathroom_num", "furnished", "total_floors", "new_latitude", "new_longitude", "pincode_target_encoded", "micro_market_cluster", *[f"distance_to_{name}_km" for name in HUBS]]
    for column in ["locality", "property_type", "furnished", "micro_market_cluster"]:
        data[column] = data[column].astype("category")
    return data[features], np.log1p(data.price)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum-r2", type=float, default=0.50)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        job = db.scalar(select(RetrainingJob).where(RetrainingJob.status == "pending").order_by(RetrainingJob.created_at))
        if not job:
            print("No pending retraining job."); return
        feedback = db.scalars(select(PriceFeedback).where(PriceFeedback.verified.is_(True))).all()
        service = get_model_service()
        feedback_rows = [feature_row(json.loads(item.property_payload), item.actual_price, service) for item in feedback]
        base = pd.read_csv(Path(__file__).resolve().parents[2] / "Data/cleaned_data.csv")
        combined = pd.concat([base, pd.DataFrame(feedback_rows)], ignore_index=True, sort=False)
        X, y = prepare_features(combined, service)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LGBMRegressor(n_estimators=2000, learning_rate=0.03, num_leaves=31, random_state=42)
        model.fit(X_train, y_train, categorical_feature=["locality", "property_type", "furnished", "micro_market_cluster"])
        score = r2_score(np.expm1(y_test), np.expm1(model.predict(X_test)))
        if score < args.minimum_r2:
            job.status = "failed"; db.commit(); raise SystemExit(f"Candidate R2 {score:.4f} below {args.minimum_r2:.4f}")
        output = Path(__file__).resolve().parents[2] / "Data/models/lightgbm-candidate.pkl"
        joblib.dump(model, output)
        job.status = "candidate_ready"; db.commit()
        print(f"Candidate saved to {output} with R2={score:.4f}. Track it with DVC before promotion.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
