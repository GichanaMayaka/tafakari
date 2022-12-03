from flask import Blueprint

authentications = Blueprint(
    name="auth",
    url_prefix="auth"
)

authentications.route("/", methods=["GET"])


def auth() -> None:
    pass
