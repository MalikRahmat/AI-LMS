import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + os.path.join(BASE_DIR, "instance", "local.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB uploads
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "mp4", "mp3", "txt", "md", "docx", "pptx", "csv"}

    UPLOAD_DIR = os.path.join(BASE_DIR, "instance", "uploads")
    MODEL_DIR = os.path.join(BASE_DIR, "instance", "models")
    GCS_BUCKET = os.getenv("GCS_BUCKET", "")

    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

    USE_TENSORFLOW = os.getenv("USE_TENSORFLOW", "false").lower() == "true"
    MOODLE_URL = os.getenv("MOODLE_URL", "").rstrip("/")
    MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "")
