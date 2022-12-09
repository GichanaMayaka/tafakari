from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
sess = Session()
login_manager = LoginManager()
jwt = JWTManager()
