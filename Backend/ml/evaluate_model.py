"""Evaluate the packaged model on a deterministic sample for CI regression checks."""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from housevalue.model_service import get_model_service  # noqa: E402
from housevalue.schemas import PredictionRequest  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum-r2", type=float, default=0.50)
    args = parser.parse_args()
    data = pd.read_csv(Path(__file__).resolve().parents[2] / "Data/cleaned_data.csv")
    sample = data.dropna(subset=["price", "locality", "area", "bedroom_num", "bathroom_num", "property_type", "new_pincode"]).query("price > 0")
    sample = sample[sample.property_type.isin(["Apartment", "Villa", "Independent House"])].sample(n=min(500, len(data)), random_state=42)
    service = get_model_service()
    predicted, actual = [], []
    for row in sample.itertuples():
        request = PredictionRequest(location=str(row.locality), bhk=max(1, int(row.bedroom_num)), bathrooms=max(1, int(row.bathroom_num)), area=float(row.area), property_type=str(row.property_type), pincode=str(int(row.new_pincode)), furnished=str(row.furnished) if str(row.furnished) in {"Unfurnished", "Semi-Furnished", "Furnished"} else "Unfurnished", total_floors=max(1, int(row.total_floors)))
        predicted.append(service.predict(request).estimated_price)
        actual.append(float(row.price))
    score = r2_score(actual, predicted)
    print(f"R2={score:.4f}")
    if score < args.minimum_r2:
        raise SystemExit(f"R2 {score:.4f} is below the minimum {args.minimum_r2:.4f}")


if __name__ == "__main__":
    main()
