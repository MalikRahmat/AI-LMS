from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import QuizAttempt, STYLES
from ..utils import role_required, current_user
from ..ml.analytics import weakness_report, overall_stats
from ..services.recommender import recommend_resources, study_plan

bp = Blueprint("student", __name__, url_prefix="/api/student")


@bp.get("/dashboard")
@role_required("student")
def dashboard():
    user = current_user()
    report = weakness_report(user.id)
    attempts = (QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.created_at.desc()).limit(10).all())
    return jsonify(
        user=user.to_dict(), stats=overall_stats(user.id), topics=report,
        recommendations=recommend_resources(user, report), study_plan=study_plan(user, report),
        history=[{"id": a.id, "score": a.score, "total": a.total, "date": a.created_at.isoformat()} for a in reversed(attempts)])


@bp.patch("/profile")
@role_required("student", "teacher", "admin")
def profile():
    d = request.get_json(silent=True) or {}
    user = current_user()
    if d.get("learning_style") in STYLES:
        user.learning_style = d["learning_style"]
    if (d.get("name") or "").strip():
        user.name = d["name"].strip()
    db.session.commit()
    return jsonify(user=user.to_dict())
