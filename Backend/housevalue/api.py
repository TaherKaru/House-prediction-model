import json
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import ALLOWED_ORIGINS, RETRAINING_THRESHOLD
from .database import PriceFeedback, RetrainingJob, User, get_db, initialize_database
from .enrichment import fetch_neighbourhood_signals
from .model_service import get_model_service
from .schemas import AuthResponse, FeedbackRequest, LoginRequest, PredictionRequest, SignUpRequest, UserResponse
from .security import create_access_token, decode_access_token, hash_password, verify_password

bearer_scheme = HTTPBearer()


def serialise_user(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email}


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    user = db.get(User, decode_access_token(credentials.credentials))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session user no longer exists.")
    return user


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    # Load the artefacts before requests are accepted, avoiding a slow first valuation.
    get_model_service()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="HouseValue API", version="2.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

    @app.get("/", tags=["health"])
    def health_check():
        try:
            service = get_model_service()
            return {"status": "ok", "model": type(service.model).__name__, "message": "HouseValue FastAPI is running."}
        except FileNotFoundError as exc:
            return {"status": "degraded", "message": str(exc)}

    @app.post("/api/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, tags=["auth"])
    def signup(payload: SignUpRequest, db: Session = Depends(get_db)):
        email = str(payload.email).lower()
        if db.scalar(select(User).where(User.email == email)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
        user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Account created successfully.", "access_token": create_access_token(user.id), "user": serialise_user(user)}

    @app.post("/api/auth/login", response_model=AuthResponse, tags=["auth"])
    def login(payload: LoginRequest, db: Session = Depends(get_db)):
        user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        return {"message": "Logged in successfully.", "access_token": create_access_token(user.id), "user": serialise_user(user)}

    @app.get("/api/auth/me", response_model=UserResponse, tags=["auth"])
    def me(user: User = Depends(current_user)):
        return serialise_user(user)

    @app.post("/api/predict", tags=["valuation"])
    async def predict(payload: PredictionRequest, _: User = Depends(current_user)):
        valuation = get_model_service().predict(payload)
        return {"prediction_id": str(uuid4()), "estimated_price": round(valuation.estimated_price, 2), "currency": "INR", "confidence": valuation.confidence, "locality": valuation.locality_resolved, "coordinates": {"latitude": valuation.latitude, "longitude": valuation.longitude}, "neighbourhood_signals": {"source": "loading"}, "model_version": "lightgbm-mumbai-v1", "note": "Neighbourhood signals load separately so the price estimate is returned immediately."}

    @app.get("/api/enrichment", tags=["valuation"])
    async def enrichment(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180), _: User = Depends(current_user)):
        return (await fetch_neighbourhood_signals(latitude, longitude)).as_dict()

    @app.post("/api/feedback", status_code=status.HTTP_201_CREATED, tags=["feedback"])
    def submit_feedback(payload: FeedbackRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
        feedback = PriceFeedback(user_id=user.id, prediction_id=payload.prediction_id, actual_price=payload.actual_price, verified=payload.verified, property_payload=json.dumps(payload.property_payload))
        db.add(feedback)
        db.commit()
        verified_count = db.scalar(select(func.count(PriceFeedback.id)).where(PriceFeedback.verified.is_(True))) or 0
        job_created = False
        if verified_count >= RETRAINING_THRESHOLD and not db.scalar(select(RetrainingJob).where(RetrainingJob.status == "pending")):
            db.add(RetrainingJob(status="pending", feedback_count=verified_count))
            db.commit()
            job_created = True
        return {"message": "Actual price feedback saved.", "verified_feedback_count": verified_count, "retraining_queued": job_created}

    return app
