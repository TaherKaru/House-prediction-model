# HouseValue architecture

```mermaid
flowchart LR
    U[Homeowner] --> F[React HouseValue UI]
    F -->|JWT-authenticated request| A[FastAPI API]
    A --> AUTH[SQLite locally / PostgreSQL in deployment]
    A --> FE[Feature builder]
    FE --> M[LightGBM + KMeans model artefacts]
    FE --> OSM[OpenStreetMap / Overpass 2 km amenities]
    OSM --> A
    W[Walk Score API, optional key] --> A
    A --> F
    F -->|Actual price feedback| A
    A --> Q[Verified feedback + retraining queue]
    Q --> R[Candidate model training worker]
    R --> DVC[DVC-tracked data and model versions]
    DVC --> M
    G[GitHub Actions] --> T[API tests, R² guardrail, UI build]
```

Live amenity signals are collected for each prediction response. They are deliberately isolated from `lightgbm-mumbai-v1` until verified feedback supports retraining a model that includes those features.
