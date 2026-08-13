"""
Example script to train a house price prediction model and save it
as model.pkl for the Flask backend to use.

Replace 'housing_data.csv' with your actual dataset.
Expected columns: area, bedrooms, bathrooms, location, price

Run this once (or whenever you retrain) from the backend/ml folder:
    python train_model.py
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib

# 1. Load data
df = pd.read_csv("housing_data.csv")

X = df[["area", "bedrooms", "bathrooms", "location"]]
y = df["price"]

# 2. Preprocessing: one-hot encode 'location', pass numeric columns through
preprocessor = ColumnTransformer(
    transformers=[
        ("location", OneHotEncoder(handle_unknown="ignore"), ["location"]),
    ],
    remainder="passthrough",
)

# 3. Full pipeline: preprocessing + model, saved together
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=200, random_state=42)),
])

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model.fit(X_train, y_train)

# 5. Evaluate
preds = model.predict(X_test)
print("R2 score:", r2_score(y_test, preds))
print("MAE:", mean_absolute_error(y_test, preds))

# 6. Save model (pipeline includes preprocessing, so predict_utils.py
#    can pass raw feature values directly)
joblib.dump(model, "model.pkl")
print("Model saved to model.pkl")
