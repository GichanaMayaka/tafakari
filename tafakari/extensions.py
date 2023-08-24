from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()
cache = Cache()
cors = CORS()
