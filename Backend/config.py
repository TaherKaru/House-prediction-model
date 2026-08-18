import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    # General
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    # MySQL. Put real credentials in Backend/.env, not source control.
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "havenly")

    # JWT (login tokens)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)   # normal login
    JWT_REMEMBER_ME_EXPIRES = timedelta(days=30)    # "Remember me" checked
