from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Shared extension instances — imported by app.py and route files
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
