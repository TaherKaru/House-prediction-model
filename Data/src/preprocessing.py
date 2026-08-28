import pandas as pd
import numpy as np


def target_encode_oof(
    train_series,
    test_series,
    y_train,
    n_splits=5,
    smoothing=20,
    random_state=42
):
    """
    Leakage-safe target encoding.

    Training:
        Uses out-of-fold encoding so a row's own target
        does not directly determine its encoded value.

    Testing:
        Uses mapping learned from the complete training set.
    """

    from sklearn.model_selection import KFold

    train_series = train_series.reset_index(drop=True)
    test_series = test_series.reset_index(drop=True)
    y_train = pd.Series(y_train).reset_index(drop=True)

    global_mean = y_train.mean()

    oof_encoded = pd.Series(index=train_series.index, dtype=float)

    kfold = KFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=random_state
    )

    for train_idx, valid_idx in kfold.split(train_series):

        fold_data = pd.DataFrame({
            "category": train_series.iloc[train_idx],
            "target": y_train.iloc[train_idx]
        })

        stats = fold_data.groupby("category")["target"].agg(
            ["mean", "count"]
        )

        # Smoothed mean
        stats["encoded"] = (
            (stats["mean"] * stats["count"] +
             global_mean * smoothing)
            /
            (stats["count"] + smoothing)
        )

        mapping = stats["encoded"]

        oof_encoded.iloc[valid_idx] = (
            train_series.iloc[valid_idx]
            .map(mapping)
            .fillna(global_mean)
            .values
        )

    # Mapping using ALL training data for test set
    full_data = pd.DataFrame({
        "category": train_series,
        "target": y_train
    })

    stats = full_data.groupby("category")["target"].agg(
        ["mean", "count"]
    )

    stats["encoded"] = (
        (stats["mean"] * stats["count"] +
         global_mean * smoothing)
        /
        (stats["count"] + smoothing)
    )

    test_encoded = (
        test_series
        .map(stats["encoded"])
        .fillna(global_mean)
    )

    return (
        oof_encoded,
        test_encoded
    )


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points
    in kilometers.
    """

    R = 6371.0  # Earth radius in km

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


MUMBAI_HUBS = {
    "airport": (19.0896, 72.8656),
    "bkc": (19.0653, 72.8697),
    "csmt": (18.9402, 72.8356),
    "andheri_station": (19.1197, 72.8468),
    "thane_station": (19.1860, 72.9756)
}


def add_distance_features(df):
    df = df.copy()

    for hub_name, (hub_lat, hub_lon) in MUMBAI_HUBS.items():

        df[f"distance_to_{hub_name}_km"] = haversine_distance(
            df["new_latitude"],
            df["new_longitude"],
            hub_lat,
            hub_lon
        )

    return df


def build_preprocessor(categorical_features):
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ],
        remainder="passthrough"
    )
