import os
from datetime import timedelta


class Config:
    # General
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT (login tokens)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)   # normal login
    JWT_REMEMBER_ME_EXPIRES = timedelta(days=30)    # "Remember me" checked
