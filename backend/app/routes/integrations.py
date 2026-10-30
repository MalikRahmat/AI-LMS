from flask import Blueprint, request, jsonify
from ..utils import role_required
from ..services import integrations as svc

bp = Blueprint("integrations", __name__, url_prefix="/api/integrations")


@bp.get("/moodle/courses")
@role_required()
def moodle():
    try:
        return jsonify(courses=svc.moodle_courses())
    except Exception as e:
        return jsonify(error=str(e)), 502


@bp.get("/coursera/search")
@role_required()
def coursera():
    q = (request.args.get("q") or "").strip()
    if not q:
        return jsonify(error="Enter a search term"), 400
    try:
        return jsonify(courses=svc.coursera_search(q))
    except Exception as e:
        return jsonify(error=f"Coursera lookup failed: {e}"), 502
