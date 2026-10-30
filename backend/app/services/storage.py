import io
import os
import uuid
from flask import send_file, send_from_directory
from werkzeug.utils import secure_filename
from ..config import Config


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_file(file):
    """Stores the upload (Google Cloud Storage if GCS_BUCKET is set, else local disk). Returns storage key."""
    key = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    if Config.GCS_BUCKET:
        from google.cloud import storage
        storage.Client().bucket(Config.GCS_BUCKET).blob(key).upload_from_file(file.stream, content_type=file.mimetype)
    else:
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        file.save(os.path.join(Config.UPLOAD_DIR, key))
    return key


def send_stored(key):
    if Config.GCS_BUCKET:
        from google.cloud import storage
        data = storage.Client().bucket(Config.GCS_BUCKET).blob(key).download_as_bytes()
        return send_file(io.BytesIO(data), download_name=key.split("_", 1)[-1], as_attachment=True)
    return send_from_directory(Config.UPLOAD_DIR, key, as_attachment=True, download_name=key.split("_", 1)[-1])
