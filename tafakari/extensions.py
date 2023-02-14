from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_session import Session

bcrypt = Bcrypt()
sess = Session()
jwt = JWTManager()
