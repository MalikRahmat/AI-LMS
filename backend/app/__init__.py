import os
from flask import Flask, jsonify, send_from_directory
from .config import Config
from .extensions import db, jwt, cors


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    os.makedirs(os.path.join(Config.UPLOAD_DIR), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(Config.UPLOAD_DIR)), exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    from .routes import register_blueprints
    register_blueprints(app)
    from .cli import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify(error="File is too large (max 25 MB)"), 413

    # Serve the built React app (used in Docker / Cloud Run)
    dist = os.path.abspath(os.path.join(app.root_path, "..", "..", "frontend", "dist"))
    if os.path.isdir(dist):
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def spa(path):
            if path.startswith("api/"):
                return jsonify(error="Not found"), 404
            full = os.path.join(dist, path)
            if path and os.path.isfile(full):
                return send_from_directory(dist, path)
            return send_from_directory(dist, "index.html")

    return app
