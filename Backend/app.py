import os

from flask import Flask

from config import Config
from database import initialize_database
from extensions import bcrypt, jwt, cors
from routes.auth import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # allow React dev server
   
    app.register_blueprint(auth_bp)

    app.config["MYSQL_INITIALIZATION_ERROR"] = initialize_database()

    @app.route("/")
    def health_check():
        database_ready = not app.config["MYSQL_INITIALIZATION_ERROR"]
        return {
            "status": "ok" if database_ready else "degraded",
            "database": "connected" if database_ready else "unavailable",
            "message": "House Price Prediction API is running.",
        }

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True,
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", "5000")),
    )
