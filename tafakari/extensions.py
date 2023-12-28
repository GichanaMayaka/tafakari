from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

from tafakari.configs import configs

bcrypt = Bcrypt()
jwt = JWTManager()
cache = Cache()
cors = CORS()
migrations = Migrate()
limiter = Limiter(
    get_remote_address,
    storage_uri=f"redis://{configs.REDIS_HOSTNAME}:{configs.REDIS_PORT}",
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",
    default_limits=["200 per day", "50 per hour"],
)
