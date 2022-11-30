from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return {
               "message": "Welcome to tafakari"
           }, 200
