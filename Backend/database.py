import re

import mysql.connector
from mysql.connector import Error

from config import Config


class DatabaseConnectionError(Exception):
    """Raised when the configured MySQL server cannot be reached."""


def _connection_options(include_database=True):
    options = {
        "host": Config.MYSQL_HOST,
        "port": Config.MYSQL_PORT,
        "user": Config.MYSQL_USER,
        "password": Config.MYSQL_PASSWORD,
    }
    if include_database:
        options["database"] = Config.MYSQL_DATABASE
    return options


def get_db_connection():
    try:
        return mysql.connector.connect(**_connection_options())
    except Error as exc:
        raise DatabaseConnectionError from exc


def initialize_database():
    """Create the configured MySQL database and its users table if needed."""
    database_name = Config.MYSQL_DATABASE
    if not re.fullmatch(r"[A-Za-z0-9_]+", database_name):
        return "MYSQL_DATABASE may contain only letters, numbers, and underscores."

    server_connection = database_connection = None
    server_cursor = database_cursor = None
    try:
        server_connection = mysql.connector.connect(**_connection_options(False))
        server_cursor = server_connection.cursor()
        server_cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database_name}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )

        database_connection = mysql.connector.connect(**_connection_options())
        database_cursor = database_connection.cursor()
        database_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
        database_connection.commit()
        return None
    except Error as exc:
        return str(exc)
    finally:
        if database_cursor:
            database_cursor.close()
        if database_connection and database_connection.is_connected():
            database_connection.close()
        if server_cursor:
            server_cursor.close()
        if server_connection and server_connection.is_connected():
            server_connection.close()
