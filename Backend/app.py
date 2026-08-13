from flask import Flask

from config import Config
from extensions import db, bcrypt, jwt, cors
from routes.auth import auth_bp
from routes.predict import predict_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # allow React dev server

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)

    # Create DB tables if they don't exist yet
    with app.app_context():
        db.create_all()

    @app.route("/")
    def health_check():
        return {"status": "ok", "message": "House Price Prediction API is running."}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
