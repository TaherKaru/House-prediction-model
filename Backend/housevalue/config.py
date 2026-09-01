import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'housevalue.db'}")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-secret-change-before-production-32-bytes")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", PROJECT_DIR / "Data/models/lightgbm.pkl"))
KMEANS_PATH = Path(os.getenv("KMEANS_PATH", PROJECT_DIR / "Data/models/kmeans.pkl"))
DATASET_PATH = Path(os.getenv("DATASET_PATH", PROJECT_DIR / "Data/cleaned_data.csv"))
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()]
OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
WALKSCORE_API_KEY = os.getenv("WALKSCORE_API_KEY", "")
RETRAINING_THRESHOLD = int(os.getenv("RETRAINING_THRESHOLD", "1000"))
