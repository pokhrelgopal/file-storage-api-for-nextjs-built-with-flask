from flask import request, jsonify, json, render_template
from .cipher import generate_random_string
from werkzeug.utils import secure_filename
from app.models import Image
from app import app, db
import os

BASE_URL = "http://127.0.0.1:8000"
UPLOAD_FOLDER = os.path.join("media", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "mp4", "avi", "mov", "mkv"}
ALLOWED_SIZE = 100 * 1024 * 1024


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_size():
    content_length = request.content_length
    if content_length is None:
        return False
    return content_length <= ALLOWED_SIZE


@app.route("/file", methods=["POST"])
def save_image():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if not allowed_size():
        return jsonify({"message": "File too large. Less than 200MB allowed"}), 400

    if file and allowed_file(file.filename):
        key = generate_random_string()
        fname = secure_filename(file.filename)
        filename = f"{key}_{fname}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        complete_image_url = f"{BASE_URL}/media/uploads/{filename}"
        image = Image(image_url=complete_image_url)
        db.session.add(image)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Image saved successfully",
                    "image_url": complete_image_url,
                }
            ),
            201,
        )
    else:
        return jsonify({"message": "Invalid file type or file not allowed"}), 400


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")
