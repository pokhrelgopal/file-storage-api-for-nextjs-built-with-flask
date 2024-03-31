from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_FOLDER = os.path.join(os.getcwd(), "media")
MEDIA = os.path.join("media", "uploads")

app = Flask(__name__)


@app.route("/media/<path:filename>")
def media_files(filename):
    return send_from_directory(MEDIA_FOLDER, filename)


app.secret_key = "my_secret_key_123"
app.config["UPLOAD_FOLDER"] = MEDIA
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@db:5432/image_db"
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes

with app.app_context():
    db.create_all()
